"""
YOLOv8 Object Detector for shelf items
Refactored from ai_engine/detector.py
"""
import cv2
import numpy as np
from ultralytics import YOLO
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class DetectionService:
    """Detects products on shelves using YOLOv8"""
    
    def __init__(self, model_path: str = "yolov8n.pt", conf_threshold: float = 0.5):
        """
        Initialize detector
        
        Args:
            model_path: Path to YOLO model weights
            conf_threshold: Confidence threshold for detections
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.model = None
        self.load_model()
        
        # Map YOLO classes to shelf products
        # In production, train custom model on your products
        self.class_mapping = {
            'bottle': 'beverage',
            'cup': 'cup',
            'bowl': 'bowl',
            'banana': 'fruit',
            'apple': 'fruit',
            'orange': 'fruit',
            'sandwich': 'food',
            'pizza': 'food',
            'cake': 'bakery',
            'book': 'product',  # Generic product
            'cell phone': 'electronics'
        }
    
    def load_model(self):
        """Load YOLO model"""
        try:
            logger.info(f"Loading YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)
            logger.info("YOLO model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[Dict]:
        """
        Detect objects in frame
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of detections with bbox, class, confidence
        """
        if self.model is None:
            logger.error("Model not loaded")
            return []
        
        try:
            # Run inference
            results = self.model(frame, conf=self.conf_threshold, verbose=False)
            
            detections = []
            for result in results:
                boxes = result.boxes
                
                for box in boxes:
                    # Extract box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0].cpu().numpy())
                    cls_id = int(box.cls[0].cpu().numpy())
                    class_name = result.names[cls_id]
                    
                    # Map to product category
                    product_category = self.class_mapping.get(class_name, 'unknown')
                    
                    detection = {
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': conf,
                        'class_id': cls_id,
                        'class_name': class_name,
                        'product_category': product_category,
                        'center': [int((x1 + x2) / 2), int((y1 + y2) / 2)]
                    }
                    detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def detect_and_visualize(self, frame: np.ndarray) -> Tuple[np.ndarray, List[Dict]]:
        """
        Detect objects and draw bounding boxes
        
        Args:
            frame: Input frame
            
        Returns:
            Annotated frame and list of detections
        """
        detections = self.detect(frame)
        annotated_frame = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            label = f"{det['class_name']}: {conf:.2f}"
            
            # Draw bounding box
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated_frame, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
            
            # Draw label text
            cv2.putText(annotated_frame, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return annotated_frame, detections
    
    def get_shelf_region_count(self, detections: List[Dict], 
                               region: Tuple[int, int, int, int]) -> int:
        """
        Count objects in specific shelf region
        
        Args:
            detections: List of detections
            region: (x1, y1, x2, y2) region coordinates
            
        Returns:
            Count of objects in region
        """
        rx1, ry1, rx2, ry2 = region
        count = 0
        
        for det in detections:
            cx, cy = det['center']
            if rx1 <= cx <= rx2 and ry1 <= cy <= ry2:
                count += 1
        
        return count
