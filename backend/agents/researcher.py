import json
import logging
import os
from typing import Any, Dict, List

from crewai import LLM, Agent, Crew, Process, Task
from crewai.tools import tool

from tools.arxiv_tool import search_arxiv
from tools.web_search_tool import search_web

logger = logging.getLogger(__name__)


@tool("Search arXiv")
def arxiv_search_tool(query: str) -> str:
    """Search arXiv for academic papers matching the query. Returns a JSON
    string of results, each with title, authors, abstract, url, published."""
    return json.dumps(search_arxiv(query, max_results=5))


@tool("Search Web")
def web_search_tool_fn(query: str) -> str:
    """Search the web for relevant pages matching the query. Returns a JSON
    string of results, each with title, url, snippet."""
    return json.dumps(search_web(query, max_results=5))


def build_researcher_llm() -> LLM:
    # Reverted from NVIDIA Build (deepseek-v4-pro): rate-limited (429) under
    # this pipeline's request volume, with backoff insufficient to clear it.
    # llama-3.3-70b-versatile is the proven-working config for these agents'
    # ReAct tool-calling.
    return LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.3,
        timeout=120,
        num_retries=8,
        retry_strategy="exponential_backoff_retry",
    )


def build_arxiv_researcher() -> Agent:
    return Agent(
        role="ArxivResearcher",
        goal="Find the most relevant academic papers on arXiv for a given subtask",
        backstory=(
            "You are a meticulous academic researcher who mines arXiv for the "
            "strongest, most relevant papers on a topic."
        ),
        llm=build_researcher_llm(),
        tools=[arxiv_search_tool],
        verbose=True,
        allow_delegation=False,
    )


def build_web_researcher() -> Agent:
    return Agent(
        role="WebResearcher",
        goal="Find relevant, credible web sources and citations for a given subtask",
        backstory=(
            "You are a diligent web researcher who tracks down credible sources, "
            "articles, and citations."
        ),
        llm=build_researcher_llm(),
        tools=[web_search_tool_fn],
        verbose=True,
        allow_delegation=False,
    )


def run_arxiv_researcher(subtasks: List[str]) -> List[Dict[str, Any]]:
    """Have the ArxivResearcher agent search arXiv for each subtask.

    Falls back to calling search_arxiv directly (bypassing the LLM) if the
    agent's output cannot be parsed as a JSON array.
    """
    agent = build_arxiv_researcher()
    joined = "\n".join(f"- {s}" for s in subtasks)
    task = Task(
        description=(
            "Use the Search arXiv tool once for EACH of the following subtasks:\n"
            f"{joined}\n\n"
            "Combine all tool results into a single JSON array of paper objects "
            "(title, authors, abstract, url, published). Respond with ONLY that "
            "JSON array, no other text."
        ),
        expected_output="A JSON array of arXiv paper result objects.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()

    parsed = _parse_json_array(str(result))
    if parsed:
        return parsed

    logger.warning("ArxivResearcher output unparseable, falling back to direct tool calls")
    combined: List[Dict[str, Any]] = []
    for subtask in subtasks:
        combined.extend(search_arxiv(subtask, max_results=5))
    return combined


def run_web_researcher(subtasks: List[str]) -> List[Dict[str, Any]]:
    """Have the WebResearcher agent search the web for each subtask.

    Falls back to calling search_web directly (bypassing the LLM) if the
    agent's output cannot be parsed as a JSON array.
    """
    agent = build_web_researcher()
    joined = "\n".join(f"- {s}" for s in subtasks)
    task = Task(
        description=(
            "Use the Search Web tool once for EACH of the following subtasks:\n"
            f"{joined}\n\n"
            "Combine all tool results into a single JSON array of result objects "
            "(title, url, snippet). Respond with ONLY that JSON array, no other text."
        ),
        expected_output="A JSON array of web search result objects.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()

    parsed = _parse_json_array(str(result))
    if parsed:
        return parsed

    logger.warning("WebResearcher output unparseable, falling back to direct tool calls")
    combined: List[Dict[str, Any]] = []
    for subtask in subtasks:
        combined.extend(search_web(subtask, max_results=5))
    return combined


def _parse_json_array(raw: str) -> List[Dict[str, Any]]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.split("\n", 1)[-1] if "\n" in raw else raw
    try:
        start = raw.index("[")
        end = raw.rindex("]") + 1
        parsed = json.loads(raw[start:end])
        if isinstance(parsed, list):
            return parsed
    except (ValueError, json.JSONDecodeError):
        pass
    return []
