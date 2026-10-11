import os
import pytest
import yaml
from core.config.loader import load_config, NaradaConfig
from core.agent.policy import PolicyInjector
from core.runtime.runtime import AgentRuntime, NaradaCore
from providers.llm.fake import FakeLLMProvider
from providers.tools.filesystem import FileSystemReadTool, FileSystemWriteTool
from providers.tools.builtin import builtin_tools


def test_config_workspace_explicit(tmp_path):
    config_file = tmp_path / "config.yaml"
    custom_ws = str(tmp_path / "custom_workspace")
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.safe_dump({"workspace": custom_ws, "llm": {"provider": "ollama", "model": "llama3"}}, f)

    cfg = load_config(str(config_file))
    assert cfg.workspace == os.path.abspath(custom_ws)


def test_config_workspace_env_fallback(tmp_path, monkeypatch):
    custom_ws = str(tmp_path / "env_workspace")
    monkeypatch.setenv("NARADA_WORKSPACE", custom_ws)

    config_file = tmp_path / "config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.safe_dump({"llm": {"provider": "ollama", "model": "llama3"}}, f)

    cfg = load_config(str(config_file))
    assert cfg.workspace == os.path.abspath(custom_ws)


def test_config_workspace_default_cwd(tmp_path, monkeypatch):
    monkeypatch.delenv("NARADA_WORKSPACE", raising=False)
    config_file = tmp_path / "config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.safe_dump({"llm": {"provider": "ollama", "model": "llama3"}}, f)

    cfg = load_config(str(config_file))
    expected = os.path.abspath(os.path.join(os.getcwd(), "workspace")) if os.path.isdir("workspace") else os.path.abspath(os.getcwd())
    assert cfg.workspace == expected


def test_policy_injector_workspace_root(tmp_path):
    ws = tmp_path / "ws"
    ws.mkdir()
    agents_dir = ws / ".agents"
    agents_dir.mkdir()
    (agents_dir / "AGENTS.md").write_text("Rule: Never delete files.", encoding="utf-8")

    injector = PolicyInjector(workspace_root=str(ws))
    assert injector.workspace_root == os.path.abspath(str(ws))
    prompt = injector.inject("Goal: Test")
    assert "Rule: Never delete files." in prompt


@pytest.mark.asyncio
async def test_agent_runtime_workspace_in_prompts(tmp_path):
    ws = str(tmp_path / "my_project")
    fake_provider = FakeLLMProvider(response_text="Done")
    rt = AgentRuntime(fake_provider, user_name="Alice", workspace=ws)

    assert rt.workspace == os.path.abspath(ws)

    # Verify workspace is passed in execute_task base prompt
    captured_prompts = []
    async def capture_generate(prompt, **kwargs):
        captured_prompts.append((prompt, kwargs))
        return await FakeLLMProvider(response_text="Done").generate(prompt, **kwargs)

    rt.provider.generate = capture_generate

    await rt.execute_task("Analyze repository")
    assert len(captured_prompts) == 1
    assert f"Workspace: {rt.workspace}" in captured_prompts[0][0]

    # Verify workspace is injected into interact system prompt
    captured_prompts.clear()
    await rt.interact([{"role": "user", "content": "What is your workspace?"}])
    assert len(captured_prompts) == 1
    messages = captured_prompts[0][1].get("messages", [])
    system_msg = next((m for m in messages if m["role"] == "system"), None)
    assert system_msg is not None
    assert f"Your active workspace path is: {rt.workspace}" in system_msg["content"]


@pytest.mark.asyncio
async def test_narada_core_workspace_and_status(tmp_path):
    ws = str(tmp_path / "core_project")
    fake_provider = FakeLLMProvider(response_text="OK")
    core = NaradaCore(fake_provider, user_name="Bob", workspace=ws)

    assert core.workspace == os.path.abspath(ws)
    assert core.agent.workspace == os.path.abspath(ws)

    status = await core.get_status()
    assert status["workspace"] == os.path.abspath(ws)


