import logging
from typing import Any, Dict, List

from fastapi import APIRouter
from pydantic import BaseModel

from orchestrator.supervisor import run_research

logger = logging.getLogger(__name__)

router = APIRouter()


class ResearchRequest(BaseModel):
    question: str


class ResearchResponse(BaseModel):
    report: Dict[str, Any]
    sources: List[str]
    critique: Dict[str, Any]
    retry_count: int
    status: str


@router.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@router.post("/api/research", response_model=ResearchResponse)
def research(request: ResearchRequest) -> ResearchResponse:
    final_state = run_research(request.question)

    arxiv_sources = [r.get("url", "") for r in final_state.get("arxiv_results", [])]
    web_sources = [r.get("url", "") for r in final_state.get("web_results", [])]

    return ResearchResponse(
        report=final_state.get("final_report", {}),
        sources=[s for s in arxiv_sources + web_sources if s],
        critique=final_state.get("critique", {}),
        retry_count=final_state.get("retry_count", 0),
        status=final_state.get("status", "unknown"),
    )
