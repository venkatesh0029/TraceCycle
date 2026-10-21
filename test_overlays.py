import sys
import os
import cv2
import numpy as np

# Add backend to path
sys.path.append('backend')

try:
    from app.services.video_service import VideoService

    # Custom shelf region
    shelf_regions = {
        'test_shelf': (100, 100, 200, 200)
    }

    # Initialize VideoService
    vs = VideoService(video_source="0", shelf_regions=shelf_regions)
    print("VideoService initialized")

    # Create black frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # Process frame with visualization
    result = vs.process_frame(frame, visualize=True)
    annotated_frame = result['frame']

    # Check if pixels in the shelf region rectangle are drawn
    # The rectangle is drawn with color (255, 0, 0) (Blue in BGR)

    # Check if any blue pixel exists in the frame
    # Note: OpenCV uses BGR. So Blue is [255, 0, 0]
    blue_pixels_count = np.sum((annotated_frame[:, :, 0] == 255) &
                               (annotated_frame[:, :, 1] == 0) &
                               (annotated_frame[:, :, 2] == 0))

    if blue_pixels_count > 0:
        print(f"Found {blue_pixels_count} blue pixels - SUCCESS")
    else:
        print("No blue pixels found - FAILURE")
        sys.exit(1)

    print("Test passed!")

except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
