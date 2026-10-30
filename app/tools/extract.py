import re
from urllib.parse import urlparse


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"(?<!\w)\+?\d[\d\s().-]{5,}\d(?!\w)"
)

CONTACT_KEYWORDS = (
    "contact",
    "complaint",
    "helpline",
    "phone",
    "email",
    "grievance",
    "citizen portal",
    "report an issue",
    "report a problem",
    "feedback",
    "customer service",
)

FORM_KEYWORDS = (
    "complaint form",
    "submit complaint",
    "online complaint",
    "grievance form",
    "citizen portal",
)


def _clean_text(value: object) -> str:
    """Convert a value into clean text."""
    if not isinstance(value, str):
        return ""

    return " ".join(value.split()).strip()


def _valid_email(email: str) -> bool:
    """Check whether an extracted email has a basic valid structure."""
    return bool(EMAIL_PATTERN.fullmatch(email))


def _valid_phone(phone: str) -> bool:
    """Reject phone candidates that are too short or too long."""
    digits = re.sub(r"\D", "", phone)
    return 7 <= len(digits) <= 15


def _is_valid_http_url(url: str) -> bool:
    """Accept only HTTP or HTTPS URLs with a hostname."""
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.hostname)
        )
    except ValueError:
        return False


def _make_candidate(
    channel_type: str,
    value: str,
    result: dict,
    evidence: str,
) -> dict:
    """Create a candidate using a consistent schema."""
    return {
        "type": channel_type,
        "value": value,
        "source_url": _clean_text(result.get("url")),
        "source_title": _clean_text(result.get("title")),
        "evidence": evidence,
    }


def extract_contacts(search_results: list[dict]) -> list[dict]:
    """
    Extract contact candidates from Tavily search results.

    This function does not verify whether contact details are genuine,
    current, or operational.
    """
    if not isinstance(search_results, list):
        raise TypeError("search_results must be a list.")

    candidates = []
    seen = set()

    for result in search_results:
        if not isinstance(result, dict):
            continue

        title = _clean_text(result.get("title"))
        url = _clean_text(result.get("url"))
        content = _clean_text(result.get("content"))

        # A source URL is required so candidates remain traceable.
        if not _is_valid_http_url(url):
            continue

        # Search-result content is the available evidence.
        text = f"{title}\n{content}"
        lower_text = text.lower()

        def add_candidate(
            channel_type: str,
            value: str,
            evidence: str,
        ) -> None:
            key = (channel_type, value.lower(), url.lower())

            if key in seen:
                return

            seen.add(key)
            candidates.append(
                _make_candidate(
                    channel_type,
                    value,
                    result,
                    evidence,
                )
            )

        # 1. Extract email addresses.
        for match in EMAIL_PATTERN.finditer(text):
            email = match.group(0).strip(".,;:")

            if _valid_email(email):
                add_candidate(
                    "email",
                    email,
                    f"Email found in search-result text: {match.group(0)}",
                )

        # 2. Extract possible phone numbers.
        for match in PHONE_PATTERN.finditer(text):
            phone = match.group(0).strip(".,;:")

            if _valid_phone(phone):
                add_candidate(
                    "phone",
                    phone,
                    f"Possible phone number found in search-result text: {phone}",
                )

        # 3. Identify pages that appear relevant to contacting an authority.
        contact_page = any(
            keyword in lower_text
            for keyword in CONTACT_KEYWORDS
        )

        if contact_page:
            is_form = any(
                keyword in lower_text
                for keyword in FORM_KEYWORDS
            )

            channel_type = "form" if is_form else "website"

            add_candidate(
                channel_type,
                url,
                "Search-result title or content indicates a possible "
                "contact or complaint page.",
            )

    return candidates