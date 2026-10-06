from typing import List, Dict
from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text

# Define the mascot frames for each state.
# We keep them subtle, geometric, and cute (navy/black, warm gold/orange accents can be done via rich styles).
# The prompt calls for a non-human, geometric, cute, curious digital creature.

MASCOT_FRAMES: Dict[str, List[str]] = {
    "idle": [
        """
      ( \\/ )      
     (o   o)     
    ╭~ ◡ ~╮    
   ( (  -  ) )   
    ╰─────╯    
        """,
        """
      ( \\/ )      
     (o   o)     
    ╭~ ◡ ~╮    
   ( (  ~  ) )   
    ╰─────╯    
        """,
    ],
    "thinking": [
        """
      ( /\\ )      
     (o   o)     
    ╭~ ◡ ~╮    
   ( (  ?  ) )   
    ╰─────╯    
        """,
        """
      ( /\\ )      
     (o   o)     
    ╭~ ◡ ~╮    
   ( ( ... ) )   
    ╰─────╯    
        """,
    ],
    "searching": [
        """
      ( <> )      
     (>   <)     
    ╭~ ◡ ~╮    
  *( (  ⌕  ) )*  
    ╰─────╯    
        """,
        """
      ( <> )      
     (<   >)     
    ╭~ ◡ ~╮    
 * ( (  ⌕  ) ) * 
    ╰─────╯    
        """,
    ],
    "working": [
        """
      ( >< )      
     (o   o)     
    ╭~ - ~╮    
  *( ( ⚙ ) )*  
    ╰─────╯    
        """,
        """
      ( >< )      
     (o   o)     
    ╭~ - ~╮    
 * ( ( ⚙ ) ) * 
    ╰─────╯    
        """,
    ],
    "success": [
        """
      ( \\/ )      
     (^   ^)     
    ╭~ ◡ ~╮    
  ✧( (  ★  ) )✧  
    ╰─────╯    
        """,
        """
      ( \\/ )      
     (^   ^)     
    ╭~ ◡ ~╮    
   ( (  ★  ) )   
    ╰─────╯    
        """,
    ],
    "error": [
        """
      ( /\\ )      
     (x   x)     
    ╭~ ◠ ~╮    
   ( (  !  ) )   
    ╰─────╯    
        """,
        """
      ( /\\ )      
     (x   x)     
    ╭~ ◠ ~╮    
   ( (  ?  ) )   
    ╰─────╯    
        """
    ],
    "sleeping": [
        """
      ( -- )      
     (-   -)     
    ╭~ ◡ ~╮    
   ( (  z  ) )   
    ╰─────╯    
        """,
        """
      ( -- )      
     (-   -)     
    ╭~ ◡ ~╮    
   ( (  Z  ) )   
    ╰─────╯    
        """
    ]
}

class MascotWidget(Static):
    """A terminal-native representation of the mascot."""
    
    current_state = reactive("idle")
    frame_index = reactive(0)

    def on_mount(self) -> None:
        # Subtle animation tick
        self.update_timer = self.set_interval(0.8, self.tick)

    def set_state(self, state: str) -> None:
        """Set the mascot to a new state."""
        if state not in MASCOT_FRAMES:
            state = "idle"
        
        if self.current_state != state:
            self.current_state = state
            self.frame_index = 0

    def tick(self) -> None:
        frames = MASCOT_FRAMES.get(self.current_state, MASCOT_FRAMES["idle"])
        self.frame_index = (self.frame_index + 1) % len(frames)
        self.refresh(layout=True)

    def render(self) -> Text:
        frames = MASCOT_FRAMES.get(self.current_state, MASCOT_FRAMES["idle"])
        # Ensure we don't go out of bounds if state changed abruptly
        idx = self.frame_index if self.frame_index < len(frames) else 0
        raw_text = frames[idx]
        
        # Style the mascot text (navy blue base, gold accents for symbols)
        t = Text(raw_text, style="bold color(24)")
        t.highlight_regex(r"[\*\✧\★\⚙\⌕\?]", "bold color(214)") # Gold accents
        return t
