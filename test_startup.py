import sys
import os

# Add backend to path
sys.path.append('backend')

try:
    from app.services.video_service import VideoService
    print("VideoService imported")
    vs = VideoService(video_source="0")
    print("VideoService initialized")
    vs.start()
    print("VideoService started")
    vs.stop()
    print("VideoService stopped")
except Exception as e:
    import traceback
    traceback.print_exc()
