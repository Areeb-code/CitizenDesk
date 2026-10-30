import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from app.nodes.save import save_node


def test_save_complaint():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "complaints.json"

        state = {
            "complaint": "Stray dogs in the neighbourhood",
            "language": "English",
            "facts": {
                "issue": "stray animals",
                "country": "Pakistan",
                "city": "Lahore",
                "location": "Model Town",
            },
            "authority": "Local government authority",
            "draft": [
                {
                    "channel": "email",
                    "format": "email",
                    "text": "Subject: Complaint about stray dogs",
                }
            ],
            "review": {
                "score": 1.0,
                "passed": True,
            },
            "status": "completed",
            "attempt": 1,
        }

        with patch(
            "app.nodes.save.COMPLAINTS_FILE",
            file_path,
        ):
            result = save_node(state)

        assert result["status"] == "saved"
        assert file_path.exists()

        with file_path.open("r", encoding="utf-8") as file:
            saved = json.load(file)

        assert len(saved) == 1
        assert saved[0]["facts"]["city"] == "Lahore"
        assert saved[0]["drafts"][0]["channel"] == "email"
        assert saved[0]["review"]["passed"] is True

        print("Complaint save test passed.")


def test_save_preserves_existing_complaints():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "complaints.json"

        with patch(
            "app.nodes.save.COMPLAINTS_FILE",
            file_path,
        ):
            first = save_node({
                "complaint": "First complaint",
                "facts": {"issue": "noise"},
                "draft": [],
                "review": {},
                "complaint_id": "complaint-001",
            })

            second = save_node({
                "complaint": "Second complaint",
                "facts": {"issue": "waste"},
                "draft": [],
                "review": {},
                "complaint_id": "complaint-002",
            })

        assert first["status"] == "saved"
        assert second["status"] == "saved"

        with file_path.open("r", encoding="utf-8") as file:
            saved = json.load(file)

        assert len(saved) == 2

        print("Existing complaint preservation test passed.")


def test_same_id_does_not_duplicate():
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = Path(temp_dir) / "complaints.json"

        with patch(
            "app.nodes.save.COMPLAINTS_FILE",
            file_path,
        ):
            state = {
                "complaint": "Noise complaint",
                "facts": {"issue": "noise"},
                "draft": [],
                "review": {},
                "complaint_id": "complaint-123",
            }

            save_node(state)
            save_node(state)

        with file_path.open("r", encoding="utf-8") as file:
            saved = json.load(file)

        assert len(saved) == 1

        print("Duplicate complaint ID test passed.")


if __name__ == "__main__":
    test_save_complaint()
    test_save_preserves_existing_complaints()
    test_same_id_does_not_duplicate()

    print("All save tests passed.")