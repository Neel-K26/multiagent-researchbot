from typing import TypedDict, List, Dict, Any


class ResearchState(TypedDict):
    question: str
    subtasks: List[str]
    arxiv_results: List[Dict[str, Any]]
    web_results: List[Dict[str, Any]]
    combined_findings: str
    critique: Dict[str, Any]
    final_report: Dict[str, Any]
    retry_count: int
    status: str
