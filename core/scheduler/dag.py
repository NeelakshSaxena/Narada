from typing import List, Dict, Set

class TaskNode:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.dependencies: Set[str] = set()

    def add_dependency(self, parent_id: str):
        self.dependencies.add(parent_id)

class TaskGraph:
    def __init__(self):
        self.nodes: Dict[str, TaskNode] = {}

    def add_task(self, task_id: str):
        if task_id not in self.nodes:
            self.nodes[task_id] = TaskNode(task_id)

    def add_dependency(self, task_id: str, depends_on: str):
        self.add_task(task_id)
        self.add_task(depends_on)
        self.nodes[task_id].add_dependency(depends_on)

    def get_execution_order(self) -> List[str]:
        """
        Returns a topological sort of task_ids.
        Raises ValueError if a cycle is detected.
        """
        visited = set()
        temp_mark = set()
        order = []

        def visit(n: str):
            if n in temp_mark:
                raise ValueError("Cycle detected in task graph")
            if n not in visited:
                temp_mark.add(n)
                for dep in self.nodes[n].dependencies:
                    visit(dep)
                temp_mark.remove(n)
                visited.add(n)
                order.append(n)

        for node_id in self.nodes:
            if node_id not in visited:
                visit(node_id)

        return order
