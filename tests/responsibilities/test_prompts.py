import pytest
from core.responsibilities.project import Project, Responsibility, Goal, Task
from core.responsibilities.prompts import ProjectStatusPrompt

def test_project_status_prompt():
    t1 = Task(name="Design schema", description="DB layout", status="completed")
    t2 = Task(name="Implement API", description="FastAPI", status="in_progress")
    t3 = Task(name="Write tests", description="Pytest", status="pending")
    t4 = Task(name="Deploy", description="AWS", status="blocked")
    
    g1 = Goal(name="Backend", description="The backend", tasks=[t1, t2, t3])
    g2 = Goal(name="Ops", description="The infra", tasks=[t4])
    
    r1 = Responsibility(name="Engineering", description="Eng", goals=[g1, g2])
    
    p1 = Project(name="Project X", description="Top secret", responsibilities=[r1])
    
    prompt = ProjectStatusPrompt.generate(p1)
    
    assert "Summarize project state for: Project X" in prompt
    assert "Responsibility: Engineering [active]" in prompt
    assert "Goal: Backend [in_progress]" in prompt
    assert "Goal: Ops [pending]" in prompt
    assert "Task: Design schema [completed]" in prompt
    assert "Task: Implement API [in_progress]" in prompt
    assert "Task: Deploy [blocked]" in prompt
    assert "Do not infer completion" in prompt
