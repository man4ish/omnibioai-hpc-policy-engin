import pytest
from unittest.mock import MagicMock
from app.services.quota_service import QuotaService
from app.models.decision import Decision
from app.models.quota import QuotaCheck


def _usage(cpu_hours=0.0, gpu_hours=0.0):
    u = MagicMock()
    u.cpu_hours = cpu_hours
    u.gpu_hours = gpu_hours
    return u


def _request(gpus=0, partition="cpu", cpu_hours=1.0, gpu_hours=0.0):
    r = MagicMock()
    r.gpus = gpus
    r.partition = partition
    r.cpu_hours = cpu_hours
    r.gpu_hours = gpu_hours
    return r


# ---------------------------------------------------------------------------
# GPU access validation
# ---------------------------------------------------------------------------

def test_no_gpu_needed_always_passes():
    decision = QuotaService.evaluate(
        usage=_usage(),
        request=_request(gpus=0),
        roles=["researcher"],
    )
    assert decision.allow is True


def test_gpu_request_denied_without_gpu_user_role():
    decision = QuotaService.evaluate(
        usage=_usage(),
        request=_request(gpus=2),
        roles=["researcher"],
    )
    assert decision.allow is False
    assert "gpu" in decision.reason.lower()


def test_gpu_request_allowed_with_gpu_user_role():
    decision = QuotaService.evaluate(
        usage=_usage(),
        request=_request(gpus=2, gpu_hours=1.0),
        roles=["researcher", "gpu_user"],
    )
    assert decision.allow is True


# ---------------------------------------------------------------------------
# Partition access validation
# ---------------------------------------------------------------------------

def test_dgx_a100_denied_without_dgx_access():
    decision = QuotaService.evaluate(
        usage=_usage(),
        request=_request(partition="dgx-a100"),
        roles=["researcher", "gpu_user"],
    )
    assert decision.allow is False
    assert "dgx" in decision.reason.lower()


def test_dgx_a100_allowed_with_dgx_access():
    decision = QuotaService.evaluate(
        usage=_usage(),
        request=_request(gpus=0, partition="dgx-a100"),
        roles=["researcher", "gpu_user", "dgx_access"],
    )
    assert decision.allow is True


def test_standard_partition_requires_no_special_role():
    decision = QuotaService.evaluate(
        usage=_usage(),
        request=_request(partition="cpu"),
        roles=[],
    )
    assert decision.allow is True


# ---------------------------------------------------------------------------
# Quota enforcement
# ---------------------------------------------------------------------------

def test_cpu_quota_exceeded_denied():
    decision = QuotaService.evaluate(
        usage=_usage(cpu_hours=119.0),  # 1 hour remaining
        request=_request(cpu_hours=2.0),  # requesting 2
        roles=[],
    )
    assert decision.allow is False
    assert "cpu" in decision.reason.lower()


def test_gpu_quota_exceeded_denied():
    decision = QuotaService.evaluate(
        usage=_usage(gpu_hours=23.5),  # 0.5 hours remaining
        request=_request(gpus=1, gpu_hours=1.0, partition="cpu"),
        roles=["gpu_user"],
    )
    assert decision.allow is False
    assert "gpu" in decision.reason.lower()


def test_quota_ok_within_limits():
    decision = QuotaService.evaluate(
        usage=_usage(cpu_hours=10.0, gpu_hours=5.0),
        request=_request(gpus=1, cpu_hours=5.0, gpu_hours=1.0),
        roles=["gpu_user"],
    )
    assert decision.allow is True
    assert decision.reason == "quota ok"


def test_decision_includes_remaining_hours():
    # evaluate_quota returns (limit - current_used), not (limit - used - requested)
    decision = QuotaService.evaluate(
        usage=_usage(cpu_hours=20.0, gpu_hours=4.0),
        request=_request(cpu_hours=10.0, gpu_hours=2.0),
        roles=[],
    )
    assert decision.allow is True
    assert decision.remaining_cpu_hours == 100.0  # 120 - 20
    assert decision.remaining_gpu_hours == 20.0   # 24 - 4


def test_zero_request_always_passes():
    decision = QuotaService.evaluate(
        usage=_usage(cpu_hours=0.0, gpu_hours=0.0),
        request=_request(cpu_hours=0.0, gpu_hours=0.0),
        roles=[],
    )
    assert decision.allow is True
