import json
import re

from app.state import AgentState
from app.models import get_json_model
from app.prompts import intake_prompt


# These fields are important for researching and drafting a complaint.
REQUIRED_FIELDS = [
    "issue",
    "country",
    "city",
    "location",
    "duration",
    "impact",
]

# These are the fields that the intake prompt is expected to return.
ALLOWED_FIELDS = [
    "issue",
    "category",
    "country",
    "city",
    "location",
    "duration",
    "impact",
    "language",
]


def _response_text(response) -> str:
    """Extract text from the model response."""

    content = getattr(response, "content", response)

    if not isinstance(content, str):
        raise ValueError("The model response is not text.")

    return content.strip()


def _parse_intake_response(response_text: str) -> dict:
    """Parse the model's JSON response into a dictionary."""

    # Handle responses wrapped in Markdown code fences.
    cleaned = response_text.strip()

    if cleaned.startswith("```"):
        cleaned = re.sub(
            r"\A```(?:json)?\s*",
            "",
            cleaned,
            count=1,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*```\Z", "", cleaned, count=1)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The model did not return valid JSON."
        ) from error

    if not isinstance(data, dict):
        raise ValueError(
            "The model response must be a JSON object."
        )

    # Keep only expected fields and normalize their values.
    facts = {}

    for field in ALLOWED_FIELDS:
        value = data.get(field, "")

        if isinstance(value, str):
            facts[field] = value.strip()
        elif value is None:
            facts[field] = ""
        else:
            facts[field] = str(value).strip()

    return facts


def intake_node(state: AgentState) -> dict:
    """
    Convert a citizen's complaint into structured facts
    and identify information that still needs clarification.
    """

    complaint = str(state.get("complaint") or "").strip()
    language = str(state.get("language") or "English").strip()

    if not complaint:
        return {
            "facts": {},
            "missing": ["issue"],
            "questions": [],
            "status": "needs_info",
            "log": [
                "Intake stopped because the complaint is empty."
            ],
        }

    log = [
        "Intake started.",
        f"Preferred response language: {language}.",
    ]

    # Initialize the configured JSON model.
    try:
        model = get_json_model()
    except Exception as error:
        return {
            "facts": {},
            "missing": list(REQUIRED_FIELDS),
            "questions": [],
            "status": "needs_info",
            "log": log + [
                f"Intake model initialization failed: "
                f"{type(error).__name__}."
            ],
        }

    # Ask the model to extract facts from the complaint.
    try:
        prompt = intake_prompt(complaint)
        response = model.invoke(prompt)
        response_text = _response_text(response)
        facts = _parse_intake_response(response_text)

    except Exception as error:
        return {
            "facts": {},
            "missing": list(REQUIRED_FIELDS),
            "questions": [],
            "status": "needs_info",
            "log": log + [
                f"Intake extraction failed: "
                f"{type(error).__name__}: {error}"
            ],
        }

    # Prefer the citizen's explicitly supplied language.
    facts["language"] = language

    # Determine which required facts are missing.
    missing = [
        field
        for field in REQUIRED_FIELDS
        if not facts.get(field)
    ]

    log.append("Complaint facts extracted successfully.")
    log.append(f"Missing required fields: {len(missing)}.")

    if missing:
        status = "needs_info"
        log.append(
            "The complaint needs clarification before research can continue."
        )
    else:
        status = "running"
        log.append(
            "Required intake fields are present. Research can continue."
        )

    return {
        "facts": facts,
        "missing": missing,
        "questions": [],
        "status": status,
        "log": log,
    }