@pytest.mark.asyncio
async def test_filesystem_tools_resolve_relative_paths(tmp_path):
    ws = tmp_path / "fs_workspace"
    ws.mkdir()
    test_file = ws / "hello.txt"
    test_file.write_text("Hello from workspace!", encoding="utf-8")

    read_tool = FileSystemReadTool(workspace_root=str(ws))
    # Read relative to workspace
    content = await read_tool.execute(path="hello.txt")
    assert content == "Hello from workspace!"

    # Write relative to workspace
    write_tool = FileSystemWriteTool(workspace_root=str(ws))
    await write_tool.execute(path="nested/output.txt", content="Saved successfully")
    nested_file = ws / "nested" / "output.txt"
    assert nested_file.exists()
    assert nested_file.read_text(encoding="utf-8") == "Saved successfully"


def test_builtin_tools_passes_workspace_root(tmp_path):
    ws = str(tmp_path / "ws_tools")
    tools = builtin_tools(workspace_root=ws)
    fs_read = next((t for t in tools if t.name == "filesystem.read"), None)
    fs_write = next((t for t in tools if t.name == "filesystem.write"), None)
    fs_list = next((t for t in tools if t.name == "filesystem.list"), None)

    assert fs_read is not None
    assert fs_read.workspace_root == os.path.abspath(ws)
    assert fs_write is not None
    assert fs_write.workspace_root == os.path.abspath(ws)
    assert fs_list is not None
    assert fs_list.workspace_root == os.path.abspath(ws)


@pytest.mark.asyncio
async def test_filesystem_tools_enforce_workspace_sandbox(tmp_path):
    ws = tmp_path / "sandbox_ws"
    ws.mkdir()
    outside_file = tmp_path / "secret.txt"
    outside_file.write_text("Secret outside data", encoding="utf-8")

    read_tool = FileSystemReadTool(workspace_root=str(ws))
    write_tool = FileSystemWriteTool(workspace_root=str(ws))

    # Path traversal should raise PermissionError
    with pytest.raises(PermissionError) as exc:
        await read_tool.execute(path="../secret.txt")
    assert "outside the authorized workspace" in str(exc.value)

    # Absolute path outside workspace should raise PermissionError
    with pytest.raises(PermissionError) as exc:
        await read_tool.execute(path=str(outside_file))
    assert "outside the authorized workspace" in str(exc.value)

    # Writing outside workspace should raise PermissionError
    with pytest.raises(PermissionError) as exc:
        await write_tool.execute(path="../hack.txt", content="payload")
    assert "outside the authorized workspace" in str(exc.value)


@pytest.mark.asyncio
async def test_filesystem_categorization_and_list_tool(tmp_path):
    from providers.tools.filesystem import FileSystemListTool
    from core.runtime.runtime import init_workspace_structure

    ws = str(tmp_path / "categorized_ws")
    init_workspace_structure(ws)

    # Check all category directories exist
    categories = ["documents", "code", "data", "outputs", "temp"]
    for cat in categories:
        assert os.path.isdir(os.path.join(ws, cat))

    write_tool = FileSystemWriteTool(workspace_root=ws)
    read_tool = FileSystemReadTool(workspace_root=ws)
    list_tool = FileSystemListTool(workspace_root=ws)

    # Write into categorized directories
    await write_tool.execute(path="documents/notes.md", content="# Meeting Notes")
    await write_tool.execute(path="code/script.py", content="print('hello')")
    await write_tool.execute(path="outputs/report.txt", content="Report Summary")

    # Read from categorized directories
    assert await read_tool.execute(path="documents/notes.md") == "# Meeting Notes"
    assert await read_tool.execute(path="code/script.py") == "print('hello')"

    # List workspace root
    root_entries = await list_tool.execute()
    entry_names = [e["name"] for e in root_entries]
    for cat in categories:
        assert cat in entry_names

    # List subfolder
    doc_entries = await list_tool.execute(path="documents")
    assert any(e["name"] == "notes.md" for e in doc_entries)

