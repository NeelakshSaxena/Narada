import pytest
from core.scheduler.dag import TaskGraph

def test_task_graph_linear():
    graph = TaskGraph()
    # A -> B -> C (C depends on B, B depends on A)
    graph.add_dependency("C", "B")
    graph.add_dependency("B", "A")
    
    order = graph.get_execution_order()
    assert order == ["A", "B", "C"]

def test_task_graph_branching():
    graph = TaskGraph()
    # A -> B
    # A -> C
    # B -> D
    # C -> D
    graph.add_dependency("B", "A")
    graph.add_dependency("C", "A")
    graph.add_dependency("D", "B")
    graph.add_dependency("D", "C")
    
    order = graph.get_execution_order()
    assert order[0] == "A"
    assert "B" in order[1:3]
    assert "C" in order[1:3]
    assert order[-1] == "D"

def test_task_graph_cycle():
    graph = TaskGraph()
    # A -> B -> C -> A
    graph.add_dependency("B", "A")
    graph.add_dependency("C", "B")
    graph.add_dependency("A", "C")
    
    with pytest.raises(ValueError, match="Cycle detected"):
        graph.get_execution_order()
