import pytest
from core.responsibilities.project import Project, Responsibility, Goal, Task

def test_project_hierarchy_status():
    t1 = Task(name="Setup DB", description="Init Postgres")
    t2 = Task(name="Write API", description="FastAPI endpoints")
    
    g1 = Goal(name="Backend Foundation", description="Core backend", tasks=[t1, t2])
    
    r1 = Responsibility(name="Backend Dev", description="Own backend", goals=[g1])
    
    p1 = Project(name="Narada v2", description="The next gen", responsibilities=[r1])
    
    # Initially active/pending
    p1.update_status()
    assert p1.status == "active"
    assert g1.status == "pending"
    
    # Update a task
    t1.status = "completed"
    t2.status = "in_progress"
    p1.update_status()
    assert g1.status == "in_progress"
    
    # Complete all
    t2.status = "completed"
    p1.update_status()
    assert g1.status == "completed"
    assert r1.status == "completed"
    assert p1.status == "completed"

def test_project_structured_state():
    t1 = Task(name="Test Task", description="A test")
    g1 = Goal(name="Test Goal", description="G1", tasks=[t1])
    r1 = Responsibility(name="Test Resp", description="R1", goals=[g1])
    p1 = Project(name="Test Proj", description="P1", responsibilities=[r1])
    
    state = p1.get_structured_state()
    assert state["project_name"] == "Test Proj"
    assert state["status"] == "active"
    assert len(state["responsibilities"]) == 1
    assert state["responsibilities"][0]["goals"][0]["tasks"][0]["name"] == "Test Task"
