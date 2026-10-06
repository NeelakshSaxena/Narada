import pytest
from core.agent.researcher import WebResearcher
from core.agent.executor import Executor
from core.tools.registry import ToolRegistry
from core.permissions.engine import PermissionEngine
from providers.tools.web import WebSearchTool, WebOpenTool
from core.providers.base import LLMProvider
from core.llm.models import LLMResponse

class MockResearchLLM(LLMProvider):
    def __init__(self):
        self.step = 0

    async def generate(self, prompt: str, **kwargs) -> LLMResponse:
        if "What information is needed?" in prompt:
            return LLMResponse(text="I need to find the population of Paris.", metadata={})
        elif "Propose search query" in prompt:
            return LLMResponse(text="", metadata={"search_query": "population of Paris"})
        elif "Extract facts" in prompt:
            return LLMResponse(text="", metadata={"fact": "Paris population is 2.16 million."})
        elif "materially answered" in prompt:
            self.step += 1
            # Stop after 1 successful extraction
            return LLMResponse(text="", metadata={"stop": self.step >= 1})
        elif "Summarize" in prompt:
            return LLMResponse(text="Summary: Paris has 2.16M people.", metadata={})
        return LLMResponse(text="Fallback", metadata={})
        
    async def stream(self, prompt: str, **kwargs):
        pass

def test_web_researcher_pipeline():
    async def run_test():
        registry = ToolRegistry()
        registry.register(WebSearchTool())
        registry.register(WebOpenTool())
        
        engine = PermissionEngine()
        executor = Executor(tool_registry=registry, permission_engine=engine, allowed_tools=["web.search", "web.open"])
        
        llm = MockResearchLLM()
        researcher = WebResearcher(llm_provider=llm, executor=executor)
        
        summary = await researcher.research("What is the population of Paris?")
        
        assert "Summary: Paris has 2.16M people." in summary
        
        # Audit log should reflect the search and open tool usage
        actions = [log["action"] for log in executor.audit_log]
        assert "web.search" in actions
        assert "web.open" in actions
        assert len(executor.audit_log) == 2
    import asyncio
    asyncio.run(run_test())
