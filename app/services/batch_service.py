"""
Batch processing service
"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class BatchService:
    """Service for handling batch operations"""
    
    def __init__(self):
        self.batch_dir = Path("data/batches")
        self.batch_dir.mkdir(parents=True, exist_ok=True)
        self.active_batches: Dict[str, Dict] = {}
    
    def create_batch(self, requests: List[Dict], batch_name: str = "batch_job") -> str:
        """Create a new batch job"""
        batch_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        batch_info = {
            "batch_id": batch_id,
            "batch_name": batch_name,
            "status": "created",
            "created_at": timestamp,
            "total_requests": len(requests),
            "completed_requests": 0,
            "requests": requests,
            "results": []
        }
        
        # Save to file
        batch_file = self.batch_dir / f"{batch_id}.json"
        with open(batch_file, 'w') as f:
            json.dump(batch_info, f, indent=2)
        
        self.active_batches[batch_id] = batch_info
        logger.info(f"Created batch {batch_id} with {len(requests)} requests")
        
        return batch_id
    
    def get_batch_status(self, batch_id: str) -> Optional[Dict]:
        """Get batch status"""
        if batch_id in self.active_batches:
            return self.active_batches[batch_id]
        
        # Try to load from file
        batch_file = self.batch_dir / f"{batch_id}.json"
        if batch_file.exists():
            with open(batch_file, 'r') as f:
                return json.load(f)
        
        return None
    
    def list_batches(self) -> List[Dict]:
        """List all batches"""
        batches = []
        
        # Get from active batches
        for batch_info in self.active_batches.values():
            batches.append({
                "batch_id": batch_info["batch_id"],
                "batch_name": batch_info["batch_name"],
                "status": batch_info["status"],
                "created_at": batch_info["created_at"],
                "total_requests": batch_info["total_requests"],
                "completed_requests": batch_info["completed_requests"]
            })
        
        # Get from files (if not in active)
        for batch_file in self.batch_dir.glob("*.json"):
            batch_id = batch_file.stem
            if batch_id not in self.active_batches:
                try:
                    with open(batch_file, 'r') as f:
                        batch_info = json.load(f)
                        batches.append({
                            "batch_id": batch_info["batch_id"],
                            "batch_name": batch_info["batch_name"],
                            "status": batch_info["status"],
                            "created_at": batch_info["created_at"],
                            "total_requests": batch_info["total_requests"],
                            "completed_requests": batch_info["completed_requests"]
                        })
                except Exception as e:
                    logger.error(f"Error loading batch {batch_id}: {e}")
        
        return batches
    
    def get_batch_results(self, batch_id: str) -> Optional[str]:
        """Get batch results file path"""
        batch_file = self.batch_dir / f"{batch_id}.json"
        if batch_file.exists():
            return str(batch_file)
        return None

# Global batch service instance
batch_service = BatchService()
