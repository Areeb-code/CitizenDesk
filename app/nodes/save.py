import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app import config
from app.state import AgentState


COMPLAINTS_FILE = config.DATA_DIR / "complaints.json"


def _load_complaints(file_path: Path) -> list[dict]:
    """Load existing complaints from JSON."""

    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            complaints = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Complaints file contains invalid JSON: {file_path}"
        ) from error

    if not isinstance(complaints, list):
        raise ValueError(
            "The complaints JSON file must contain a list."
        )

    if not all(isinstance(item, dict) for item in complaints):
        raise ValueError(
            "Every saved complaint must be a JSON object."
        )

    return complaints


def _write_complaints(
    complaints: list[dict],
    file_path: Path,
) -> None:
    """Write complaints safely to a JSON file."""

    file_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = file_path.with_suffix(".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(
            complaints,
            file,
            ensure_ascii=False,
            indent=4,
        )
        file.write("\n")

    temporary_path.replace(file_path)


def save_node(state: AgentState) -> dict:
    """Save complaint facts, drafts, and review results to JSON."""

    facts = state.get("facts", {})
    drafts = state.get("draft", [])
    review = state.get("review", {})

    if not isinstance(facts, dict):
        return {
            "status": "save_failed",
            "log": ["Save failed: complaint facts must be a dictionary."],
        }

    if not isinstance(drafts, list):
        return {
            "status": "save_failed",
            "log": ["Save failed: drafts must be a list."],
        }

    if not isinstance(review, dict):
        return {
            "status": "save_failed",
            "log": ["Save failed: review must be a dictionary."],
        }

    # Reuse an existing ID if this complaint is being saved again.
    complaint_id = str(
        state.get("complaint_id") or uuid.uuid4().hex
    )

    record = {
        "complaint_id": complaint_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "complaint": state.get("complaint", ""),
        "language": state.get("language", "English"),
        "facts": facts,
        "authority": state.get("authority", ""),
        "research_results": state.get("research_results", []),
        "channels": state.get("channels", []),
        "drafts": drafts,
        "review": review,
        "status": state.get("status", "completed"),
        "research_attempts": state.get("attempt", 0),
    }

    try:
        complaints = _load_complaints(COMPLAINTS_FILE)

        # Avoid adding the same complaint ID twice.
        existing_index = next(
            (
                index
                for index, item in enumerate(complaints)
                if item.get("complaint_id") == complaint_id
            ),
            None,
        )

        if existing_index is None:
            complaints.append(record)
        else:
            complaints[existing_index] = record

        _write_complaints(complaints, COMPLAINTS_FILE)

    except (OSError, ValueError, TypeError) as error:
        return {
            "status": "save_failed",
            "log": [
                f"Complaint save failed: {type(error).__name__}: {error}"
            ],
        }

    return {
        "saved_file": str(COMPLAINTS_FILE),
        "status": "saved",
        "log": [
            f"Complaint saved successfully with ID {complaint_id}.",
            f"Storage file: {COMPLAINTS_FILE}",
        ],
    }