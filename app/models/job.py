from pydantic import BaseModel


class JobRequest(BaseModel):
    user_id: str

    cpu_hours: float = 0
    gpu_hours: float = 0

    gpus: int = 0
    memory_gb: int = 0

    partition: str = "cpu"