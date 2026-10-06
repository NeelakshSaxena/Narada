from dataclasses import dataclass, field
from typing import List, Dict, Optional
import uuid

@dataclass
class Task:
    name: str
    description: str
    status: str = "pending" # pending, in_progress, completed, blocked
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

@dataclass
class Goal:
    name: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    status: str = "pending"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def update_status(self):
        if not self.tasks:
            return
        if all(t.status == "completed" for t in self.tasks):
            self.status = "completed"
        elif any(t.status == "in_progress" for t in self.tasks):
            self.status = "in_progress"

@dataclass
class Responsibility:
    name: str
    description: str
    goals: List[Goal] = field(default_factory=list)
    status: str = "active"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def update_status(self):
        if not self.goals:
            return
        for g in self.goals:
            g.update_status()
        if all(g.status == "completed" for g in self.goals):
            self.status = "completed"
        elif any(g.status == "in_progress" for g in self.goals):
            self.status = "active"

@dataclass
class Project:
    name: str
    description: str
    responsibilities: List[Responsibility] = field(default_factory=list)
    status: str = "active"
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def update_status(self):
        if not self.responsibilities:
            return
        for r in self.responsibilities:
            r.update_status()
        if all(r.status == "completed" for r in self.responsibilities):
            self.status = "completed"
            
    def get_structured_state(self) -> dict:
        self.update_status()
        return {
            "project_name": self.name,
            "status": self.status,
            "responsibilities": [
                {
                    "name": r.name,
                    "status": r.status,
                    "goals": [
                        {
                            "name": g.name,
                            "status": g.status,
                            "tasks": [
                                {"name": t.name, "status": t.status} for t in g.tasks
                            ]
                        } for g in r.goals
                    ]
                } for r in self.responsibilities
            ]
        }
