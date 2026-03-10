import os
from dotenv import load_dotenv
from crewai import Crew, Task, Process, LLM
from crew_agents import (
    get_planner_agent,
    get_researcher_agent,
    get_academic_researcher_agent,
    get_summarizer_agent,
    get_critic_agent,
    get_writer_agent,
)
from tools.search_tool import get_search_tool
from tools.arxiv_tool import get_arxiv_tool
from tools.pubmed_tool import get_pubmed_tool

load_dotenv()


def build_llm() -> LLM:
    """Initialize the Google Gemini LLM via CrewAI's native LLM class."""
    return LLM(
        model="gemini/gemini-2.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.3,
    )


def run_research_pipeline(topic: str, depth: str = "standard") -> dict:
    """
    Run the full multi-agent research pipeline.

    Args:
        topic: The research topic from the user.
        depth: "quick" (3 sub-questions) or "standard" (5 sub-questions) or "deep" (7 sub-questions)

    Returns:
        dict with keys: plan, raw_research, academic_research, summary, critique, final_report
    """
    llm = build_llm()
    search_tool = get_search_tool()
    arxiv_tool = get_arxiv_tool()
    pubmed_tool = get_pubmed_tool()

    # Build all agents
    planner             = get_planner_agent(llm)
    researcher          = get_researcher_agent(llm, search_tool)
    academic_researcher = get_academic_researcher_agent(llm, arxiv_tool, pubmed_tool)
    summarizer          = get_summarizer_agent(llm)
    critic              = get_critic_agent(llm)
    writer              = get_writer_agent(llm)

    depth_map = {"quick": 3, "standard": 5, "deep": 7}
    num_questions = depth_map.get(depth, 5)

    # --- Define Tasks ---

    task_plan = Task(
        description=(
            f"Analyze this research topic: '{topic}'\n\n"
            f"Break it down into exactly {num_questions} specific, focused sub-questions "
            f"that together cover the topic comprehensively. "
            f"Format your output as a numbered list of sub-questions."
        ),
        expected_output=(
            f"A numbered list of {num_questions} specific sub-questions about '{topic}', "
            f"each on its own line."
        ),
        agent=planner,
    )

    task_research = Task(
        description=(
            f"You have been given a list of sub-questions about '{topic}'. "
            f"For EACH sub-question, search the web and gather relevant facts, statistics, "
            f"expert opinions, and source URLs. "
            f"Present your findings clearly labeled by sub-question number."
        ),
        expected_output=(
            f"A detailed collection of findings for each sub-question about '{topic}', "
            f"with source URLs cited for key claims."
        ),
        agent=researcher,
        context=[task_plan],
    )

    task_academic = Task(
        description=(
            f"You have been given a list of sub-questions about '{topic}'. "
            f"For EACH sub-question, search ArXiv and PubMed to find the most relevant "
            f"peer-reviewed papers, preprints, or clinical studies. "
            f"For each paper found, provide: title, authors, journal/source, year, URL, and a "
            f"brief summary of key findings from the abstract. "
            f"Label findings clearly by sub-question number. "
            f"If a topic is not covered in academic literature, state that explicitly."
        ),
        expected_output=(
            f"A structured list of academic papers for each sub-question about '{topic}', "
            f"with full citation details (title, authors, year, URL) and abstract summaries."
        ),
        agent=academic_researcher,
        context=[task_plan],
    )

    task_summarize = Task(
        description=(
            f"Take BOTH the web research findings AND the academic research findings about '{topic}' "
            f"and produce a unified, structured summary. "
            f"Group related findings by theme. For each theme, distinguish between: "
            f"(1) findings from web/news sources and (2) findings from peer-reviewed papers. "
            f"Highlight key statistics, landmark papers, and expert consensus. "
            f"Note any contradictions between web sources and academic literature."
        ),
        expected_output=(
            f"A well-organized summary of all research findings on '{topic}', "
            f"grouped by theme, clearly distinguishing web sources from academic papers, "
            f"with key statistics and citations preserved."
        ),
        agent=summarizer,
        context=[task_research, task_academic],
    )

    task_critique = Task(
        description=(
            f"Critically evaluate the research summary about '{topic}'. "
            f"Identify: factual gaps, unsupported claims, contradictions, and missing perspectives. "
            f"Pay special attention to whether academic sources back up web claims. "
            f"Give a quality score out of 10 with brief justification. "
            f"List 3-5 specific improvement notes for the Writer Agent to address."
        ),
        expected_output=(
            f"A critique of the research on '{topic}' including: "
            f"a quality score (X/10), identified gaps or weaknesses, "
            f"and 3-5 specific actionable notes for the final report writer."
        ),
        agent=critic,
        context=[task_summarize],
    )

    task_write = Task(
        description=(
            f"Write a focused research report on '{topic}' in markdown. "
            f"Keep it concise — do NOT repeat everything from the summary. "
            f"Structure exactly as follows:\n"
            f"1. ## Executive Summary (3-4 sentences)\n"
            f"2. ## Key Findings (3-4 sections, 2-3 paragraphs each)\n"
            f"3. ## Key Takeaways (5 bullet points)\n"
            f"4. ## Academic References (list papers from academic research)\n"
            f"5. ## Web Sources (list URLs from web research)\n"
            f"Address the top 2-3 critique points only. Be sharp and direct."
        ),
        expected_output=(
            f"A concise markdown research report on '{topic}' with exactly the 5 sections listed. "
            f"Total length: 600-900 words. No filler, no repetition."
        ),
        agent=writer,
        context=[task_summarize, task_critique],
    )

    # --- Assemble Crew ---
    crew = Crew(
        agents=[planner, researcher, academic_researcher, summarizer, critic, writer],
        tasks=[task_plan, task_research, task_academic, task_summarize, task_critique, task_write],
        process=Process.sequential,
        verbose=True,
    )

    result = crew.kickoff()

    def get_output(task):
        try:
            if task.output:
                if hasattr(task.output, 'raw'):
                    return task.output.raw or ""
                return str(task.output)
        except Exception:
            pass
        return ""

    outputs = {
        "plan":              get_output(task_plan),
        "raw_research":      get_output(task_research),
        "academic_research": get_output(task_academic),
        "summary":           get_output(task_summarize),
        "critique":          get_output(task_critique),
        "final_report":      get_output(task_write) or str(result),
    }

    # Fallback: if final_report is empty, use the crew result directly
    if not outputs["final_report"].strip():
        outputs["final_report"] = str(result.raw) if hasattr(result, 'raw') else str(result)

    return outputs