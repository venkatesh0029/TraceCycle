"""
Event detection logic for shelf operations
Detects: pick, return, misplace, missing events
Refactored from ai_engine/event_detector.py
"""
import numpy as np
from typing import List, Dict, Optional, Set
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)


class EventService:
    """
    Detects shelf events based on object tracking
    """
    
    def __init__(self, 
                 shelf_regions: Dict[str, tuple],
                 frame_buffer_size: int = 30):
        """
        Initialize event detector
        
        Args:
            shelf_regions: Dict mapping shelf_id to (x1, y1, x2, y2) region
            frame_buffer_size: Number of frames to buffer for event detection
        """
        self.shelf_regions = shelf_regions
        self.frame_buffer_size = frame_buffer_size
        
        # Track object history
        self.object_history = defaultdict(lambda: deque(maxlen=frame_buffer_size))
        self.shelf_inventory = defaultdict(set)  # shelf_id -> set of track_ids
        self.previous_counts = defaultdict(int)
        self.track_shelf_mapping = {}  # track_id -> shelf_id
        
        # Event thresholds
        self.movement_threshold = 50  # pixels
        self.stationary_frames = 10
        
    def update(self, tracked_objects: List[Dict]) -> List[Dict]:
        """
        Update tracking and detect events
        
        Args:
            tracked_objects: List of tracked objects from tracker
            
        Returns:
            List of detected events
        """
        events = []
        current_frame_objects = {}
        
        # Update object history and detect events
        for obj in tracked_objects:
            track_id = obj['track_id']
            center = obj['center']
            bbox = obj['bbox']
            
            current_frame_objects[track_id] = obj
            
            # Add to history
            self.object_history[track_id].append({
                'center': center,
                'bbox': bbox,
                'timestamp': obj.get('timestamp', None)
            })
            
            # Determine which shelf this object is on
            current_shelf = self._get_shelf_for_position(center)
            previous_shelf = self.track_shelf_mapping.get(track_id)
            
            # Detect pick event (object leaving shelf)
            if previous_shelf and not current_shelf:
                event = {
                    'event_type': 'pick',
                    'track_id': track_id,
                    'shelf_id': previous_shelf,
                    'product_category': obj.get('product_category', 'unknown'),
                    'confidence': obj.get('confidence', 0),
                    'bbox': bbox,
                    'center': center
                }
                events.append(event)
                logger.info(f"Pick event detected: Track {track_id} from shelf {previous_shelf}")
                
                # Remove from shelf inventory
                if track_id in self.shelf_inventory[previous_shelf]:
                    self.shelf_inventory[previous_shelf].remove(track_id)
            
            # Detect return event (object returning to shelf)
            elif not previous_shelf and current_shelf:
                event = {
                    'event_type': 'return',
                    'track_id': track_id,
                    'shelf_id': current_shelf,
                    'product_category': obj.get('product_category', 'unknown'),
                    'confidence': obj.get('confidence', 0),
                    'bbox': bbox,
                    'center': center
                }
                events.append(event)
                logger.info(f"Return event detected: Track {track_id} to shelf {current_shelf}")
                
                # Add to shelf inventory
                self.shelf_inventory[current_shelf].add(track_id)
            
            # Detect misplace event (object moving between shelves)
            elif previous_shelf and current_shelf and previous_shelf != current_shelf:
                event = {
                    'event_type': 'misplace',
                    'track_id': track_id,
                    'from_shelf': previous_shelf,
                    'to_shelf': current_shelf,
                    'product_category': obj.get('product_category', 'unknown'),
                    'confidence': obj.get('confidence', 0),
                    'bbox': bbox,
                    'center': center
                }
                events.append(event)
                logger.info(f"Misplace event: Track {track_id} from {previous_shelf} to {current_shelf}")
                
                # Update shelf inventory
                if track_id in self.shelf_inventory[previous_shelf]:
                    self.shelf_inventory[previous_shelf].remove(track_id)
                self.shelf_inventory[current_shelf].add(track_id)
            
            # Update shelf mapping
            if current_shelf:
                self.track_shelf_mapping[track_id] = current_shelf
                self.shelf_inventory[current_shelf].add(track_id)
        
        # Detect missing objects (tracks that disappeared)
        previous_tracks = set(self.track_shelf_mapping.keys())
        current_tracks = set(current_frame_objects.keys())
        missing_tracks = previous_tracks - current_tracks
        
        for track_id in missing_tracks:
            shelf_id = self.track_shelf_mapping.get(track_id)
            if shelf_id:
                event = {
                    'event_type': 'missing',
                    'track_id': track_id,
                    'shelf_id': shelf_id,
                    'product_category': 'unknown'
                }
                events.append(event)
                logger.info(f"Missing event: Track {track_id} from shelf {shelf_id}")
                
                # Remove from inventory
                if track_id in self.shelf_inventory[shelf_id]:
                    self.shelf_inventory[shelf_id].remove(track_id)
                del self.track_shelf_mapping[track_id]
        
        # Update shelf counts
        for shelf_id in self.shelf_regions.keys():
            current_count = len(self.shelf_inventory[shelf_id])
            previous_count = self.previous_counts[shelf_id]
            
            if current_count != previous_count:
                logger.debug(f"Shelf {shelf_id} count: {previous_count} -> {current_count}")
                self.previous_counts[shelf_id] = current_count
        
        return events
    
    def _get_shelf_for_position(self, center: tuple) -> Optional[str]:
        """
        Determine which shelf a position belongs to
        
        Args:
            center: (x, y) center coordinates
            
        Returns:
            shelf_id or None
        """
        cx, cy = center
        
        for shelf_id, (x1, y1, x2, y2) in self.shelf_regions.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return shelf_id
        
        return None
    
    def get_shelf_counts(self) -> Dict[str, int]:
        """
        Get current object count for each shelf
        
        Returns:
            Dict mapping shelf_id to count
        """
        return {shelf_id: len(objects) 
                for shelf_id, objects in self.shelf_inventory.items()}
    
    def reset(self):
        """Reset event detector state"""
        self.object_history.clear()
        self.shelf_inventory.clear()
        self.previous_counts.clear()
        self.track_shelf_mapping.clear()
