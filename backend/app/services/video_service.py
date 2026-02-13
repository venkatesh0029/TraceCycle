"""
Main video processing pipeline
Coordinates detection, tracking, and event detection
Refactored from ai_engine/video_processor.py
"""
import cv2
import numpy as np
from typing import Optional, Callable, Dict
import time
import logging
from datetime import datetime

from .detection_service import DetectionService
from .tracking_service import TrackingService
from .event_service import EventService

logger = logging.getLogger(__name__)


class VideoService:
    """
    Main video processing pipeline for shelf monitoring
    """
    
    def __init__(self,
                 video_source: str,
                 yolo_model: str = "yolov8n.pt", # Reverted to default
                 conf_threshold: float = 0.5,
                 shelf_regions: Optional[Dict] = None,
                 frame_skip: int = 2):
        """
        Initialize video processor
        
        Args:
            video_source: Video file path or camera index (0 for webcam)
            yolo_model: Path to YOLO model
            conf_threshold: Detection confidence threshold
            shelf_regions: Dict of shelf_id -> (x1, y1, x2, y2) regions
            frame_skip: Process every Nth frame
        """
        self.video_source = video_source
        self.frame_skip = frame_skip
        self.frame_count = 0
        self.running = False
        self.synthetic_mode = False
        
        # Initialize components
        self.detector = DetectionService(yolo_model, conf_threshold)
        self.tracker = TrackingService(max_age=30, min_hits=3, iou_threshold=0.3)
        
        # Default shelf regions if not provided
        if shelf_regions is None:
            # Use entire frame as a single "Display Area" to capture all events
            # This ensures analytics work even without specific shelf boxes
            shelf_regions = {
                'display_area': (0, 0, 640, 480)
            }
        
        self.event_detector = EventService(shelf_regions)
        
        # Video capture
        self.cap = None
        self.fps = 0
        self.frame_width = 0
        self.frame_height = 0
        
        # Statistics
        self.stats = {
            'frames_processed': 0,
            'detections_count': 0,
            'events_count': 0,
            'avg_fps': 0,
            'start_time': None
        }
        
        self.callbacks = []
        self.latest_result = None
        self.thread = None
    
    def start(self):
        """Start video capture and processing thread"""
        if self.running:
            logger.info("Video processor already running")
            return

        try:
            self.synthetic_mode = False
            
            # Setup video source (same as before)
            if self.video_source == "synthetic":
                self.synthetic_mode = True
            else:
                if self.video_source.isdigit():
                    self.cap = cv2.VideoCapture(int(self.video_source), cv2.CAP_DSHOW)
                else:
                    self.cap = cv2.VideoCapture(self.video_source)
                
                if not self.cap or not self.cap.isOpened():
                    logger.warning(f"Failed to open video source: {self.video_source}. Falling back to SYNTHETIC mode.")
                    self.synthetic_mode = True
                else:
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.cap.set(cv2.CAP_PROP_FPS, 15)

            if self.synthetic_mode:
                self.frame_width = 1280
                self.frame_height = 720
                self.fps = 30.0
            else:
                self.fps = self.cap.get(cv2.CAP_PROP_FPS)
                self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"Video source opened: {self.frame_width}x{self.frame_height} @ {self.fps} FPS")
            
            self.running = True
            self.stats['start_time'] = time.time()
            
            # Start processing thread
            import threading
            self.thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.thread.start()
            
        except Exception as e:
            logger.error(f"Failed to start video processor: {e}")
            raise
    
    def stop(self):
        """Stop video capture"""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=2.0)
        
        if self.cap:
            self.cap.release()
        logger.info("Video processor stopped")

    def _generate_synthetic_frame(self):
        """Generate a demo frame for testing when no camera is available"""
        # Create black background
        frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
        
        # Draw some "shelves"
        # Shelf A
        cv2.rectangle(frame, (100, 200), (500, 600), (50, 50, 50), 2)
        cv2.putText(frame, "Shelf A", (100, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        # Shelf B
        cv2.rectangle(frame, (600, 200), (1000, 600), (50, 50, 50), 2)
        cv2.putText(frame, "Shelf B", (600, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        # Simulate a moving object (product)
        t = time.time()
        x = int(600 + 400 * abs(np.sin(t / 2))) # Move back and forth
        y = 400
        
        # Draw "Product"
        cv2.circle(frame, (x, y), 30, (0, 0, 255), -1) # Red ball
        cv2.putText(frame, "Demo Item", (x-40, y-40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add timestamp
        cv2.putText(frame, f"SYNTHETIC DEMO MODE - {datetime.now().strftime('%H:%M:%S')}", 
                   (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                   
        return frame
    
    def process_frame(self, frame: np.ndarray, visualize: bool = True) -> Dict:
        """
        Process a single frame
        
        Args:
            frame: Input frame
            visualize: Whether to draw visualizations
            
        Returns:
            Dict with processed results
        """
        start_time = time.time()
        
        detections = []
        tracked_objects = []
        events = []
        shelf_counts = {}
        
        if not self.synthetic_mode:
            # Detect objects
            detections = self.detector.detect(frame)
            self.stats['detections_count'] += len(detections)
            
            # Track objects
            tracked_objects = self.tracker.update_tracks(detections)
            
            # Detect events
            events = self.event_detector.update(tracked_objects)
            self.stats['events_count'] += len(events)
            
            # Get shelf counts
            shelf_counts = self.event_detector.get_shelf_counts()
        else:
            # Mock detections for the demo
            pass

        # Visualize if requested
        annotated_frame = frame.copy() if visualize else None
        if visualize:
            if not self.synthetic_mode:
                annotated_frame = self._draw_visualizations(
                    annotated_frame, tracked_objects, events, shelf_counts
                )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        result = {
            'frame': annotated_frame if visualize else frame,
            'detections': detections,
            'tracked_objects': tracked_objects,
            'events': events,
            'shelf_counts': shelf_counts,
            'processing_time': processing_time,
            'frame_number': self.frame_count,
            'timestamp': datetime.now().isoformat()
        }
        
        self.stats['frames_processed'] += 1
        
        return result

    def add_callback(self, callback: Callable):
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def remove_callback(self, callback: Callable):
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def _processing_loop(self):
        """Main processing loop running in separate thread"""
        logger.info("Starting processing loop thread")
        frame_times = []
        
        while self.running:
            try:
                if self.synthetic_mode:
                    frame = self._generate_synthetic_frame()
                    time.sleep(1/15) # Limit to ~15 FPS in synthetic too
                    ret = True
                else:
                    ret, frame = self.cap.read()
                    if ret and frame is not None:
                        if frame.shape[1] > 640:
                            scale = 640 / frame.shape[1]
                            new_height = int(frame.shape[0] * scale)
                            frame = cv2.resize(frame, (640, new_height))
                
                if not ret:
                    logger.warning("Failed to read frame")
                    time.sleep(1)
                    continue
                
                self.frame_count += 1
                if self.frame_count % self.frame_skip != 0:
                    continue

                # Process frame
                result = self.process_frame(frame, visualize=True)
                
                # Update latest result (Thread safe assignment)
                self.latest_result = result
                
                # Calculate FPS
                frame_times.append(result['processing_time'])
                if len(frame_times) > 30:
                    frame_times.pop(0)
                avg_time = sum(frame_times) / len(frame_times)
                self.stats['avg_fps'] = 1.0 / avg_time if avg_time > 0 else 0

                # Notify callbacks
                for cb in self.callbacks:
                    try:
                        cb(result)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")
                        
            except Exception as e:
                logger.error(f"Error in processing loop: {e}")
                time.sleep(1)
                
        logger.info("Processing loop finished")

    
    def _draw_visualizations(self, frame, tracked_objects, events, shelf_counts):
        """Draw bounding boxes, IDs, and shelf regions"""
        
        # Draw shelf regions
        for shelf_id, (x1, y1, x2, y2) in self.event_detector.shelf_regions.items():
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            count = shelf_counts.get(shelf_id, 0)
            label = f"{shelf_id}: {count} items"

            # Ensure label is visible
            text_y = y1 - 10 if y1 > 20 else y1 + 20

            cv2.putText(frame, label, (x1, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Draw tracked objects
        for obj in tracked_objects:
            x1, y1, x2, y2 = obj['bbox']
            track_id = obj['track_id']
            conf = obj['confidence']
            
            # Color based on category
            color = (0, 255, 0)  # Green for tracked
            
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label = f"ID:{track_id} {obj['class_name']} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Draw recent events
        y_offset = 60
        for event in events[-5:]:  # Show last 5 events
            event_text = f"{event['event_type'].upper()}: Track {event.get('track_id', '?')}"
            cv2.putText(frame, event_text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            y_offset += 30
        
        return frame
    
    def read_frame(self):
        """Read the next frame (synthetic or real)"""
        # ... (restored simple version)
        if self.synthetic_mode:
            time.sleep(1/30) # Simulate 30 FPS
            return True, self._generate_synthetic_frame()
        else:
            if self.cap:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    if frame.shape[1] > 640:
                        scale = 640 / frame.shape[1]
                        new_height = int(frame.shape[0] * scale)
                        frame = cv2.resize(frame, (640, new_height))
                    return True, frame
                return False, None
            return False, None

    def get_stats(self) -> Dict:
        """Get processing statistics"""
        if self.stats['start_time']:
            runtime = time.time() - self.stats['start_time']
            self.stats['runtime_seconds'] = runtime
        return self.stats.copy()
