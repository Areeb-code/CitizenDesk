from unittest.mock import patch

from app.nodes.researcher import researcher_node
from app.nodes.verifier import verifier_node


def test_researcher_to_verifier_pipeline():
    state = {
        "facts": {
            "issue": "stray dogs roaming in the neighbourhood",
            "category": "stray animals",
            "country": "Pakistan",
            "city": "Lahore",
            "location": "Model Town Lahore",
        },
        "authority": "Relevant local government authority",
        "attempt": 0,
        "research_mode": "normal",
        "channels": [],
        "research_results": [],
        "log": [],
        "status": "running",
    }

    mock_results = [
        {
            "title": "Department Contact",
            "url": "https://example.gov.pk/contact",
            "content": (
                "Contact us at contact@example.gov.pk. "
                "For complaints, visit our contact page."
            ),
            "score": 0.9,
        }
    ]

    with patch(
        "app.nodes.researcher.search_web",
        return_value=mock_results,
    ):
        research_result = researcher_node(state)

    assert len(research_result["channels"]) > 0

    # Pass the researcher's extracted candidates to the verifier.
    verifier_input = {
        **state,
        **research_result,
    }

    verification_result = verifier_node(verifier_input)

    assert len(verification_result["channels"]) > 0

    for channel in verification_result["channels"]:
        assert "verification_score" in channel
        assert "verification_status" in channel
        assert "verification_notes" in channel
        assert channel["live_contact_tested"] is False

    print("Researcher-to-verifier pipeline test passed.")
    print(
        "Candidates assessed:",
        len(verification_result["channels"]),
    )


if __name__ == "__main__":
    test_researcher_to_verifier_pipeline()
    print("All pipeline tests passed.")