from app.tools.contract import add_contacts
from app.tools.search import search_web
from app.tools.extract import extract_contacts
from app.state import AgentState


def researcher_node(state: AgentState) -> dict:
    """Search for authority information and extract contact candidates."""

    facts = state.get("facts", {})
    if not isinstance(facts, dict):
        facts = {}

    authority = str(state.get("authority") or "").strip()
    country = str(facts.get("country") or "").strip()
    city = str(facts.get("city") or "").strip()
    category = str(facts.get("category") or "").strip()
    issue = str(facts.get("issue") or "").strip()

    attempt = state.get("attempt", 0) + 1
    research_mode = state.get("research_mode") or "normal"

    log = [
        f"Research round {attempt} started.",
        f"Research mode: {research_mode}.",
        f"Authority to investigate: {authority or 'not identified'}.",
    ]

    if not authority:
        return {
            "attempt": attempt,
            "research_results": [],
            "channels": [],
            "status": "needs_info",
            "log": log + [
                "Research stopped because no authority was identified."
            ],
        }

    # Build a search query.
    if research_mode == "extended":
        query = (
            f"{authority} {category} {issue} "
            f"{city} {country} government complaint contact alternatives"
        )
    else:
        query = (
            f"{authority} official website contact complaint "
            f"{category} {city} {country}"
        )

    log.append(f"Prepared research query: {query}")

    # Search the web.
    try:
        results = search_web(query, max_results=5)

    except Exception as error:
        return {
            "attempt": attempt,
            "research_mode": research_mode,
            "research_results": [],
            "channels": [],
            "status": "running",
            "log": log + [
                f"Web search failed: {type(error).__name__}: {error}",
                "The research attempt did not complete successfully.",
            ],
        }

    if not results:
        return {
            "attempt": attempt,
            "research_mode": research_mode,
            "research_results": [],
            "channels": [],
            "status": "running",
            "log": log + [
                "The search completed, but no results were found."
            ],
        }

    log.append(f"Tavily returned {len(results)} search results.")

    # Extract contact candidates and save them to JSON.
    try:
        channels = extract_contacts(results)

    except Exception as error:
        return {
            "attempt": attempt,
            "research_mode": research_mode,
            "research_results": results,
            "channels": [],
            "status": "running",
            "log": log + [
                f"Contact extraction failed: {type(error).__name__}: {error}"
            ],
        }

    log.append(
        f"Contact extraction produced {len(channels)} candidate(s)."
    )

    # Save extracted candidates to data/contacts.json.
    try:
        save_result = add_contacts(channels)

        log.append(
            f"Contact storage: {save_result['added']} new contact(s) saved; "
            f"{save_result['duplicates']} duplicate(s) skipped."
        )

    except Exception as error:
        log.append(
            f"Contact storage failed: {type(error).__name__}: {error}"
        )

    return {
        "attempt": attempt,
        "research_mode": research_mode,
        "research_results": results,
        "channels": channels,
        "status": "running",
        "log": log,
    }