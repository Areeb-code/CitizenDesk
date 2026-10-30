from app.nodes.feedback import feedback_node


def test_missing_fields_create_one_natural_language_question():
    result = feedback_node({
        "facts": {"issue": "blocked drain"},
        "missing": ["location"],
        "feedback_answers": {},
    })
    assert result["status"] == "needs_info"
    assert len(result["questions"]) == 1
    assert result["questions"][0]["field"] == "clarification"
    assert "city" in result["questions"][0]["question"]


def test_clarification_is_not_copied_into_a_single_fact_field():
    original = {"issue": "blocked drain"}
    result = feedback_node({
        "facts": original,
        "missing": ["location"],
        "feedback_answers": {"clarification": "It is in Johar Town, Lahore."},
    })
    assert result["facts"] == original
    assert "location" in result["missing"]
    assert "re-read" in result["questions"][0]["question"].lower()


def test_no_missing_information_continues():
    result = feedback_node({"facts": {"issue": "noise"}, "missing": [], "feedback_answers": {}})
    assert result["status"] == "running"
    assert result["missing"] == []
    assert result["questions"] == []


def test_original_facts_are_not_mutated():
    original = {"issue": "noise"}
    feedback_node({"facts": original, "missing": ["location"], "feedback_answers": {}})
    assert original == {"issue": "noise"}
