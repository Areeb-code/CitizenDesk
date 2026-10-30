from app.nodes.verifier import (
    verifier_node,
    _verify_channel,
)


def test_official_candidate():
    channel = {
        "type": "website",
        "value": "https://example.gov.pk/contact",
        "source_url": "https://example.gov.pk/contact",
        "source_title": "Department Contact Page",
        "evidence": "The page lists department contact information.",
    }

    result = _verify_channel(channel)

    assert result["source_appears_official"] is True
    assert result["verification_score"] == 1.0
    assert result["verification_status"] == "candidate_passed"
    assert result["live_contact_tested"] is False

    print("Official-domain candidate test passed.")


def test_missing_contact_value():
    channel = {
        "type": "phone",
        "value": "",
        "source_url": "https://example.gov.pk/contact",
    }

    result = _verify_channel(channel)

    assert result["verification_status"] == "rejected"
    assert result["verification_score"] < 1.0

    print("Missing contact value test passed.")


def test_verifier_node():
    state = {
        "channels": [
            {
                "type": "email",
                "value": "contact@example.gov.pk",
                "source_url": "https://example.gov.pk/contact",
                "source_title": "Contact page",
                "evidence": "Email listed on the page.",
            }
        ],
        "log": [],
    }

    result = verifier_node(state)

    assert len(result["channels"]) == 1
    assert "verification_status" in result["channels"][0]
    assert result["status"] == "running"
    assert len(result["log"]) > 0

    print("Verifier node test passed.")


def test_empty_channels():
    result = verifier_node({"channels": [], "log": []})

    assert result["channels"] == []
    assert result["status"] == "running"

    print("Empty channels test passed.")


if __name__ == "__main__":
    test_official_candidate()
    test_missing_contact_value()
    test_verifier_node()
    test_empty_channels()

    print("All verifier tests passed.")