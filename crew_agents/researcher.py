from crewai import Agent, LLM
from crewai.tools import BaseTool


def get_researcher_agent(llm: LLM, search_tool: BaseTool) -> Agent:
    """
    Researcher Agent: Takes each sub-question and searches the web
    to gather raw factual information and sources.
    """
    return Agent(
        role="Web Researcher",
        goal=(
            "For each sub-question provided, search the web thoroughly and gather "
            "accurate, up-to-date information. Collect key facts, statistics, expert "
            "opinions, and relevant sources. Always note the source URL for every piece of data."
        ),
        backstory=(
            "You are an investigative researcher who previously worked for Reuters and "
            "the BBC. You have an obsession with primary sources and verifiable facts. "
            "You distrust single-source claims and always cross-reference. "
            "You are fast, methodical, and leave no sub-question unanswered."
        ),
        llm=llm,
        tools=[search_tool],
        verbose=True,
        allow_delegation=False,
        max_iter=5,
    )