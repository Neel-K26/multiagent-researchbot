import json
import logging
import os
from typing import Any, Dict

from crewai import LLM, Agent, Crew, Process, Task

logger = logging.getLogger(__name__)


def build_critic_llm() -> LLM:
    # gemini-1.5-flash and gemini-2.5-flash are both retired/blocked for this
    # account; gemini-flash-latest is Google's forward-compatible alias for
    # the current flash-tier model, avoiding another hardcoded-version 404.
    return LLM(
        model="gemini/gemini-flash-latest",
        api_key=os.environ["GEMINI_API_KEY"],
        temperature=0.2,
        num_retries=8,
        retry_strategy="exponential_backoff_retry",
    )


def build_critic_agent() -> Agent:
    return Agent(
        role="Research Critic",
        goal="Rigorously review research findings for gaps, contradictions, and weak evidence",
        backstory=(
            "You are a skeptical peer reviewer who stress-tests research findings "
            "before they are published, flagging anything unsupported, "
            "contradictory, or thin."
        ),
        llm=build_critic_llm(),
        verbose=True,
        allow_delegation=False,
    )


def critique_findings(question: str, combined_findings: str) -> Dict[str, Any]:
    """Run the critic agent over combined findings.

    Defaults to a STRONG verdict if the LLM output cannot be parsed, so a
    formatting slip never causes an infinite retry loop.
    """
    agent = build_critic_agent()
    task = Task(
        description=(
            f"Research question: {question}\n\n"
            f"Combined findings:\n{combined_findings}\n\n"
            "Review these findings for gaps, contradictions, and weak evidence. "
            "Respond with ONLY a JSON object with exactly these keys:\n"
            '- "verdict": either "STRONG" or "RETRY"\n'
            '- "critique": a short paragraph explaining your assessment\n'
            '- "follow_up_queries": a JSON array of follow-up search queries '
            "(empty array if verdict is STRONG)"
        ),
        expected_output="A JSON object with keys verdict, critique, follow_up_queries.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()

    parsed = _parse_json_object(str(result))
    if parsed and "verdict" in parsed:
        parsed.setdefault("critique", "")
        parsed.setdefault("follow_up_queries", [])
        return parsed

    logger.warning("Critic output unparseable, defaulting to STRONG to avoid infinite retries")
    return {"verdict": "STRONG", "critique": str(result), "follow_up_queries": []}


def _parse_json_object(raw: str) -> Dict[str, Any]:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        raw = raw.split("\n", 1)[-1] if "\n" in raw else raw
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        parsed = json.loads(raw[start:end])
        if isinstance(parsed, dict):
            return parsed
    except (ValueError, json.JSONDecodeError):
        pass
    return {}
