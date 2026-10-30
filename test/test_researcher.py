from unittest.mock import patch
from app.tools.contract import add_contacts
from app.nodes.researcher import researcher_node


def test_researcher_extracts_contacts():
    state = {
        "facts": {
            "issue": "stray dogs",
            "category": "stray animals",
            "country": "Pakistan",
            "city": "Lahore",
        },
        "authority": "Relevant local government authority",
        "attempt": 0,
        "research_mode": "normal",
        "log": [],
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
        result = researcher_node(state)

    assert result["attempt"] == 1
    assert len(result["research_results"]) == 1
    print("\n--- RESEARCHER DEBUG ---")
    print("STATUS:", result.get("status"))
    print("RESEARCH RESULTS:", result.get("research_results"))
    print("CHANNELS:", result.get("channels"))
    print("LOG:", result.get("log"))
    print("--- END DEBUG ---")

    assert len(result["channels"]) >= 1
    print("STATUS:", result.get("status"))
    print("RESEARCH RESULTS:", result.get("research_results"))
    print("CHANNELS:", result.get("channels"))
    print("LOG:", result.get("log"))    

    assert any(
        channel["type"] == "email"
        and channel["value"] == "contact@example.gov.pk"
        for channel in result["channels"]
    )

    assert result["status"] == "running"

    print("Researcher contact extraction test passed.")


if __name__ == "__main__":
    test_researcher_extracts_contacts()
    print("All researcher tests passed.")
