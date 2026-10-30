import json
from pathlib import Path

from app import config


CONTACTS_FILE = config.DATA_DIR / "contacts.json"


def _load_contacts(file_path: Path = CONTACTS_FILE) -> list[dict]:
    """Load saved contacts from JSON, returning an empty list if absent."""
    if not file_path.exists():
        return []

    try:
        with file_path.open("r", encoding="utf-8") as file:
            contacts = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Contacts file contains invalid JSON: {file_path}"
        ) from error

    if not isinstance(contacts, list):
        raise ValueError(
            "The contacts JSON file must contain a list."
        )

    if not all(isinstance(item, dict) for item in contacts):
        raise ValueError(
            "Every saved contact must be a JSON object."
        )

    return contacts


def _save_contacts(
    contacts: list[dict],
    file_path: Path = CONTACTS_FILE,
) -> None:
    """Write contacts to JSON, creating the parent directory if needed."""
    file_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = file_path.with_suffix(".tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(
            contacts,
            file,
            ensure_ascii=False,
            indent=4,
        )
        file.write("\n")

    temporary_path.replace(file_path)


def _contact_key(contact: dict) -> tuple[str, str, str]:
    """Build a key for detecting duplicate contact records."""
    return (
        str(contact.get("type", "")).strip().lower(),
        str(contact.get("value", "")).strip().lower(),
        str(
            contact.get("source_url")
            or contact.get("url")
            or ""
        ).strip().rstrip("/").lower(),
    )


def add_contacts(
    new_contacts: list[dict],
    file_path: Path = CONTACTS_FILE,
) -> dict:
    """
    Add contact candidates to JSON storage without duplicating records.

    Returns counts for newly added and duplicate candidates.
    """
    if not isinstance(new_contacts, list):
        raise TypeError("new_contacts must be a list.")

    if not all(isinstance(item, dict) for item in new_contacts):
        raise TypeError("Every new contact must be a dictionary.")

    contacts = _load_contacts(file_path)
    existing_keys = {
        _contact_key(contact)
        for contact in contacts
    }

    added = 0
    duplicates = 0

    for contact in new_contacts:
        value = str(contact.get("value", "")).strip()
        channel_type = str(contact.get("type", "")).strip()

        if not value or not channel_type:
            continue

        key = _contact_key(contact)

        if key in existing_keys:
            duplicates += 1
            continue

        contacts.append(dict(contact))
        existing_keys.add(key)
        added += 1

    _save_contacts(contacts, file_path)

    return {
        "added": added,
        "duplicates": duplicates,
        "total": len(contacts),
        "file_path": str(file_path),
    }


def get_contacts(
    file_path: Path = CONTACTS_FILE,
) -> list[dict]:
    """Return all contacts currently saved in JSON storage."""
    return _load_contacts(file_path)