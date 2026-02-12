"""
DeepSORT-style object tracker for shelf items
Simplified implementation using Kalman filter and Hungarian algorithm
Refactored from ai_engine/tracker.py
"""
import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class KalmanBoxTracker:
    """
    Kalman Filter for tracking bounding boxes in image space
    """
    count = 0
    
    def __init__(self, bbox):
        """Initialize tracker with initial bounding box"""
        self.id = KalmanBoxTracker.count
        KalmanBoxTracker.count += 1
        
        # State: [x, y, w, h, vx, vy, vw, vh]
        self.x = np.array([bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1], 0, 0, 0, 0])
        self.time_since_update = 0
        self.hits = 1
        self.hit_streak = 1
        self.age = 0
        
        # Simple velocity model
        self.history = []
        
    def update(self, bbox):
        """Update tracker with new detection"""
        self.time_since_update = 0
        self.hits += 1
        self.hit_streak += 1
        
        # Update state with new measurement
        self.x[0] = bbox[0]
        self.x[1] = bbox[1]
        self.x[2] = bbox[2] - bbox[0]
        self.x[3] = bbox[3] - bbox[1]
        
        self.history.append(self.get_state())
    
    def predict(self):
        """Predict next state"""
        self.age += 1
        self.time_since_update += 1
        
        # Simple motion model: assume constant velocity
        if len(self.history) > 1:
            prev = np.array(self.history[-1])
            self.x[0] += self.x[4]  # x + vx
            self.x[1] += self.x[5]  # y + vy
            self.x[2] += self.x[6]  # w + vw
            self.x[3] += self.x[7]  # h + vh
        
        self.hit_streak = 0
        return self.get_state()
    
    def get_state(self):
        """Return current bounding box [x1, y1, x2, y2]"""
        x, y, w, h = self.x[0], self.x[1], self.x[2], self.x[3]
        return [x, y, x + w, y + h]


class TrackingService:
    """
    Multi-object tracker using DeepSORT approach
    """
    
    def __init__(self, max_age: int = 30, min_hits: int = 3, iou_threshold: float = 0.3):
        """
        Initialize tracker
        
        Args:
            max_age: Maximum frames to keep alive a track without matches
            min_hits: Minimum hits before track is confirmed
            iou_threshold: Minimum IOU for matching
        """
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.trackers = []
        self.frame_count = 0
        
    def update_tracks(self, detections: List[Dict]) -> List[Dict]:
        """
        Update tracker with new detections
        
        Args:
            detections: List of detection dicts with 'bbox' key
            
        Returns:
            List of tracked objects with 'track_id' added
        """
        self.frame_count += 1
        
        # Predict new locations of existing trackers
        for tracker in self.trackers:
            tracker.predict()
        
        # Extract bounding boxes from detections
        det_bboxes = [det['bbox'] for det in detections]
        
        # Match detections to trackers
        matched, unmatched_dets, unmatched_trks = self._match_detections_to_trackers(
            det_bboxes, self.trackers
        )
        
        # Update matched trackers with assigned detections
        for det_idx, trk_idx in matched:
            self.trackers[trk_idx].update(det_bboxes[det_idx])
        
        # Create new trackers for unmatched detections
        for det_idx in unmatched_dets:
            tracker = KalmanBoxTracker(det_bboxes[det_idx])
            self.trackers.append(tracker)
        
        # Remove dead trackers
        self.trackers = [t for t in self.trackers 
                        if t.time_since_update < self.max_age]
        
        # Build output
        tracked_objects = []
        for i, tracker in enumerate(self.trackers):
            # Only return confirmed tracks
            if tracker.hits >= self.min_hits or self.frame_count <= self.min_hits:
                # Find matching detection
                for det_idx, trk_idx in matched:
                    if trk_idx == i:
                        obj = detections[det_idx].copy()
                        obj['track_id'] = tracker.id
                        obj['track_age'] = tracker.age
                        obj['hits'] = tracker.hits
                        tracked_objects.append(obj)
                        break
        
        return tracked_objects
    
    def _match_detections_to_trackers(self, detections: List, trackers: List):
        """
        Match detections to trackers using Hungarian algorithm
        
        Returns:
            matched: List of (det_idx, trk_idx) pairs
            unmatched_dets: List of unmatched detection indices
            unmatched_trks: List of unmatched tracker indices
        """
        if len(trackers) == 0:
            return [], list(range(len(detections))), []
        
        # Compute IOU matrix
        iou_matrix = np.zeros((len(detections), len(trackers)))
        for d, det in enumerate(detections):
            for t, trk in enumerate(trackers):
                iou_matrix[d, t] = self._iou(det, trk.get_state())
        
        # Hungarian algorithm for optimal assignment
        if min(iou_matrix.shape) > 0:
            det_indices, trk_indices = linear_sum_assignment(-iou_matrix)
            matches = [[d, t] for d, t in zip(det_indices, trk_indices)]
        else:
            matches = []
        
        # Filter matches by IOU threshold
        matched_indices = []
        unmatched_detections = []
        unmatched_trackers = []
        
        for m in matches:
            if iou_matrix[m[0], m[1]] < self.iou_threshold:
                unmatched_detections.append(m[0])
                unmatched_trackers.append(m[1])
            else:
                matched_indices.append(m)
        
        # Add unmatched detections
        for d in range(len(detections)):
            if d not in [m[0] for m in matched_indices]:
                unmatched_detections.append(d)
        
        # Add unmatched trackers
        for t in range(len(trackers)):
            if t not in [m[1] for m in matched_indices]:
                unmatched_trackers.append(t)
        
        return matched_indices, unmatched_detections, unmatched_trackers
    
    @staticmethod
    def _iou(bbox1, bbox2):
        """
        Calculate Intersection over Union
        
        Args:
            bbox1, bbox2: [x1, y1, x2, y2] format
            
        Returns:
            IOU score
        """
        x1 = max(bbox1[0], bbox2[0])
        y1 = max(bbox1[1], bbox2[1])
        x2 = min(bbox1[2], bbox2[2])
        y2 = min(bbox1[3], bbox2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        
        area1 = (bbox1[2] - bbox1[0]) * (bbox1[3] - bbox1[1])
        area2 = (bbox2[2] - bbox2[0]) * (bbox2[3] - bbox2[1])
        union = area1 + area2 - intersection
        
        return intersection / union if union > 0 else 0
    
    def reset(self):
        """Reset tracker state"""
        self.trackers = []
        self.frame_count = 0
        KalmanBoxTracker.count = 0
