from fastapi import APIRouter
from app.models.job import JobRequest

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/evaluate")
async def evaluate_job(request: JobRequest):

    return {
        "allow": True,
        "reason": "job approved",
        "partition": request.partition,
    }