from app import config
from app.state import AgentState


def route_after_intake(state: AgentState) -> str:
    """Stop on a local model failure; otherwise ask or continue."""
    if state.get("status") in {"service_unavailable", "extraction_failed"}:
        return "stop"
    if state.get("missing"):
        return "ask"
    return "continue"


def route_after_review(state: AgentState) -> str:
    """Choose whether to save, rewrite, or request manual review."""
    review = state.get("review", {})
    passed = review.get("passed")
    if passed is None:
        passed = review.get("score", 0) >= config.PASS_SCORE
    if passed:
        return "save"
    if state.get("revision", 0) < config.MAX_REVISIONS:
        return "rewrite"
    return "manual_review"
