class Gateway:
    """
    Nārada Gateway: The always-on boundary between users/events and the internal runtime.
    Stubbed for Phase 1.
    """
    def __init__(self):
        self.active = False
        
    def start(self):
        self.active = True
        
    def stop(self):
        self.active = False
