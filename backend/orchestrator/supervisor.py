import concurrent.futures
import logging
from typing import Any, Dict, List, Literal

from langgraph.graph import END, StateGraph

from agents.critic import critique_findings
from agents.planner import plan_subtasks
from agents.researcher import run_arxiv_researcher, run_web_researcher
from agents.state import ResearchState
from agents.writer import write_report

logger = logging.getLogger(__name__)

MAX_RETRIES = 3


def plan_node(state: ResearchState) -> ResearchState:
    subtasks = plan_subtasks(state["question"])
    return {**state, "subtasks": subtasks, "status": "planned"}


def research_parallel_node(state: ResearchState) -> ResearchState:
    subtasks = state["subtasks"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        arxiv_future = executor.submit(run_arxiv_researcher, subtasks)
        web_future = executor.submit(run_web_researcher, subtasks)
        arxiv_results = arxiv_future.result()
        web_results = web_future.result()

    combined_findings = _combine_findings(arxiv_results, web_results)

    return {
        **state,
        "arxiv_results": arxiv_results,
        "web_results": web_results,
        "combined_findings": combined_findings,
        "status": "researched",
    }


def critique_node(state: ResearchState) -> ResearchState:
    critique = critique_findings(state["question"], state["combined_findings"])

    if critique.get("verdict") == "RETRY":
        follow_ups = critique.get("follow_up_queries") or []
        return {
            **state,
            "critique": critique,
            "retry_count": state["retry_count"] + 1,
            "subtasks": follow_ups if follow_ups else state["subtasks"],
            "status": "critiqued",
        }

    return {**state, "critique": critique, "status": "critiqued"}


def write_node(state: ResearchState) -> ResearchState:
    final_report = write_report(state["question"], state["combined_findings"], state["critique"])
    return {**state, "final_report": final_report, "status": "done"}


def route_after_critique(state: ResearchState) -> Literal["research_parallel", "write"]:
    verdict = state["critique"].get("verdict")
    if verdict == "RETRY" and state["retry_count"] < MAX_RETRIES:
        return "research_parallel"
    return "write"


def _combine_findings(arxiv_results: List[Dict[str, Any]], web_results: List[Dict[str, Any]]) -> str:
    lines = ["## arXiv findings"]
    for r in arxiv_results:
        lines.append(f"- {r.get('title')}: {str(r.get('abstract', ''))[:300]}")

    lines.append("\n## Web findings")
    for r in web_results:
        lines.append(f"- {r.get('title')}: {r.get('snippet', '')}")

    return "\n".join(lines)


def build_graph():
    graph = StateGraph(ResearchState)

    graph.add_node("plan", plan_node)
    graph.add_node("research_parallel", research_parallel_node)
    graph.add_node("review", critique_node)
    graph.add_node("write", write_node)

    graph.set_entry_point("plan")
    graph.add_edge("plan", "research_parallel")
    graph.add_edge("research_parallel", "review")
    graph.add_conditional_edges(
        "review",
        route_after_critique,
        {"research_parallel": "research_parallel", "write": "write"},
    )
    graph.add_edge("write", END)

    return graph.compile()


def run_research(question: str) -> ResearchState:
    graph = build_graph()
    initial_state: ResearchState = {
        "question": question,
        "subtasks": [],
        "arxiv_results": [],
        "web_results": [],
        "combined_findings": "",
        "critique": {},
        "final_report": {},
        "retry_count": 0,
        "status": "start",
    }
    return graph.invoke(initial_state)
