import pytest
from unittest.mock import MagicMock, patch, call
from app.services.usage_service import UsageService


def _make_db(existing_record=None):
    """Build a mock DB session."""
    db = MagicMock()
    query_mock = MagicMock()
    filter_mock = MagicMock()
    filter_mock.first.return_value = existing_record
    query_mock.filter.return_value = filter_mock
    db.query.return_value = query_mock
    return db


# ---------------------------------------------------------------------------
# get_or_create_user_usage
# ---------------------------------------------------------------------------

def test_returns_existing_record_if_found():
    record = MagicMock()
    record.user_id = "u1"
    db = _make_db(existing_record=record)

    result = UsageService.get_or_create_user_usage(db, "u1")

    assert result is record
    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_creates_new_record_if_not_found():
    db = _make_db(existing_record=None)

    result = UsageService.get_or_create_user_usage(db, "new-user")

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()


def test_new_record_has_zero_usage():
    captured = []

    def capture_add(record):
        captured.append(record)

    db = _make_db(existing_record=None)
    db.add.side_effect = capture_add

    UsageService.get_or_create_user_usage(db, "u2")

    assert len(captured) == 1
    rec = captured[0]
    assert rec.user_id == "u2"
    assert rec.cpu_hours == 0
    assert rec.gpu_hours == 0
    assert rec.jobs_running == 0


def test_returns_refreshed_record_for_new_user():
    db = _make_db(existing_record=None)
    refreshed = MagicMock()
    db.refresh.side_effect = lambda r: setattr(r, "_refreshed", True)

    result = UsageService.get_or_create_user_usage(db, "u3")

    db.refresh.assert_called_once_with(result)


def test_queries_correct_user_id():
    from app.db.models import UsageRecord
    record = MagicMock()
    db = _make_db(existing_record=record)

    UsageService.get_or_create_user_usage(db, "target-user")

    db.query.assert_called_once_with(UsageRecord)
