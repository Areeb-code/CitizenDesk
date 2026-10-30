import json

from app.state import AgentState
from app.models import get_writer_model
from app.prompts import (
    email_prompt,
    call_summary_prompt,
    CALL_SCRIPT_TEMPLATE,
)


def _response_text(response) -> str:
    """Extract text from a language-model response."""
    content = getattr(response, "content", response)

    if not isinstance(content, str):
        raise ValueError("The model returned a non-text response.")

    return content.strip()


def _build_call_script(summary_data: dict, facts: dict) -> str:
    """Fill the phone-call script template with generated content."""
    summary = str(summary_data.get("summary", "")).strip()
    have_ready = summary_data.get("have_ready", [])

    if not summary:
        raise ValueError("The model did not provide a call summary.")

    if not isinstance(have_ready, list):
        raise ValueError("'have_ready' must be a list.")

    # Remove empty items and normalize the remaining values.
    items = [
        str(item).strip()
        for item in have_ready
        if str(item).strip()
    ]

    if not items:
        raise ValueError("The model did not provide preparation items.")

    # Avoid inserting multiline text in an unexpected format.
    have_ready_text = "\n".join(
        f"- {item}" for item in items
    )

    issue = str(facts.get("issue") or "the reported problem")

    return (
        CALL_SCRIPT_TEMPLATE
        .replace("{have_ready}", have_ready_text)
        .replace("{issue}", issue)
        .replace("{summary}", summary)
    )


def writer_node(state: AgentState) -> dict:
    """
    Generate an email and phone-call script from complaint facts.

    The node reads state, calls the configured writer model, and
    returns a list of drafts for reviewer_node.
    """
    facts = state.get("facts", {})
    language = str(
        state.get("language")
        or facts.get("language")
        or "English"
    )

    if not isinstance(facts, dict):
        return {
            "draft": [],
            "status": "needs_info",
            "log": [
                "Writer failed: complaint facts are not a dictionary."
            ],
        }

    issue = str(facts.get("issue", "")).strip()
    location = str(facts.get("location", "")).strip()

    if not issue or not location:
        return {
            "draft": [],
            "status": "needs_info",
            "log": [
                "Writer stopped: issue or location is missing."
            ],
        }

    # Copy the facts so the writer does not mutate shared state.
    writing_facts = dict(facts)

    # Authority is stored separately in AgentState.
    writing_facts["authority"] = (
        state.get("authority") or "the concerned authority"
    )

    # Pass previous review feedback to the email prompt when rewriting.
    review = state.get("review", {})
    fixes = ""

    if isinstance(review, dict):
        failed_checks = review.get("failed", [])

        if isinstance(failed_checks, list):
            fixes = "; ".join(
                str(item) for item in failed_checks
            )

    log = [
        "Writer started.",
        f"Writing language: {language}.",
        "Preparing an email and phone-call script.",
    ]

    drafts = []

    try:
        model = get_writer_model()
    except Exception as error:
        return {
            "draft": [],
            "status": "running",
            "log": log + [
                f"Writer could not initialize the model: "
                f"{type(error).__name__}."
            ],
        }

    # 1. Generate the complaint email.
    try:
        prompt = email_prompt(
            writing_facts,
            language=language,
            fixes=fixes,
        )

        response = model.invoke(prompt)
        email_text = _response_text(response)

        if email_text:
            drafts.append({
                "channel": "email",
                "format": "email",
                "text": email_text,
            })

            log.append("Writer generated an email draft.")
        else:
            log.append("Writer received an empty email response.")

    except Exception as error:
        log.append(
            f"Email generation failed: {type(error).__name__}."
        )

    # 2. Generate the phone-call summary and fill the template.
    try:
        prompt = call_summary_prompt(
            writing_facts,
            language=language,
        )

        response = model.invoke(prompt)
        response_text = _response_text(response)

        # The call-summary prompt requires one JSON object.
        summary_data = json.loads(response_text)

        if not isinstance(summary_data, dict):
            raise ValueError(
                "The call-summary response is not a JSON object."
            )

        call_script = _build_call_script(
            summary_data,
            writing_facts,
        )

        drafts.append({
            "channel": "phone",
            "format": "phone",
            "text": call_script,
        })

        log.append("Writer generated a phone-call script.")

    except Exception as error:
        log.append(
            f"Phone script generation failed: "
            f"{type(error).__name__}."
        )

    # Do not report success when neither draft was generated.
    if not drafts:
        log.append("Writer failed to generate any usable drafts.")

        return {
            "draft": [],
            "status": "running",
            "log": log,
        }

    log.append(f"Writer completed with {len(drafts)} draft(s).")

    return {
        "draft": drafts,
        "status": "running",
        "log": log,
    }