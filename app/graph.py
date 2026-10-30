from langgraph.graph import StateGraph, START, END

from app.state import AgentState
from app.router import route_after_intake, route_after_review

from app.nodes.intake import intake_node
from app.nodes.feedback import feedback_node
from app.nodes.authority import authority_node
from app.nodes.researcher import researcher_node
from app.nodes.verifier import verifier_node
from app.nodes.writer import writer_node
from app.nodes.reviewer import reviewer_node
from app.nodes.save import save_node


def rewrite_node(state: AgentState) -> dict:
    """Revise a draft and count the revision attempt."""

    result = writer_node(state)

    return {
        **result,
        "revision": state.get("revision", 0) + 1,
        "log": [
            f"Draft revision {state.get('revision', 0) + 1} started."
        ] + result.get("log", []),
    }


def manual_review_node(state: AgentState) -> dict:
    """Stop automatic revisions and flag the complaint for human review."""

    return {
        "status": "manual_review",
        "log": [
            "Automatic revision limit reached.",
            "Human review is required before the complaint is finalized.",
        ],
    }


def route_after_feedback(state: AgentState) -> str:
    """Continue only when the required information is available."""

    if state.get("missing"):
        return "ask"

    return "continue"


def build_graph():
    """Build and compile the CitizenDesk workflow."""

    builder = StateGraph(AgentState)

    # Register the workflow nodes.
    builder.add_node("intake", intake_node)
    builder.add_node("feedback", feedback_node)
    builder.add_node("authority", authority_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("verifier", verifier_node)
    builder.add_node("writer", writer_node)
    builder.add_node("reviewer", reviewer_node)
    builder.add_node("rewrite", rewrite_node)
    builder.add_node("save", save_node)
    builder.add_node("manual_review", manual_review_node)

    # Define the starting point.
    builder.add_edge(START, "intake")

    # Check whether intake needs clarification.
    builder.add_conditional_edges(
        "intake",
        route_after_intake,
        {
            "ask": "feedback",
            "continue": "authority",
            "stop": END,
        },
    )

    # Ask for missing information, or continue if answers were supplied.
    builder.add_conditional_edges(
        "feedback",
        route_after_feedback,
        {
            "ask": END,
            "continue": "authority",
        },
    )

    # Research and draft the complaint.
    builder.add_edge("authority", "researcher")
    builder.add_edge("researcher", "verifier")
    builder.add_edge("verifier", "writer")
    builder.add_edge("writer", "reviewer")

    # Decide whether to save, rewrite, or require human review.
    builder.add_conditional_edges(
        "reviewer",
        route_after_review,
        {
            "save": "save",
            "rewrite": "rewrite",
            "manual_review": "manual_review",
        },
    )

    # Recheck the revised draft.
    builder.add_edge("rewrite", "reviewer")

    # End after saving or flagging for human review.
    builder.add_edge("save", END)
    builder.add_edge("manual_review", END)

    return builder.compile()


graph = build_graph()