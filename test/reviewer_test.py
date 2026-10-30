from app.nodes.reviewer import reviewer_node, review_draft


def test_email_review():
    facts = {
        "location": "Model Town Lahore",
        "duration": "two weeks",
        "impact": "Residents feel unsafe",
    }

    draft = {
        "format": "email",
        "text": (
            "Subject: Stray dogs in Model Town Lahore\n\n"
            "The issue has continued for two weeks and creates "
            "a safety risk for residents. Please investigate "
            "and take action within 7 days.\n\n"
            "Regards,\n[Name]\n[Phone]"
        ),
    }

    result = review_draft(
        draft=draft,
        facts=facts,
        known_numbers=set(),
        english=True,
    )

    assert result["checks"]["Starts with a Subject line"]
    assert result["checks"]["Mentions the location"]
    assert result["checks"]["No invented phone numbers"]
    assert result["checks"]["No unfilled { } placeholders"]

    print("Email review test passed.")
    print("Score:", result["score"])


def test_critical_failure():
    facts = {
        "location": "Model Town Lahore",
    }

    draft = {
        "format": "other",
        "text": (
            "Residents in Model Town Lahore should call "
            "03001234567 for help."
        ),
    }

    result = review_draft(
        draft=draft,
        facts=facts,
        known_numbers=set(),
        english=True,
    )

    assert not result["passed"]
    assert "No invented phone numbers" in result["critical_failures"]

    print("Critical failure test passed.")


def test_reviewer_node():
    state = {
        "facts": {
            "location": "Model Town Lahore",
        },
        "language": "English",
        "channels": [],
        "draft": [
            {
                "format": "other",
                "text": (
                    "Residents in Model Town Lahore need assistance."
                ),
            }
        ],
    }

    result = reviewer_node(state)

    assert "review" in result
    assert len(result["review"]["per_draft"]) == 1
    assert isinstance(result["log"], list)

    print("Reviewer node test passed.")
    print("Overall score:", result["review"]["score"])


if __name__ == "__main__":
    test_email_review()
    test_critical_failure()
    test_reviewer_node()
    print("All reviewer tests passed.")