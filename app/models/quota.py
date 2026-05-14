from pydantic import BaseModel


class QuotaCheck(BaseModel):
    user_id: str

    cpu_hours: float = 0
    gpu_hours: float = 0

    gpus: int = 0