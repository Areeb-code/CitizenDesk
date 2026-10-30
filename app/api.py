"""Local FastAPI bridge for CitizenDesk, Ollama model settings and JSON storage."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import urllib.error
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import config
from app.nodes.save import COMPLAINTS_FILE
from app.tools.contract import CONTACTS_FILE

logger = logging.getLogger("citizendesk.api")
FRONTEND_DIR = config.ROOT / "frontend"
OLLAMA_TIMEOUT_SECONDS = 3

app = FastAPI(
    title="CitizenDesk",
    description="A local-first civic complaint research and drafting workspace.",
    version="1.2.0",
)


class ComplaintRunRequest(BaseModel):
    complaint: str = Field(min_length=8, max_length=12000)
    # Language is detected from the complaint; this remains for older clients.
    language: str = Field(default="auto", min_length=2, max_length=40)
    complaint_id: str | None = Field(default=None, max_length=80)
    answers: dict[str, str] = Field(default_factory=dict)


class ContactDeleteRequest(BaseModel):
    contact_ids: list[str] = Field(min_length=1, max_length=500)


class DeleteAllContactsRequest(BaseModel):
    confirmation: str


class ModelSelectionRequest(BaseModel):
    model_name: str = Field(min_length=1, max_length=120)


class ModelDirectoryRequest(BaseModel):
    path: str = Field(min_length=1, max_length=1000)


class ImportGGUFRequest(BaseModel):
    file_path: str = Field(min_length=1, max_length=2000)
    model_name: str = Field(min_length=1, max_length=64)


def _read_json_list(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        logger.exception("Invalid JSON in %s", path)
        raise HTTPException(status_code=500, detail=f"Stored JSON is invalid: {path.name}") from error
    if not isinstance(data, list):
        raise HTTPException(status_code=500, detail=f"Expected a JSON list in {path.name}")
    return [item for item in data if isinstance(item, dict)]


def _write_json_list(path: Path, data: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
        file.write("\n")
    temporary_path.replace(path)


def _contact_id(contact: dict[str, Any], index: int = 0) -> str:
    stable_json = json.dumps(contact, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(f"{index}:{stable_json}".encode("utf-8")).hexdigest()[:20]


def _contact_with_id(contact: dict[str, Any], index: int) -> dict[str, Any]:
    return {**contact, "contact_id": _contact_id(contact, index)}


def _ollama_tags() -> tuple[list[dict[str, Any]], str | None]:
    """Read models installed in Ollama without loading any model into memory."""
    base_url = str(config.OLLAMA_BASE_URL).rstrip("/")
    request = urllib.request.Request(
        f"{base_url}/api/tags",
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
        raw_models = payload.get("models", []) if isinstance(payload, dict) else []
        models = []
        for item in raw_models:
            if not isinstance(item, dict):
                continue
            details = item.get("details") or {}
            models.append({
                "name": str(item.get("name") or item.get("model") or ""),
                "size": int(item.get("size") or 0),
                "modified_at": item.get("modified_at") or "",
                "family": details.get("family") or "",
                "parameter_size": details.get("parameter_size") or "",
                "quantization_level": details.get("quantization_level") or "",
            })
        return models, None
    except (OSError, urllib.error.URLError, TimeoutError, ValueError) as error:
        return [], str(error)


def _ollama_status() -> dict[str, Any]:
    base_url = str(config.OLLAMA_BASE_URL).rstrip("/")
    models, error = _ollama_tags()
    current_model = str(config.MODEL_NAME)
    available_names = {item["name"] for item in models}
    selected_available = current_model in available_names

    if error:
        connection_refused = any(
            marker in error.lower()
            for marker in ("10061", "actively refused", "connection refused", "connecterror")
        )
        friendly_error = (
            f"Ollama connection refused at {base_url}. Open the Ollama desktop app. "
            "If you use `ollama serve`, run it only when Ollama is not already running."
            if connection_refused else
            f"Cannot reach Ollama at {base_url}: {error}"
        )
        return {
            "online": False,
            "model_available": False,
            "model": current_model,
            "base_url": base_url,
            "models": [],
            "error": friendly_error,
        }

    return {
        "online": True,
        "model_available": selected_available,
        "model": current_model,
        "base_url": base_url,
        "models": models,
        "error": "" if selected_available else f"Ollama is running, but '{current_model}' is not installed.",
    }


def _write_model_to_env(model_name: str) -> None:
    """Persist model selection without removing other .env settings."""
    env_path = config.ROOT / ".env"
    original = env_path.read_text(encoding="utf-8") if env_path.exists() else ""
    line = f"MODEL_NAME={model_name}"
    pattern = re.compile(r"^\s*MODEL_NAME\s*=.*$", flags=re.MULTILINE)
    if pattern.search(original):
        updated = pattern.sub(line, original, count=1)
    else:
        separator = "" if not original or original.endswith(("\n", "\r")) else "\n"
        updated = original + separator + line + "\n"
    temporary = env_path.with_suffix(".env.tmp")
    temporary.write_text(updated, encoding="utf-8")
    temporary.replace(env_path)
    settings_path = config.DATA_DIR / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_temp = settings_path.with_suffix(".json.tmp")
    settings_temp.write_text(json.dumps({"model_name": model_name}, indent=2) + "\n", encoding="utf-8")
    settings_temp.replace(settings_path)
    os.environ["MODEL_NAME"] = model_name
    config.MODEL_NAME = model_name


def _public_state(state: dict[str, Any]) -> dict[str, Any]:
    allowed = {
        "complaint_id", "complaint", "language", "facts", "missing", "questions",
        "authority", "research_results", "channels", "attempt", "draft", "review",
        "revision", "status", "saved_file", "log", "error_message",
    }
    return {key: state.get(key) for key in allowed if key in state}


def _sse(payload: dict[str, Any]) -> str:
    return "data: " + json.dumps(payload, ensure_ascii=False, default=str) + "\n\n"


def _initial_state(request: ComplaintRunRequest) -> dict[str, Any]:
    answers = {
        str(key): str(value).strip()
        for key, value in request.answers.items()
        if str(value).strip()
    }
    return {
        "complaint_id": request.complaint_id or uuid.uuid4().hex,
        "complaint": request.complaint.strip(),
        "language": "auto",
        "facts": {},
        "missing": [],
        "questions": [],
        "feedback_answers": answers,
        "authority": "",
        "research_results": [],
        "channels": [],
        "failed_channels": [],
        "research_mode": "normal",
        "attempt": 0,
        "draft": [],
        "review": {},
        "revision": 0,
        "status": "running",
        "saved_file": "",
        "log": [],
        "error_message": "",
    }


def _load_saved_model_selection() -> None:
    settings_path = config.DATA_DIR / "settings.json"
    if not settings_path.exists():
        return
    try:
        saved = json.loads(settings_path.read_text(encoding="utf-8"))
        selected = str(saved.get("model_name") or "").strip() if isinstance(saved, dict) else ""
        if selected:
            config.MODEL_NAME = selected
    except (OSError, json.JSONDecodeError, AttributeError):
        logger.warning("Could not read saved model selection from %s", settings_path)


_load_saved_model_selection()


@app.get("/api/health")
@app.get("/health")
def health() -> dict[str, Any]:
    ollama = _ollama_status()
    return {
        "ok": True,
        "service": "CitizenDesk",
        "storage": "JSON",
        "model": config.MODEL_NAME,
        "ollama": ollama,
        "model_ready": ollama["online"] and ollama["model_available"],
    }


@app.get("/api/settings/models")
def list_available_models() -> dict[str, Any]:
    """List models Ollama itself reports as installed."""
    ollama = _ollama_status()
    return {
        "online": ollama["online"],
        "base_url": ollama["base_url"],
        "current_model": config.MODEL_NAME,
        "models": ollama["models"],
        "error": ollama["error"],
    }


@app.post("/api/settings/model")
def select_model(request: ModelSelectionRequest) -> dict[str, Any]:
    model_name = request.model_name.strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,119}", model_name):
        raise HTTPException(status_code=400, detail="Choose a model from the installed-model list.")
    models, error = _ollama_tags()
    if error:
        raise HTTPException(
            status_code=503,
            detail="Ollama is not reachable. Open the Ollama desktop app, then try again. "
                   "Do not start a second server if port 11434 is already in use.",
        )
    if model_name not in {item["name"] for item in models}:
        raise HTTPException(status_code=404, detail=f"'{model_name}' is not currently installed in Ollama.")
    _write_model_to_env(model_name)
    return {"selected_model": model_name, "models": models, "message": "Model selection saved to .env."}


@app.post("/api/settings/browse-directory")
def browse_model_directory() -> dict[str, str]:
    """Open the native folder picker on the local Windows machine."""
    if os.name != "nt":
        raise HTTPException(status_code=501, detail="Native folder browsing is available on Windows only. Enter the folder path manually.")
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(title="Choose a folder containing local GGUF model files")
        root.destroy()
        return {"path": selected or ""}
    except Exception as error:
        logger.exception("Native model folder picker failed")
        raise HTTPException(status_code=500, detail=f"Could not open the Windows folder picker: {type(error).__name__}. Enter the path manually.") from error


@app.post("/api/settings/scan-directory")
def scan_model_directory(request: ModelDirectoryRequest) -> dict[str, Any]:
    """Find standalone GGUF files. Ollama-managed models are listed separately via /api/tags."""
    directory = Path(request.path.strip().strip('"')).expanduser()
    if not directory.exists() or not directory.is_dir():
        raise HTTPException(status_code=404, detail="That folder does not exist or is not a directory.")
    try:
        candidates = []
        # Stop after 101 matches so scanning a large model cache stays bounded.
        for root, _directories, filenames in os.walk(directory):
            for filename in filenames:
                if Path(filename).suffix.lower() == ".gguf":
                    candidates.append(Path(root) / filename)
                    if len(candidates) > 100:
                        break
            if len(candidates) > 100:
                break
        candidates.sort(key=lambda path: str(path).lower())
    except OSError as error:
        raise HTTPException(status_code=400, detail=f"Could not read that folder: {error}") from error

    items = []
    for file_path in candidates[:100]:
        try:
            stat = file_path.stat()
        except OSError:
            continue
        items.append({
            "name": file_path.name,
            "path": str(file_path.resolve()),
            "size": stat.st_size,
            "modified_at": stat.st_mtime,
        })
    return {
        "directory": str(directory.resolve()),
        "count": len(items),
        "truncated": len(candidates) > 100,
        "items": items,
        "note": "Ollama's own model store is managed internally and will appear in Installed Ollama models above. This scan lists loose .gguf files only.",
    }


@app.post("/api/settings/import-gguf")
def import_gguf_model(request: ImportGGUFRequest) -> dict[str, Any]:
    """Register a selected GGUF file with Ollama using a Modelfile, then select it."""
    model_name = request.model_name.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]{1,63}", model_name):
        raise HTTPException(status_code=400, detail="Model name must use 2–64 lowercase letters, numbers, dots, underscores, or hyphens.")

    file_path = Path(request.file_path.strip().strip('"')).expanduser()
    if not file_path.exists() or not file_path.is_file() or file_path.suffix.lower() != ".gguf":
        raise HTTPException(status_code=404, detail="The selected .gguf file could not be found.")

    ollama_executable = shutil.which("ollama")
    if not ollama_executable:
        raise HTTPException(status_code=503, detail="The 'ollama' command was not found. Install/open Ollama and ensure its command is available in PATH.")

    modelfile_dir = config.DATA_DIR / "model_imports"
    modelfile_dir.mkdir(parents=True, exist_ok=True)
    modelfile_path = modelfile_dir / f"{model_name}.Modelfile"
    # Ollama's documented GGUF import method uses a Modelfile FROM path.
    quoted_path = file_path.resolve().as_posix().replace('"', '\\"')
    modelfile_path.write_text(f'FROM "{quoted_path}"\n', encoding="utf-8")

    try:
        result = subprocess.run(
            [ollama_executable, "create", model_name, "-f", str(modelfile_path)],
            cwd=str(modelfile_dir),
            capture_output=True,
            text=True,
            timeout=1200,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        raise HTTPException(status_code=504, detail="Ollama model import exceeded 20 minutes. Check the Ollama terminal and try again.") from error
    except OSError as error:
        raise HTTPException(status_code=500, detail=f"Could not start Ollama model import: {error}") from error

    output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"Ollama could not import this GGUF file. {output[-3000:]}")

    _write_model_to_env(model_name)
    models, list_error = _ollama_tags()
    return {
        "imported_model": model_name,
        "selected_model": model_name,
        "models": models,
        "output": output[-3000:],
        "warning": "Importing does not guarantee that this model will fit in available RAM. Start with a small quantized model and test it before running a full complaint.",
        "ollama_error": list_error or "",
    }


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    complaints = _read_json_list(COMPLAINTS_FILE)
    contacts = _read_json_list(CONTACTS_FILE)
    completed = sum(1 for item in complaints if (item.get("review") or {}).get("passed") is True)
    attention = sum(
        1 for item in complaints
        if str(item.get("status") or "").lower() in {
            "needs_info", "manual_review", "save_failed", "service_unavailable", "extraction_failed"
        } or (item.get("review") or {}).get("passed") is False
    )
    recent = sorted(complaints, key=lambda item: str(item.get("created_at") or ""), reverse=True)[:6]
    return {
        "total_complaints": len(complaints),
        "reviewed_complaints": completed,
        "needs_attention": attention,
        "contact_candidates": len(contacts),
        "recent_complaints": recent,
    }


@app.get("/api/complaints")
@app.get("/history")
def list_complaints() -> dict[str, Any]:
    complaints = _read_json_list(COMPLAINTS_FILE)
    complaints.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
    return {"items": complaints}


@app.get("/api/complaints/{complaint_id}")
def get_complaint(complaint_id: str) -> dict[str, Any]:
    for complaint in _read_json_list(COMPLAINTS_FILE):
        if str(complaint.get("complaint_id")) == complaint_id:
            return complaint
    raise HTTPException(status_code=404, detail="Complaint not found")


@app.get("/api/contacts")
def list_contacts() -> dict[str, Any]:
    contacts = _read_json_list(CONTACTS_FILE)
    return {"items": [_contact_with_id(item, index) for index, item in enumerate(contacts)]}


@app.post("/api/contacts/delete")
def delete_selected_contacts(request: ContactDeleteRequest) -> dict[str, Any]:
    wanted = set(request.contact_ids)
    contacts = _read_json_list(CONTACTS_FILE)
    kept = [item for index, item in enumerate(contacts) if _contact_id(item, index) not in wanted]
    removed = len(contacts) - len(kept)
    if removed:
        _write_json_list(CONTACTS_FILE, kept)
    return {"deleted": removed, "remaining": len(kept)}


@app.delete("/api/contacts")
def delete_all_contacts(request: DeleteAllContactsRequest) -> dict[str, Any]:
    if request.confirmation.strip() != "DELETE ALL CONTACTS":
        raise HTTPException(status_code=400, detail="Type DELETE ALL CONTACTS exactly to permanently clear the contact library.")
    contacts = _read_json_list(CONTACTS_FILE)
    _write_json_list(CONTACTS_FILE, [])
    return {"deleted": len(contacts), "remaining": 0}


@app.post("/api/complaints/run")
@app.post("/generate-complaint")
def run_complaint(request: ComplaintRunRequest) -> StreamingResponse:
    initial_state = _initial_state(request)

    def event_stream():
        yield _sse({"type": "started", "complaint_id": initial_state["complaint_id"], "message": "CitizenDesk workflow started."})
        last_state: dict[str, Any] = initial_state
        try:
            from app.graph import graph as citizen_graph
            for snapshot in citizen_graph.stream(initial_state, stream_mode="values"):
                last_state = snapshot
                yield _sse({"type": "snapshot", "state": _public_state(snapshot)})
            yield _sse({"type": "complete", "state": _public_state(last_state)})
        except Exception as error:  # pragma: no cover - depends on optional local services
            logger.exception("CitizenDesk workflow failed")
            yield _sse({
                "type": "error",
                "message": "The workflow stopped unexpectedly. Check the CitizenDesk terminal for details.",
                "error_type": type(error).__name__,
                "state": _public_state(last_state),
            })

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.get("/", include_in_schema=False)
def application_home() -> FileResponse:
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="Frontend files are missing")
    return FileResponse(index_file)


if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")
