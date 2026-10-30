from app.tools.extract import extract_contacts


def test_extract_email_and_phone():
    results = [
        {
            "title": "Department Contact",
            "url": "https://example.gov.pk/contact",
            "content": (
                "Contact us at contact@example.gov.pk. "
                "Phone: +92 42 12345678."
            ),
        }
    ]

    contacts = extract_contacts(results)

    emails = [
        item for item in contacts
        if item["type"] == "email"
    ]
    phones = [
        item for item in contacts
        if item["type"] == "phone"
    ]

    assert any(
        item["value"] == "contact@example.gov.pk"
        for item in emails
    )
    assert any(
        "12345678" in item["value"]
        for item in phones
    )

    for item in contacts:
        assert item["source_url"]
        assert item["source_title"]
        assert item["evidence"]

    print("Email and phone extraction test passed.")


def test_extract_contact_page():
    results = [
        {
            "title": "Complaint Form",
            "url": "https://example.gov.pk/complaint",
            "content": "Submit complaint using the online complaint form.",
        }
    ]

    contacts = extract_contacts(results)

    assert any(
        item["type"] == "form"
        and item["value"] == "https://example.gov.pk/complaint"
        for item in contacts
    )

    print("Contact page extraction test passed.")


def test_skip_invalid_source():
    results = [
        {
            "title": "Contact",
            "url": "not-a-valid-url",
            "content": "Email: contact@example.gov.pk",
        }
    ]

    assert extract_contacts(results) == []

    print("Invalid source URL test passed.")


def test_duplicate_removal():
    result = {
        "title": "Contact",
        "url": "https://example.gov.pk/contact",
        "content": "Email: contact@example.gov.pk",
    }

    contacts = extract_contacts([result, result])

    email_contacts = [
        item for item in contacts
        if item["type"] == "email"
    ]

    assert len(email_contacts) == 1

    print("Duplicate removal test passed.")


if __name__ == "__main__":
    test_extract_email_and_phone()
    test_extract_contact_page()
    test_skip_invalid_source()
    test_duplicate_removal()

    print("All extraction tests passed.")