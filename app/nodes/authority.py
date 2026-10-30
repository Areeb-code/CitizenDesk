import json

from app.state import AgentState
from app.models import get_json_model
from app.prompts import authority_prompt


def authority_node(state: AgentState) -> dict:
    """Identify a likely public authority for the complaint."""

    # 1. Read the complaint facts.
    facts = state.get("facts", {})

    # 2. Validate the facts before using them.
    if not isinstance(facts, dict):
        return {
            "authority": "",
            "status": "needs_info",
            "log": [
                "Authority identification skipped: complaint facts are invalid."
            ],
        }

    issue = facts.get("issue")
    country = facts.get("country")

    if not issue or not country:
        return {
            "authority": "",
            "status": "needs_info",
            "log": [
                "Authority identification skipped: complaint issue or country is missing."
            ],
        }

    log = [
        "Authority identification started.",
        f"Complaint issue: {issue}.",
        f"Country: {country}.",
    ]

    # 3. Initialize the JSON model.
    try:
        model = get_json_model()
    except Exception as error:
        return {
            "authority": "",
            "status": "running",
            "log": log + [
                f"Authority model initialization failed: "
                f"{type(error).__name__}."
            ],
        }

    # 4. Build the prompt and ask the model.
    try:
        prompt = authority_prompt(facts)
        response = model.invoke(prompt)
    except Exception as error:
        return {
            "authority": "",
            "status": "running",
            "log": log + [
                f"Authority identification failed: "
                f"{type(error).__name__}."
            ],
        }

    # 5. Extract and parse the JSON response.
    try:
        content = response.content

        if not isinstance(content, str):
            raise ValueError("The model response was not text.")

        result = json.loads(content)

    except (json.JSONDecodeError, TypeError, ValueError, AttributeError):
        return {
            "authority": "",
            "status": "running",
            "log": log + [
                "Authority identification failed: the model returned invalid JSON."
            ],
        }

    # 6. Validate the response structure.
    if not isinstance(result, dict):
        return {
            "authority": "",
            "status": "running",
            "log": log + [
                "Authority identification failed: expected a JSON object."
            ],
        }

    # 7. Extract the authority candidate.
    authority = result.get("authority", "")

    if not isinstance(authority, str):
        authority = ""

    authority = authority.strip()

    if not authority:
        return {
            "authority": "",
            "status": "running",
            "log": log + [
                "No suitable authority candidate identified. Further research is needed."
            ],
        }

    # 8. Return the candidate for further research and verification.
    return {
        "authority": authority,
        "status": "running",
        "log": log + [
            f"Authority candidate identified: {authority}.",
            "The candidate still requires verification through reliable sources.",
        ],
    }