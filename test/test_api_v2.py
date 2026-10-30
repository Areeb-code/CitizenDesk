import json
from types import SimpleNamespace
from fastapi.testclient import TestClient

from app import api

client = TestClient(api.app)


def test_model_settings_list_installed_ollama_models(monkeypatch):
    monkeypatch.setattr(api, "_ollama_tags", lambda: ([{"name": "gemma3:1b", "size": 900}], None))
    response = client.get("/api/settings/models")
    assert response.status_code == 200
    assert response.json()["models"][0]["name"] == "gemma3:1b"


def test_select_model_persists_without_removing_existing_env_values(tmp_path, monkeypatch):
    monkeypatch.setattr(api.config, "ROOT", tmp_path)
    monkeypatch.setattr(api.config, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(api.config, "MODEL_NAME", "old-model")
    monkeypatch.setattr(api, "_ollama_tags", lambda: ([{"name": "gemma3:1b"}, {"name": "llama3.2:3b"}], None))
    (tmp_path / ".env").write_text("TAVILY_API_KEY=test-key\nMODEL_NAME=old-model\n", encoding="utf-8")

    response = client.post("/api/settings/model", json={"model_name": "llama3.2:3b"})
    assert response.status_code == 200
    assert api.config.MODEL_NAME == "llama3.2:3b"
    env_text = (tmp_path / ".env").read_text(encoding="utf-8")
    assert "TAVILY_API_KEY=test-key" in env_text
    assert "MODEL_NAME=llama3.2:3b" in env_text
    settings = json.loads((tmp_path / "data" / "settings.json").read_text(encoding="utf-8"))
    assert settings["model_name"] == "llama3.2:3b"


def test_select_model_rejects_not_installed_model(monkeypatch):
    monkeypatch.setattr(api, "_ollama_tags", lambda: ([{"name": "gemma3:1b"}], None))
    response = client.post("/api/settings/model", json={"model_name": "missing-model"})
    assert response.status_code == 404


def test_scan_directory_finds_only_gguf_files(tmp_path):
    (tmp_path / "one.gguf").write_bytes(b"gguf")
    (tmp_path / "notes.txt").write_text("not a model", encoding="utf-8")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "two.GGUF").write_bytes(b"gguf2")
    response = client.post("/api/settings/scan-directory", json={"path": str(tmp_path)})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert {item["name"] for item in data["items"]} == {"one.gguf", "two.GGUF"}


def test_scan_directory_rejects_missing_folder():
    response = client.post("/api/settings/scan-directory", json={"path": "this-folder-should-not-exist"})
    assert response.status_code == 404


def test_import_gguf_creates_modelfile_and_selects_model(tmp_path, monkeypatch):
    gguf = tmp_path / "small local model.gguf"
    gguf.write_bytes(b"test model marker")
    monkeypatch.setattr(api.config, "DATA_DIR", tmp_path / "data")
    monkeypatch.setattr(api.config, "ROOT", tmp_path)
    monkeypatch.setattr(api, "_write_model_to_env", lambda name: setattr(api.config, "MODEL_NAME", name))
    monkeypatch.setattr(api.shutil, "which", lambda _: "ollama.exe")
    monkeypatch.setattr(api.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout="success", stderr=""))
    monkeypatch.setattr(api, "_ollama_tags", lambda: ([{"name": "citizendesk-small-local-model"}], None))

    response = client.post("/api/settings/import-gguf", json={"file_path": str(gguf), "model_name": "citizendesk-small-local-model"})
    assert response.status_code == 200
    modelfile = tmp_path / "data" / "model_imports" / "citizendesk-small-local-model.Modelfile"
    assert modelfile.exists()
    assert str(gguf).replace("\\", "/") in modelfile.read_text(encoding="utf-8")
    assert response.json()["selected_model"] == "citizendesk-small-local-model"


def test_delete_selected_contacts_only_removes_selected_entry(tmp_path, monkeypatch):
    contacts_path = tmp_path / "contacts.json"
    records = [
        {"type": "email", "value": "one@example.gov"},
        {"type": "phone", "value": "+1 555 0100"},
    ]
    contacts_path.write_text(json.dumps(records), encoding="utf-8")
    monkeypatch.setattr(api, "CONTACTS_FILE", contacts_path)
    contact_id = api._contact_id(records[0], 0)
    response = client.post("/api/contacts/delete", json={"contact_ids": [contact_id]})
    assert response.status_code == 200
    remaining = json.loads(contacts_path.read_text(encoding="utf-8"))
    assert len(remaining) == 1
    assert remaining[0]["value"] == "+1 555 0100"


def test_delete_all_requires_explicit_phrase(tmp_path, monkeypatch):
    contacts_path = tmp_path / "contacts.json"
    contacts_path.write_text(json.dumps([{"type": "email", "value": "one@example.gov"}]), encoding="utf-8")
    monkeypatch.setattr(api, "CONTACTS_FILE", contacts_path)
    response = client.request("DELETE", "/api/contacts", json={"confirmation": "wrong"})
    assert response.status_code == 400
    assert len(json.loads(contacts_path.read_text(encoding="utf-8"))) == 1
    response = client.request("DELETE", "/api/contacts", json={"confirmation": "DELETE ALL CONTACTS"})
    assert response.status_code == 200
    assert json.loads(contacts_path.read_text(encoding="utf-8")) == []
