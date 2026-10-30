import json
import tempfile
from pathlib import Path

from app.tools.contract import add_contacts, get_contacts


def test_add_and_load_contacts():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "contacts.json"

        contacts = [
            {
                "type": "email",
                "value": "contact@example.gov.pk",
                "source_url": "https://example.gov.pk/contact",
                "source_title": "Contact page",
                "evidence": "Email found on the page.",
            }
        ]

        result = add_contacts(contacts, file_path)

        assert result["added"] == 1
        assert result["duplicates"] == 0
        assert result["total"] == 1

        saved = get_contacts(file_path)

        assert len(saved) == 1
        assert saved[0]["value"] == "contact@example.gov.pk"

        print("JSON save and load test passed.")


def test_duplicate_contacts():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "contacts.json"

        contact = {
            "type": "email",
            "value": "contact@example.gov.pk",
            "source_url": "https://example.gov.pk/contact",
        }

        add_contacts([contact], file_path)
        result = add_contacts([contact], file_path)

        assert result["added"] == 0
        assert result["duplicates"] == 1
        assert len(get_contacts(file_path)) == 1

        print("Duplicate detection test passed.")


def test_json_is_valid():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "contacts.json"

        add_contacts(
            [{
                "type": "website",
                "value": "https://example.gov.pk/contact",
                "source_url": "https://example.gov.pk/contact",
            }],
            file_path,
        )

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        assert isinstance(data, list)

        print("Valid JSON format test passed.")


if __name__ == "__main__":
    test_add_and_load_contacts()
    test_duplicate_contacts()
    test_json_is_valid()

    print("All contract tests passed.")