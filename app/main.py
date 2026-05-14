from fastapi import FastAPI

from app.db.session import Base, engine

from app.api.routes_policy import router as policy_router
from app.api.routes_quota import router as quota_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="OmniBioAI HPC Policy Engine",
)

app.include_router(policy_router)
app.include_router(quota_router)


@app.get("/")
async def root():
    return {
        "service": "omnibioai-hpc-policy-engine",
        "status": "running",
    }