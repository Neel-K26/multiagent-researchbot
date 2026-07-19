import json
import logging
import os
from typing import List

from crewai import LLM, Agent, Crew, Process, Task

logger = logging.getLogger(__name__)


def build_planner_llm() -> LLM:
    # NVIDIA Build (OpenAI-compatible) via litellm's generic "openai/" +
    # base_url routing — see agents/researcher.py for why this is a
    # crewai.LLM rather than langchain_openai.ChatOpenAI.
    return LLM(
        model="openai/deepseek-ai/deepseek-v4-pro",
        api_key=os.environ["NVIDIA_API_KEY"],
        base_url="https://integrate.api.nvidia.com/v1",
        temperature=0.1,
        timeout=120,
        num_retries=8,
        retry_strategy="exponential_backoff_retry",
    )


def build_planner_agent() -> Agent:
    return Agent(
        role="Research Planner",
        goal="Break a research question into specific, independently searchable subtasks",
        backstory=(
            "You are an expert research strategist who decomposes broad research "
            "questions into precise subtasks suited for arXiv and web search."
        ),
        llm=build_planner_llm(),
        verbose=True,
        allow_delegation=False,
    )


def plan_subtasks(question: str) -> List[str]:
    """Run the planner agent and return exactly 3 search subtasks.

    Falls back to a single subtask (the original question) if the LLM
    output cannot be parsed as a JSON array of strings.
    """
    agent = build_planner_agent()
    task = Task(
        description=(
            "Break the following research question into exactly 3 specific, "
            "independently searchable subtasks suitable for arXiv and web "
            f"search.\n\nResearch question: {question}\n\n"
            "Respond with ONLY a JSON array of 3 strings, no other text."
        ),
        expected_output='A JSON array of exactly 3 subtask strings, e.g. ["subtask 1", "subtask 2", "subtask 3"]',
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()

    subtasks = _parse_json_array(str(result))
    if not subtasks:
        logger.warning("Planner output unparseable, falling back to raw question")
        subtasks = [question]
    return subtasks


def _parse_json_array(raw: str) -> List[str]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.split("\n", 1)[-1] if "\n" in raw else raw
    try:
        start = raw.index("[")
        end = raw.rindex("]") + 1
        parsed = json.loads(raw[start:end])
        if isinstance(parsed, list) and all(isinstance(x, str) for x in parsed):
            return parsed
    except (ValueError, json.JSONDecodeError):
        pass
    return []
