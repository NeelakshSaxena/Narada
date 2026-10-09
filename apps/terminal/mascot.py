from textual.widgets import Static
from textual.reactive import reactive
from rich.text import Text
from rich.align import Align

YEL = "\033[38;2;255;184;40m"   # Gold / Trim
BLU = "\033[38;2;61;90;128m"    # Brightened Robe (was 25;28;45)
SKN = "\033[38;2;255;232;196m"  # Chibi Face Skin
EYE = "\033[38;2;40;25;18m"     # Eye Brown/Black
ORG = "\033[38;2;255;110;30m"   # Orb / Glow Orange
RST = "\033[0m"

SPRITES = {
"IDLE": f"""
              {YEL}·       ✦{RST}
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}◉ ◉  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}ᴗ        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"HELLO": f"""
              {YEL}✦{RST}
          {BLU}╭───────╮       ╭{SKN}─{BLU}╮{RST}
       {BLU}╭──╯  {SKN}◉ ◉  {BLU}╰──╮   ╱{YEL}Hi│{RST}
      {BLU}╱       {SKN}◡        {BLU}╲ ╰──╯{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲     ╱{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰   {BLU}╱{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱  {YEL}👋{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"LISTENING": f"""
          {YEL}♫       ·{RST}
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}◉ ◉  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}ᴗ        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"THINKING": f"""
             {YEL}·   ·{RST}
          {BLU}╭───────╮    {YEL}?{RST}
       {BLU}╭──╯  {SKN}◉ ◉  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}─        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"CURIOUS": f"""
              {YEL}?{RST}
          {BLU}╭───────╮   {YEL}◦{RST}
       {BLU}╭──╯  {SKN}◉  ◉ {BLU}╰──╮{RST}
      {BLU}╱       {SKN}O        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰   {YEL}◇{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"HAPPY": f"""
          {YEL}✦         ✦{RST}
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}^ ^  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}◡        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰   {YEL}✦{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"EXPLAINING": f"""
          {BLU}╭───────╮        {YEL}→{RST}
       {BLU}╭──╯  {SKN}◉ ◉  {BLU}╰──╮    {YEL}·{RST}
      {BLU}╱       {SKN}◡        {BLU}╲  {YEL}→{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"PLAYFUL": f"""
             {YEL}✦{RST}
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}◕ ◕  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}ᴗ        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲  {YEL}♪{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱  {YEL}✦{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"SERIOUS": f"""
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}▪ ▪  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}─        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"SEARCHING": f"""
       {YEL}◦      ◇      ◦{RST}
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}◉ {YEL}→  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}ᴗ        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲    {YEL}◇{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"USING TOOLS": f"""
             {YEL}⚙       ◇{RST}
          {BLU}╭───────╮   {YEL}┌{BLU}─{YEL}┐{RST}
       {BLU}╭──╯  {SKN}◉ ◉  {BLU}╰──╮{YEL}│⌘│{RST}
      {BLU}╱       {SKN}◡        {BLU}╲{YEL}└{BLU}─{YEL}┘{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲     {YEL}◫{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"READING": f"""
          {BLU}╭───────╮     ╱{YEL}▱{BLU}╲{RST}
       {BLU}╭──╯  {SKN}◉ ◉  {BLU}╰──╮ {YEL}▱▱{RST}
      {BLU}╱       {SKN}ᴗ        {BLU}╲╲{YEL}▱{BLU}╱{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"SURPRISED": f"""
              {YEL}!{RST}
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}O O  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}o        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"CONFUSED": f"""
           {YEL}?       ?{RST}
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}◔ ◕  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}︶        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"CONCERNED": f"""
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}◕ ◕  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}︵        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰    {YEL}!{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"ERROR": f"""
             {YEL}✕{RST}
          {BLU}╭───────╮    {YEL}▪{RST}
       {BLU}╭──╯  {SKN}◕ ◕  {BLU}╰──╮ {YEL}▪{RST}
      {BLU}╱       {SKN}︵        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲    {YEL}✕{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"SUCCESS": f"""
       {YEL}✦              ✦{RST}
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}^ ^  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}◡        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯  {YEL}✓{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰   {YEL}✦{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
""",

"SLEEPING": f"""
          {BLU}╭───────╮{RST}
       {BLU}╭──╯  {SKN}- -  {BLU}╰──╮{RST}
      {BLU}╱       {SKN}ᴗ        {BLU}╲{RST}
     {BLU}╱   ╲──────────╱   ╲{RST}
    {BLU}╰──────╲╱╲╱╲╱───────╯{RST}
          {BLU}╱  ╲╱  ╲{RST}
      {ORG}〰{BLU}──╯    ╰──{ORG}〰    {YEL}z{RST}
         {BLU}╲  ╭{SKN}─{BLU}╮  ╱   {YEL}z Z{RST}
          {BLU}╰{SKN}─{BLU}╯ ╰{SKN}─{BLU}╯{RST}
"""
}

class MascotWidget(Static):
    """
    ASCII Mascot for Nārada terminal.
    """
    
    current_state = reactive("idle")

    def set_state(self, new_state: str) -> None:
        """Update the mascot's state."""
        self.current_state = new_state

    def render(self) -> Align:
        # Map our internal states to the provided sprites
        state_map = {
            "hello": "HELLO",
            "idle": "IDLE",
            "thinking": "THINKING",
            "searching": "SEARCHING",
            "working": "USING TOOLS",
            "success": "SUCCESS",
            "error": "ERROR",
            "sleeping": "SLEEPING"
        }
        
        sprite_key = state_map.get(self.current_state, "IDLE")
        raw_ansi = SPRITES.get(sprite_key, SPRITES["IDLE"])
        
        # Remove empty first/last lines for a cleaner bounding box
        lines = [line for line in raw_ansi.split('\n') if line.strip()]
        clean_ansi = "\n".join(lines)
        
        # Textual/Rich can parse ANSI color codes natively
        text = Text.from_ansi(clean_ansi)
        text.justify = "center"
        return Align.center(text, vertical="middle")
