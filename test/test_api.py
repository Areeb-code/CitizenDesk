"""Small API smoke tests for the CitizenDesk UI bridge.

Run from the CitizenDesk project root with: python -m pytest test/test_api.py -q
"""

import json
import sys
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app import api

client = TestClient(api.app)


def test_health_reports_local_service():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["storage"] == "JSON"


def test_dashboard_reads_json_files(tmp_path, monkeypatch):
    complaints_file = tmp_path / "complaints.json"
    contacts_file = tmp_path / "contacts.json"
    complaints_file.write_text(
        json.dumps([
            {
                "complaint_id": "case-1",
                "review": {"passed": True},
                "created_at": "2026-10-01T10:00:00+00:00",
            },
            {
                "complaint_id": "case-2",
                "status": "manual_review",
                "review": {"passed": False},
                "created_at": "2026-10-02T10:00:00+00:00",
            },
        ]),
        encoding="utf-8",
    )
    contacts_file.write_text(json.dumps([{"type": "email", "value": "help@example.gov.pk"}]), encoding="utf-8")
    monkeypatch.setattr(api, "COMPLAINTS_FILE", complaints_file)
    monkeypatch.setattr(api, "CONTACTS_FILE", contacts_file)

    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["total_complaints"] == 2
    assert data["reviewed_complaints"] == 1
    assert data["needs_attention"] == 1
    assert data["contact_candidates"] == 1


def test_workflow_streams_graph_updates(monkeypatch):
    class FakeGraph:
        def stream(self, initial_state, stream_mode):
            assert stream_mode == "values"
            updated = dict(initial_state)
            updated["facts"] = {"issue": "A streetlight is not working"}
            updated["authority"] = "Local authority (test candidate)"
            updated["status"] = "saved"
            updated["saved_file"] = "data/complaints.json"
            updated["log"] = ["Intake completed.", "Complaint saved."]
            yield updated

    monkeypatch.setitem(sys.modules, "app.graph", SimpleNamespace(graph=FakeGraph()))
    response = client.post(
        "/api/complaints/run",
        json={
            "complaint": "A streetlight is not working on Main Road.",
            "language": "English",
            "complaint_id": "case-test",
        },
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    assert '"type": "started"' in response.text
    assert '"type": "snapshot"' in response.text
    assert '"type": "complete"' in response.text
    assert '"complaint_id": "case-test"' in response.text


def test_frontend_files_are_served():
    home = client.get("/")
    script = client.get("/assets/app.js")
    assert home.status_code == 200
    assert "CitizenDesk" in home.text
    assert script.status_code == 200
    assert "runWorkflow" in script.text
