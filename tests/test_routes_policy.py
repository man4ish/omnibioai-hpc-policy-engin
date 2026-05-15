import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes_policy import router


@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


# ---------------------------------------------------------------------------
# POST /jobs/evaluate
# ---------------------------------------------------------------------------

def test_evaluate_job_allow_default(client):
    response = client.post("/jobs/evaluate", json={
        "user_id": "u1",
        "cpu_hours": 4.0,
        "gpu_hours": 0.0,
        "gpus": 0,
        "memory_gb": 16,
        "partition": "cpu",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["allow"] is True
    assert data["reason"] == "job approved"


def test_evaluate_job_returns_partition(client):
    response = client.post("/jobs/evaluate", json={
        "user_id": "u1",
        "partition": "gpu",
    })
    assert response.status_code == 200
    assert response.json()["partition"] == "gpu"


def test_evaluate_job_with_gpu_partition(client):
    response = client.post("/jobs/evaluate", json={
        "user_id": "u2",
        "gpus": 4,
        "gpu_hours": 2.0,
        "partition": "gpu",
    })
    assert response.status_code == 200
    assert response.json()["allow"] is True


def test_evaluate_job_default_partition_is_cpu(client):
    response = client.post("/jobs/evaluate", json={"user_id": "u3"})
    assert response.status_code == 200
    assert response.json()["partition"] == "cpu"


def test_evaluate_job_dgx_partition(client):
    response = client.post("/jobs/evaluate", json={
        "user_id": "u4",
        "partition": "dgx-a100",
        "gpus": 8,
    })
    assert response.status_code == 200
    # The stub always approves — test that response structure is correct
    assert "allow" in response.json()
    assert "reason" in response.json()


def test_evaluate_job_missing_user_id_returns_422(client):
    response = client.post("/jobs/evaluate", json={"cpu_hours": 4.0})
    assert response.status_code == 422
