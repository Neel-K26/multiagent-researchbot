import json
import logging
import os
from typing import Any, Dict

from crewai import Agent, Crew, Process, Task
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)


def build_writer_llm() -> ChatGroq:
    return ChatGroq(
        model_name="llama-3.1-8b-instant",
        groq_api_key=os.environ["GROQ_API_KEY"],
        temperature=0.4,
    )


def build_writer_agent() -> Agent:
    return Agent(
        role="Research Writer",
        goal="Synthesize research findings into a clear, structured report",
        backstory=(
            "You are a skilled technical writer who turns raw research findings "
            "into concise, well-cited reports for a technical audience."
        ),
        llm=build_writer_llm(),
        verbose=True,
        allow_delegation=False,
    )


def write_report(question: str, combined_findings: str, critique: Dict[str, Any]) -> Dict[str, Any]:
    """Run the writer agent and return a structured report.

    Falls back to a low-confidence report wrapping the raw LLM text if the
    output cannot be parsed as a JSON object.
    """
    agent = build_writer_agent()
    task = Task(
        description=(
            f"Research question: {question}\n\n"
            f"Combined findings:\n{combined_findings}\n\n"
            f"Critic's assessment: {critique.get('critique', '')}\n\n"
            "Write a final structured research report. Respond with ONLY a JSON "
            "object with exactly these keys:\n"
            '- "summary": a short executive summary\n'
            '- "key_findings": a JSON array of key finding strings\n'
            '- "sources": a JSON array of source URLs referenced\n'
            '- "confidence_score": a float between 0 and 1'
        ),
        expected_output="A JSON object with keys summary, key_findings, sources, confidence_score.",
        agent=agent,
    )
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=True)
    result = crew.kickoff()

    parsed = _parse_json_object(str(result))
    if parsed and "summary" in parsed:
        parsed.setdefault("key_findings", [])
        parsed.setdefault("sources", [])
        parsed.setdefault("confidence_score", 0.5)
        return parsed

    logger.warning("Writer output unparseable, falling back to raw text report")
    return {
        "summary": str(result),
        "key_findings": [],
        "sources": [],
        "confidence_score": 0.0,
    }


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
