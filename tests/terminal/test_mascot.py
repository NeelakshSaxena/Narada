import pytest
import asyncio
from apps.terminal.app import NaradaTerminalUI
from apps.terminal.mascot import MascotWidget

def test_mascot_state_changes():
    async def run_test():
        app = NaradaTerminalUI()
        async with app.run_test() as pilot:
            mascot = app.query_one(MascotWidget)
            
            # Initial state should be idle
            assert mascot.current_state == "idle"
            
            # Change state
            mascot.set_state("thinking")
            assert mascot.current_state == "thinking"
            
            # Change state
            mascot.set_state("searching")
            assert mascot.current_state == "searching"
            
            # Invalid state falls back to idle
            mascot.set_state("non_existent_state")
            assert mascot.current_state == "idle"

    asyncio.run(run_test())

def test_terminal_ui_input():
    async def run_test():
        app = NaradaTerminalUI()
        async with app.run_test() as pilot:
            # Check initial state
            assert app.status_panel.status_text == "ONLINE"
            
            # Type something
            await pilot.press("t", "e", "s", "t", "enter")
            
            # State should temporarily transition to thinking/searching
            assert app.mascot.current_state == "searching"
            assert app.status_panel.status_text == "WORKING"

    asyncio.run(run_test())
