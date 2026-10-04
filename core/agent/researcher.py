from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from core.agent.executor import Executor
from core.providers.base import LLMProvider

@dataclass
class ResearchState:
    query: str
    needed_info: str = ""
    visited_urls: List[str] = field(default_factory=list)
    extracted_facts: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    loop_count: int = 0
    max_loops: int = 3
    status: str = "STARTING"

class WebResearcher:
    def __init__(self, llm_provider: LLMProvider, executor: Executor):
        self.llm = llm_provider
        self.executor = executor
        self.system_prompt = """
        Research the requested topic.
        Rules:
        1. State what information is needed before searching.
        2. Prefer authoritative sources.
        3. Search using the available web tool.
        4. Open relevant sources.
        5. Extract only information needed for the goal.
        6. Track source URLs.
        7. Distinguish facts from inference.
        8. Store durable findings only if they are useful beyond this task.
        9. If evidence conflicts, report the conflict.
        10. Stop searching when additional search is unlikely to materially improve the answer.
        """

    async def research(self, topic: str) -> str:
        state = ResearchState(query=topic)
        state.status = "PLANNING"
        
        # 1. State what information is needed
        plan_response = await self.llm.generate(f"{self.system_prompt}\nTopic: {topic}\nWhat information is needed?")
        state.needed_info = plan_response.text

        while state.loop_count < state.max_loops:
            state.loop_count += 1
            
            # 2. Search
            search_response = await self.llm.generate("Propose search query")
            search_query = search_response.metadata.get("search_query", topic)
            
            search_result = await self.executor.execute("web.search", query=search_query)
            if search_result["status"] != "SUCCESS":
                return f"Research failed at search: {search_result.get('error', search_result)}"
            
            urls = [r["url"] for r in search_result["result"]]
            if not urls:
                break
                
            # Avoid repeating URLs to prevent infinite loop
            target_url = None
            for u in urls:
                if u not in state.visited_urls:
                    target_url = u
                    break
            
            if not target_url:
                break
                
            state.visited_urls.append(target_url)
            
            # 3. Open source
            open_result = await self.executor.execute("web.open", url=target_url)
            if open_result["status"] != "SUCCESS":
                continue
                
            # 4. Extract facts
            extract_response = await self.llm.generate(f"Extract facts from: {open_result['result']}")
            fact = extract_response.metadata.get("fact", "Extracted fact")
            state.extracted_facts.append(f"{fact} (Source: {target_url})")
            
            # 5. Decide to continue or stop
            decide_response = await self.llm.generate("Have we materially answered the query?")
            if decide_response.metadata.get("stop", True):
                break
                
        # 6. Summarize & Write Memory
        summary_response = await self.llm.generate(f"Summarize these facts: {state.extracted_facts}")
        state.summary = summary_response.text
        
        return state.summary
