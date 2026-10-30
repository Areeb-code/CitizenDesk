from app.nodes import save as save_module


def test_save_node_persists_research_evidence(tmp_path, monkeypatch):
    target = tmp_path / "complaints.json"
    monkeypatch.setattr(save_module, "COMPLAINTS_FILE", target)
    result = save_module.save_node({
        "complaint_id": "case-1",
        "complaint": "Streetlight outage",
        "language": "English",
        "facts": {"issue": "Streetlight outage"},
        "authority": "Test municipal office",
        "research_results": [{"title": "Office contact", "url": "https://example.gov.pk/contact"}],
        "channels": [{"type": "email", "value": "office@example.gov.pk", "verification_status": "candidate_passed"}],
        "draft": [{"format": "email", "text": "Subject: Streetlight outage"}],
        "review": {"score": 1.0, "passed": True},
        "status": "running",
        "attempt": 1,
    })

    assert result["status"] == "saved"
    import json
    saved = json.loads(target.read_text(encoding="utf-8"))[0]
    assert saved["channels"][0]["value"] == "office@example.gov.pk"
    assert saved["research_results"][0]["title"] == "Office contact"
