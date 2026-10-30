from unittest.mock import Mock, patch

from app.nodes.writer import writer_node, _build_call_script


def test_build_call_script():
    facts = {
        "issue": "stray dogs roaming in the neighbourhood",
    }

    summary_data = {
        "summary": (
            "I am calling about stray dogs in Model Town Lahore. "
            "The issue has continued for two weeks."
        ),
        "have_ready": [
            "Exact street and landmark",
            "Photos if available",
            "Your contact details",
        ],
    }

    result = _build_call_script(summary_data, facts)

    assert "stray dogs roaming in the neighbourhood" in result
    assert "Model Town Lahore" in result
    assert "Exact street and landmark" in result
    assert "{summary}" not in result
    assert "{issue}" not in result
    assert "{have_ready}" not in result

    print("Call script template test passed.")


@patch("app.nodes.writer.get_writer_model")
def test_writer_node(mock_get_model):
    model = Mock()

    email_response = Mock()
    email_response.content = (
        "Subject: Stray dogs in Model Town Lahore\n\n"
        "Please investigate the issue reported in Model Town Lahore "
        "and take appropriate action within 7 days.\n\n"
        "[Name]\n[Phone]"
    )

    call_response = Mock()
    call_response.content = (
        '{"summary": "I am calling about stray dogs in Model Town Lahore.", '
        '"have_ready": ["Exact location", "Photos if available"]}'
    )

    model.invoke.side_effect = [
        email_response,
        call_response,
    ]

    mock_get_model.return_value = model

    state = {
        "complaint": "Stray dogs are roaming in Model Town Lahore.",
        "language": "English",
        "facts": {
            "issue": "stray dogs roaming in the neighbourhood",
            "category": "stray animals",
            "country": "Pakistan",
            "city": "Lahore",
            "location": "Model Town Lahore",
            "duration": "two weeks",
            "impact": "residents feel unsafe",
            "language": "English",
        },
        "authority": "Relevant local authority",
        "review": {},
        "revision": 0,
    }

    result = writer_node(state)

    assert len(result["draft"]) == 2
    assert result["draft"][0]["format"] == "email"
    assert result["draft"][1]["format"] == "phone"
    assert result["status"] == "running"
    assert len(result["log"]) > 0
    assert model.invoke.call_count == 2

    print("Writer node test passed.")
    print("Generated drafts:", len(result["draft"]))


if __name__ == "__main__":
    test_build_call_script()
    test_writer_node()
    print("All writer tests passed.")