from unittest.mock import Mock, patch

from app.nodes.authority import authority_node


def test_authority_node():
    state = {
        "facts": {
            "issue": "stray dogs roaming in the neighbourhood",
            "category": "stray animals",
            "country": "Pakistan",
            "city": "Lahore",
            "location": "Model Town Lahore",
        },
        "status": "running",
        "log": [],
    }

    mock_response = Mock()
    mock_response.content = (
        '{"authority": "Relevant local government authority", '
        '"reasoning": "It handles local public issues", '
        '"confidence": 0.8, '
        '"needs_research": true}'
    )

    with patch(
        "app.nodes.authority.get_json_model"
    ) as mock_get_model:
        mock_model = Mock()
        mock_model.invoke.return_value = mock_response
        mock_get_model.return_value = mock_model

        result = authority_node(state)

    assert result["authority"] == (
        "Relevant local government authority"
    )
    assert result["status"] == "running"
    assert len(result["log"]) > 0
    mock_model.invoke.assert_called_once()

    print("Valid authority response test passed.")


def test_missing_facts():
    state = {
        "facts": {
            "country": "Pakistan",
        },
        "log": [],
    }

    result = authority_node(state)

    assert result["authority"] == ""
    assert result["status"] == "needs_info"

    print("Missing complaint information test passed.")


def test_invalid_json():
    state = {
        "facts": {
            "issue": "stray dogs",
            "country": "Pakistan",
        },
        "log": [],
    }

    mock_response = Mock()
    mock_response.content = "This is not valid JSON."

    with patch(
        "app.nodes.authority.get_json_model"
    ) as mock_get_model:
        mock_model = Mock()
        mock_model.invoke.return_value = mock_response
        mock_get_model.return_value = mock_model

        result = authority_node(state)

    assert result["authority"] == ""
    assert result["status"] == "running"
    assert any(
        "invalid JSON" in entry
        for entry in result["log"]
    )

    print("Invalid JSON test passed.")


if __name__ == "__main__":
    test_authority_node()
    test_missing_facts()
    test_invalid_json()
    print("All authority tests passed.")