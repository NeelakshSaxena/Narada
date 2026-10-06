import pytest
from unittest.mock import patch, MagicMock
import argparse
import sys
from scripts.narada import start_server, chat_repl, main

def test_start_server():
    with patch("uvicorn.run") as mock_run:
        start_server("127.0.0.1", 9000)
        mock_run.assert_called_once_with("apps.api.main:app", host="127.0.0.1", port=9000)

import asyncio

def test_chat_repl_exit():
    with patch("builtins.input", return_value="exit"):
        # Should exit immediately without making HTTP calls
        asyncio.run(chat_repl())

def test_chat_repl_chat():
    with patch("builtins.input", side_effect=["Hello", "exit"]):
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Hi there"}}]
            }
            mock_post.return_value = mock_response
            
            with patch("builtins.print") as mock_print:
                asyncio.run(chat_repl())
                mock_post.assert_called_once()
                mock_print.assert_any_call("Narada> Hi there")

def test_main_cli_start():
    test_args = ["narada", "start", "--host", "127.0.0.1", "--port", "9999"]
    with patch.object(sys, 'argv', test_args):
        with patch("scripts.narada.start_server") as mock_start:
            main()
            mock_start.assert_called_once_with("127.0.0.1", 9999)

def test_main_cli_chat():
    test_args = ["narada", "chat"]
    with patch.object(sys, 'argv', test_args):
        with patch("asyncio.run") as mock_run:
            main()
            mock_run.assert_called_once()
