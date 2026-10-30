"""Regression tests for automatic intake, Ollama diagnostics, and contact deletion."""

import importlib
import json
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient


# Keep the node tests runnable in a minimal test environment. In the actual
# CitizenDesk venv, langchain-ollama is installed and this stub is not used.
try:
    import langchain_ollama  # noqa: F401
except ModuleNotFoundError:
    class _UnusedChatOllama:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("This test must mock get_json_model before constructing ChatOllama")

    sys.modules["langchain_ollama"] = SimpleNamespace(ChatOllama=_UnusedChatOllama)

from app.nodes import intake as intake_module
from app.nodes.feedback import feedback_node
from app import api

client = TestClient(api.app)


def _model_with_response(text):
    model = Mock()
    model.invoke.return_value = SimpleNamespace(content=text)
    return model


def test_intake_detects_language_automatically(monkeypatch):
    model = _model_with_response(json.dumps({
        "issue": "Garbage is accumulating",
        "category": "waste",
        "country": "Pakistan",
        "city": "Lahore",
        "location": "Johar Town",
        "duration": "three weeks",
        "impact": "Residents are affected by the smell",
        "language": "Roman Urdu",
    }))
    monkeypatch.setattr(intake_module, "get_json_model", lambda: model)

    result = intake_module.intake_node({
        "complaint": "Mere ilaqay mein kachra teen hafton se jama ho raha hai. Main Johar Town Lahore mein rehta hoon. Badboo ki wajah se log pareshan hain.",
        "language": "auto",
        "feedback_answers": {},
    })

    assert result["status"] == "running"
    assert result["language"] == "Roman Urdu"
    assert result["facts"]["language"] == "Roman Urdu"
    assert result["missing"] == []


def test_intake_reprocesses_original_complaint_with_free_text_clarification(monkeypatch):
    model = _model_with_response(json.dumps({
        "problem": "Broken streetlights",
        "category": "public lighting",
        "country": "Pakistan",
        "city_name": "Lahore",
        "address": "Street 5, Model Town",
        "how_long": "about ten days",
        "effects": "Children cannot see safely at night",
        "detected_language": "English",
    }))
    monkeypatch.setattr(intake_module, "get_json_model", lambda: model)

    result = intake_module.intake_node({
        "complaint": "Streetlights are not working in our area.",
        "language": "auto",
        "feedback_answers": {"clarification": "It is Street 5, Model Town, Lahore, Pakistan, for about ten days. Children cannot see safely at night."},
    })

    prompt = model.invoke.call_args.args[0]
    assert "Additional details supplied by the citizen" in prompt
    assert "Street 5, Model Town" in prompt
    assert result["status"] == "running"
    assert result["facts"]["city"] == "Lahore"
    assert result["facts"]["location"] == "Street 5, Model Town"
    assert result["facts"]["duration"] == "about ten days"


def test_intake_stops_cleanly_when_ollama_connection_is_refused(monkeypatch):
    model = Mock()
    model.invoke.side_effect = RuntimeError(
        "ConnectError: [WinError 10061] No connection could be made because the target machine actively refused it"
    )
    monkeypatch.setattr(intake_module, "get_json_model", lambda: model)

    result = intake_module.intake_node({"complaint": "There is a drainage problem on our street.", "language": "auto"})

    assert result["status"] == "service_unavailable"
    assert result["missing"] == []
    assert "Ollama" in result["error_message"]
    assert not result["questions"]


def test_feedback_keeps_paragraph_clarification_out_of_single_fact_fields():
    clarification = "This is in Model Town Lahore and has continued for ten days."
    result = feedback_node({
        "facts": {"issue": "streetlights not working"},
        "missing": ["city", "location", "duration"],
        "feedback_answers": {"clarification": clarification},
    })

    assert result["facts"] == {"issue": "streetlights not working"}
    assert result["missing"] == ["city", "location", "duration"]
    assert any("fresh context-aware intake pass" in line for line in result["log"])


def test_health_reports_ollama_readiness(monkeypatch):
    monkeypatch.setattr(api, "_ollama_status", lambda: {
        "online": True,
        "model_available": True,
        "model": "gemma3:1b",
        "base_url": "http://localhost:11434",
        "error": "",
    })
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["model_ready"] is True


def test_health_reports_offline_ollama_without_marking_api_offline(monkeypatch):
    monkeypatch.setattr(api, "_ollama_status", lambda: {
        "online": False,
        "model_available": False,
        "model": "gemma3:1b",
        "base_url": "http://localhost:11434",
        "error": "Connection refused",
    })
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["model_ready"] is False
    assert response.json()["ollama"]["online"] is False


def test_delete_selected_contacts_preserves_unselected_records(tmp_path, monkeypatch):
    target = tmp_path / "contacts.json"
    records = [
        {"type": "email", "value": "one@example.gov.pk", "source_url": "https://one.gov.pk/contact"},
        {"type": "phone", "value": "+92 300 0000000", "source_url": "https://two.gov.pk/contact"},
    ]
    target.write_text(json.dumps(records), encoding="utf-8")
    monkeypatch.setattr(api, "CONTACTS_FILE", target)

    listed = client.get("/api/contacts").json()["items"]
    response = client.post("/api/contacts/delete", json={"contact_ids": [listed[0]["contact_id"]]})

    assert response.status_code == 200
    assert response.json()["deleted"] == 1
    remaining = json.loads(target.read_text(encoding="utf-8"))
    assert len(remaining) == 1
    assert remaining[0]["value"] == "+92 300 0000000"


def test_delete_all_requires_exact_typed_confirmation(tmp_path, monkeypatch):
    target = tmp_path / "contacts.json"
    target.write_text(json.dumps([{"type": "email", "value": "one@example.gov.pk"}]), encoding="utf-8")
    monkeypatch.setattr(api, "CONTACTS_FILE", target)

    rejected = client.request("DELETE", "/api/contacts", json={"confirmation": "delete all"})
    assert rejected.status_code == 400
    assert len(json.loads(target.read_text(encoding="utf-8"))) == 1

    accepted = client.request("DELETE", "/api/contacts", json={"confirmation": "DELETE ALL CONTACTS"})
    assert accepted.status_code == 200
    assert accepted.json()["deleted"] == 1
    assert json.loads(target.read_text(encoding="utf-8")) == []


def test_delete_selection_can_distinguish_identical_duplicate_entries(tmp_path, monkeypatch):
    target = tmp_path / "contacts.json"
    duplicate = {"type": "email", "value": "same@example.gov.pk", "source_url": "https://example.gov.pk/contact"}
    target.write_text(json.dumps([duplicate, duplicate]), encoding="utf-8")
    monkeypatch.setattr(api, "CONTACTS_FILE", target)

    listed = client.get("/api/contacts").json()["items"]
    assert listed[0]["contact_id"] != listed[1]["contact_id"]
    response = client.post("/api/contacts/delete", json={"contact_ids": [listed[0]["contact_id"]]})
    assert response.status_code == 200
    assert len(json.loads(target.read_text(encoding="utf-8"))) == 1
