import asyncio
import json
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv
import cv2
import threading
import time
import logging
from datetime import datetime
from contextlib import asynccontextmanager

# Services
from app.services.video_service import VideoService
from app.database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Iterate over a copy to avoid modification during iteration issues
        for connection in self.active_connections[:]:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()
loop = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def process_video_result(result):
    """Callback to handle video processing results"""
    if result.get('events'):
        # Only broadcast if there are events
        try:
            # Broadcast via WebSocket
            message = json.dumps({
                "type": "event",
                "events": result['events'], # List of event dicts
                "timestamp": result['timestamp']
            }, default=str)
            
            if loop and loop.is_running():
                asyncio.run_coroutine_threadsafe(manager.broadcast(message), loop)
            
            # Persist to MongoDB
            if db.db is not None:
                # Add timestamp object for better querying
                current_time = datetime.fromisoformat(result['timestamp'])
                for event in result['events']:
                    event_doc = {
                        **event,
                        "timestamp": current_time,
                        "processed_at": datetime.utcnow()
                    }
                    db.db.events.insert_one(event_doc)

        except Exception as e:
            logger.error(f"Error processing/saving event: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global loop
    loop = asyncio.get_running_loop()
    
    # Startup
    db.connect()
    
    # Register callback
    video_service.add_callback(process_video_result)
    
    if video_service.video_source != "synthetic":
        try:
             video_service.start()
        except:
             pass
    yield
    # Shutdown
    db.close()
    video_service.remove_callback(process_video_result)
    video_service.stop()

    video_service.stop()

app = FastAPI(
    title="TraceCycle API",
    description="Backend for Waste Traceability System with Blockchain Integration",
    version="1.0.0",
    lifespan=lifespan
)

from app.api import analytics
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Video Service Instance
# Default to camera (index 0). VideoService handles fallback to synthetic if camera fails.
video_service = VideoService(video_source="0", frame_skip=2)

@app.get("/")
async def read_root():
    return {
        "message": "Welcome to TraceCycle API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/video/start")
async def start_video(source: str = "0"):
    """
    Start the video processing service
    
    Args:
        source: Video source (default "0" for webcam, or "synthetic" for demo)
    """
    if not video_service.running:
        try:
            # Update source if changed
            if source != video_service.video_source:
                video_service.video_source = source
                
            video_service.start()
            return {"status": "started", "mode": "synthetic" if video_service.synthetic_mode else "camera"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "already_running", "mode": "synthetic" if video_service.synthetic_mode else "camera"}

@app.post("/video/stop")
async def stop_video():
    """Stop the video processing service"""
    if video_service.running:
        video_service.stop()
        return {"status": "stopped"}
    return {"status": "not_running"}

def generate_frames():
    """Generator for MJPEG stream"""
    while True:
        if video_service.running and video_service.latest_result:
            frame = video_service.latest_result['frame']
            if frame is not None:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            else:
                time.sleep(0.01)
        else:
            time.sleep(0.1)

@app.get("/video/feed")
async def video_feed():
    """MJPEG Video Feed Endpoint"""
    if not video_service.running:
         # Auto-start for convenience if accessed
         video_service.start()
    
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/video/stats")
async def get_video_stats():
    """Get current video processing statistics"""
    return video_service.get_stats()

@app.websocket("/ws/notifications")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, maybe listen for client commands
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
