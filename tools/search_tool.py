from crewai_tools import SerperDevTool
from tavily import TavilyClient
from crewai.tools import BaseTool
from pydantic import Field
import os


class TavilySearchTool(BaseTool):
    name: str = "Web Search"
    description: str = (
        "Search the web for current information on any topic. "
        "Input should be a search query string. "
        "Returns relevant web results with titles, content, and URLs."
    )
    max_results: int = Field(default=5)

    def _run(self, query: str) -> str:
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        response = client.search(
            query=query,
            max_results=self.max_results,
            search_depth="advanced",
        )
        results = []
        for r in response.get("results", []):
            results.append(
                f"Title: {r.get('title', '')}\n"
                f"URL: {r.get('url', '')}\n"
                f"Content: {r.get('content', '')}\n"
            )
        return "\n---\n".join(results) if results else "No results found."


def get_search_tool() -> TavilySearchTool:
    """Returns a CrewAI-compatible Tavily search tool."""
    return TavilySearchTool()