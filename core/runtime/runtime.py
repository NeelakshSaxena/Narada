class AgentRuntime:
    """
    AgentRuntime: Manages execution, planning, and state.
    Stubbed for Phase 1.
    """
    def __init__(self):
        self.is_running = False
        
    def execute_task(self, task):
        pass

class NaradaCore:
    def __init__(self):
        self.agent = AgentRuntime()
        self.is_running = True
        
    def get_status(self):
        return {"status": "ok", "running": self.is_running}
