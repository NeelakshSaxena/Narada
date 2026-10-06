from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align

class MascotWidget(Static):
    """
    Placeholder for the Mascot.
    Will be replaced with actual images later.
    """
    
    current_state = reactive("idle")

    def set_state(self, new_state: str) -> None:
        """Update the mascot's state."""
        self.current_state = new_state

    def render(self) -> Align:
        # A simple, clean placeholder without fake ASCII art.
        text = Text("[ MASCOT AREA ]\n\n", style="bold #d4af37")
        text.append(f"State: {self.current_state}", style="dim #4a6fa5")
        text.justify = "center"
        return Align.center(text, vertical="middle")
