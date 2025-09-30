"""
Batch processing endpoints
"""

from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from ..services.batch_service import batch_service
from ..models import BatchGenerateRequest, BatchResponse

router = APIRouter(prefix="/batch")

@router.post("/generate", response_model=BatchResponse)
async def create_batch_generate(request: BatchGenerateRequest):
    """Create a batch generation job"""
    # Convert requests to dict format
    requests_data = [req.dict() for req in request.requests]
    
    batch_id = batch_service.create_batch(requests_data, request.batch_name)
    
    batch_info = batch_service.get_batch_status(batch_id)
    
    return BatchResponse(
        batch_id=batch_id,
        status=batch_info["status"],
        created_at=batch_info["created_at"],
        total_requests=batch_info["total_requests"]
    )

@router.get("/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of a batch job"""
    batch_info = batch_service.get_batch_status(batch_id)
    
    if not batch_info:
        raise HTTPException(status_code=404, detail="Batch not found")
    
    return {
        "batch_id": batch_info["batch_id"],
        "status": batch_info["status"],
        "created_at": batch_info["created_at"],
        "total_requests": batch_info["total_requests"],
        "completed_requests": batch_info["completed_requests"],
        "progress_percentage": (batch_info["completed_requests"] / batch_info["total_requests"]) * 100
    }

@router.get("/download/{batch_id}")
async def download_batch_results(batch_id: str):
    """Download batch results as JSON file"""
    results_file = batch_service.get_batch_results(batch_id)
    
    if not results_file:
        raise HTTPException(status_code=404, detail="Batch results not found")
    
    return FileResponse(
        results_file,
        media_type="application/json",
        filename=f"batch_{batch_id}_results.json"
    )

@router.get("/list")
async def list_batches():
    """List all batch jobs"""
    return {"batches": batch_service.list_batches()}
