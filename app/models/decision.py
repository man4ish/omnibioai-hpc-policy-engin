from pydantic import BaseModel


class Decision(BaseModel):
    allow: bool
    reason: str

    remaining_cpu_hours: float = 0
    remaining_gpu_hours: float = 0