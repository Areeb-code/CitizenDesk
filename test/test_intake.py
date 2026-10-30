import sys
from types import ModuleType

try:
    import langchain_ollama  # noqa: F401
except ImportError:
    stub = ModuleType("langchain_ollama")
    stub.ChatOllama = object
    sys.modules["langchain_ollama"] = stub

from unittest.mock import Mock, patch

from app.nodes.intake import intake_node, _extract_json_object, _detect_language


def response(content):
    item = Mock()
    item.content = content
    return item


def test_detected_language_is_used_when_language_is_auto():
    model = Mock()
    model.invoke.return_value = response('{"issue":"garbage collecting is missed","category":"waste","country":"Pakistan","city":"Lahore","location":"Model Town","duration":"one week","impact":"residents affected","language":"Roman Urdu"}')
    with patch("app.nodes.intake.get_json_model", return_value=model):
        result = intake_node({"complaint": "Mere ilaqay mein kachra jama hai, Lahore Model Town mein.", "language": "auto"})
    assert result["language"] == "Roman Urdu"
    assert result["facts"]["language"] == "Roman Urdu"
    assert result["missing"] == []


def test_clarification_is_sent_with_original_complaint():
    model = Mock()
    model.invoke.return_value = response('{"issue":"blocked drain","category":"drainage","country":"Pakistan","city":"Lahore","location":"Johar Town, Street 4","duration":"three days","impact":"water is overflowing","language":"English"}')
    with patch("app.nodes.intake.get_json_model", return_value=model):
        result = intake_node({
            "complaint": "There is a blocked drain.",
            "language": "auto",
            "feedback_answers": {"clarification": "It is in Johar Town, Lahore, Street 4, for three days. Water is overflowing."},
        })
    assert result["facts"]["location"] == "Johar Town, Street 4"
    prompt = model.invoke.call_args.args[0]
    assert "original description" in prompt.lower()
    assert "Johar Town" in prompt


def test_json_with_leading_explanation_is_parsed():
    data = _extract_json_object('Here are the extracted details:\n{"issue":"noise","city":"Lahore"}\nDone.')
    assert data["issue"] == "noise"
    assert data["city"] == "Lahore"


def test_duration_and_impact_are_optional_not_blocking():
    model = Mock()
    model.invoke.return_value = response('{"issue":"streetlight not working","category":"electricity","country":"Pakistan","city":"Lahore","location":"Model Town","duration":"","impact":"","language":"English"}')
    with patch("app.nodes.intake.get_json_model", return_value=model):
        result = intake_node({"complaint": "Streetlight is not working in Model Town, Lahore."})
    assert result["status"] == "running"
    assert result["missing"] == []


def test_invalid_json_retries_then_preserves_original_complaint():
    model = Mock()
    model.invoke.side_effect = [response("not json"), response("still not json")]
    complaint = "There is a waste problem in my street for two weeks."
    with patch("app.nodes.intake.get_json_model", return_value=model):
        result = intake_node({"complaint": complaint, "language": "auto"})
    assert model.invoke.call_count == 2
    assert result["facts"]["issue"] == complaint
    assert result["status"] == "needs_info"
    assert result["questions"][0]["field"] == "clarification"


def test_connection_refused_is_not_reported_as_missing_user_information():
    model = Mock()
    model.invoke.side_effect = ConnectionError("[WinError 10061] No connection could be made because the target machine actively refused it")
    with patch("app.nodes.intake.get_json_model", return_value=model):
        result = intake_node({"complaint": "Stray dogs are gathering near Model Town, Lahore."})
    assert result["status"] == "service_unavailable"
    assert result["missing"] == []
    assert "Ollama" in result["error_message"]
    assert result["facts"]["issue"].startswith("Stray dogs")


def test_language_fallback_recognizes_urdu_script_and_roman_urdu():
    assert _detect_language("میرے علاقے میں پانی نہیں آ رہا") == "Urdu"
    assert _detect_language("Mere ilaqay mein pani nahi aa raha") == "Roman Urdu"


def test_empty_complaint_does_not_call_model():
    with patch("app.nodes.intake.get_json_model") as factory:
        result = intake_node({"complaint": " "})
    factory.assert_not_called()
    assert result["status"] == "needs_info"
    assert result["missing"] == ["issue"]
