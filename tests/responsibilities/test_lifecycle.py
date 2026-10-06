import pytest
import asyncio
from datetime import datetime, timedelta
from core.responsibilities.models import Responsibility, ResponsibilityStatus
from core.responsibilities.scheduler import ResponsibilityScheduler
from core.skills.base import SkillRegistry, Skill
from core.tools.registry import ToolRegistry

def test_responsibility_lifecycle():
    resp = Responsibility(schedule_interval_seconds=60)
    assert resp.status == ResponsibilityStatus.DRAFT
    assert resp.is_due() is False # DRAFT is not due
    
    resp.transition_to(ResponsibilityStatus.ACTIVE)
    assert resp.status == ResponsibilityStatus.ACTIVE
    assert resp.is_due() is True
    
    resp.mark_executed(success=False)
    assert resp.status == ResponsibilityStatus.ERROR
    assert resp.is_due() is False
    
    resp.transition_to(ResponsibilityStatus.RECOVERY)
    assert resp.status == ResponsibilityStatus.RECOVERY
    # Time logic might block it, but let's fast forward
    resp.next_run_at = datetime.utcnow() - timedelta(seconds=1)
    assert resp.is_due() is True
    
    resp.mark_executed(success=True)
    assert resp.status == ResponsibilityStatus.ACTIVE
    assert resp.last_success is not None

def test_completed_state_locked():
    resp = Responsibility()
    resp.transition_to(ResponsibilityStatus.COMPLETED)
    with pytest.raises(ValueError):
        resp.transition_to(ResponsibilityStatus.ACTIVE)

def test_terminal_states_locked():
    for state in [ResponsibilityStatus.COMPLETED, ResponsibilityStatus.CANCELLED, ResponsibilityStatus.STOPPED, ResponsibilityStatus.ARCHIVED]:
        resp = Responsibility()
        resp.transition_to(state)
        with pytest.raises(ValueError):
            resp.transition_to(ResponsibilityStatus.ACTIVE)

def test_pause_semantics():
    resp = Responsibility()
    resp.transition_to(ResponsibilityStatus.ACTIVE)
    assert resp.is_due() is True
    
    resp.pause()
    assert resp.status == ResponsibilityStatus.PAUSED
    assert resp.is_due() is False

def test_lifecycle_methods():
    resp = Responsibility()
    resp.cancel()
    assert resp.status == ResponsibilityStatus.CANCELLED

    resp = Responsibility()
    resp.stop()
    assert resp.status == ResponsibilityStatus.STOPPED

    resp = Responsibility()
    resp.disable()
    assert resp.status == ResponsibilityStatus.DISABLED

    resp = Responsibility()
    resp.archive()
    assert resp.status == ResponsibilityStatus.ARCHIVED
