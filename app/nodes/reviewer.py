import re

from app import config
from app.state import AgentState


# Detect unfilled curly-brace placeholders, such as {location}.
PLACEHOLDER = re.compile(r"[{}]")

# Detect phone-like sequences containing at least 9 digits.
NUMBER = re.compile(r"\+?\d[\d\s\-()]{6,}\d")

# Common duration expressions.
DURATION = re.compile(
    r"\b(days?|weeks?|months?|years?)\b",
    re.IGNORECASE,
)

IMPACT_WORDS = (
    "health",
    "safety",
    "safe",
    "danger",
    "risk",
    "disease",
    "hygiene",
    "unsafe",
)

# These failures prevent a draft from passing review.
CRITICAL_CHECKS = {
    "No invented phone numbers",
    "No unfilled { } placeholders",
}


def _digits(text: str) -> str:
    """Return only the digits from a string."""
    return re.sub(r"\D", "", text)


def _words(text: str, min_len: int = 4) -> list[str]:
    """Extract meaningful words for location checks."""
    return [
        word
        for word in re.findall(r"\w+", text.lower())
        if len(word) >= min_len
    ]


def _mentions_location(text: str, facts: dict) -> bool:
    """
    Check whether the draft mentions the provided location.

    All meaningful location words must appear in the draft.
    """
    location = str(facts.get("location", "")).strip()

    if not location:
        return False

    location_words = _words(location)
    draft_words = set(_words(text, min_len=1))

    if not location_words:
        return False

    return all(word in draft_words for word in location_words)


def _known_numbers(state: AgentState) -> set[str]:
    """
    Collect phone-number digits from researched contact channels.

    The verifier should populate channels with researched contacts.
    """
    known = set()

    for channel in state.get("channels", []):
        if not isinstance(channel, dict):
            continue

        value = str(channel.get("value", "")).strip()
        digits = _digits(value)

        # Avoid treating arbitrary short numbers as verified contacts.
        if len(digits) >= 7:
            known.add(digits)

    return known


def _no_invented_numbers(
    text: str,
    known: set[str],
) -> bool:
    """
    Reject phone-like sequences that do not match known contact numbers.

    This is a heuristic. It cannot prove that a number is genuine.
    """
    for match in NUMBER.findall(text):
        digits = _digits(match)

        if len(digits) < 9:
            continue

        # A long number must match a known number, allowing formatting
        # differences or a partial representation of a known number.
        matches_known = any(
            digits in known_number or known_number in digits
            for known_number in known
        )

        if not matches_known:
            return False

    return True


def _email_checks(
    text: str,
    facts: dict,
    english: bool,
) -> dict[str, bool]:
    """Validate the required elements of an email draft."""
    low = text.lower()

    checks = {
        "Starts with a Subject line": (
            bool(re.match(r"\s*subject\s*:", low))
        ),
        "Mentions the location": _mentions_location(text, facts),
        "Within 250 words": len(text.split()) <= 250,
        "Has [Name] and [Phone] placeholders": (
            "[name]" in low and "[phone]" in low
        ),
    }

    if english:
        checks["States how long it has lasted"] = bool(
            DURATION.search(low)
        )

        checks["Mentions health or safety impact"] = any(
            word in low for word in IMPACT_WORDS
        )

        checks["Asks for action within a deadline"] = (
            "within" in low
            and bool(
                re.search(r"\b(days?|hours?)\b", low)
            )
        )

    return checks


def _phone_checks(
    text: str,
    facts: dict,
) -> dict[str, bool]:
    """Validate the required elements of a phone-call script."""
    low = text.lower()

    return {
        "Asks for a reference number": (
            "reference number" in low
            or "complaint number" in low
        ),
        "Handles a redirect": "which office" in low,
        "Includes an escalation question": "supervisor" in low,
        "Mentions the location": _mentions_location(text, facts),
        "Within 350 words": len(text.split()) <= 350,
    }


def _generic_checks(
    text: str,
    facts: dict,
) -> dict[str, bool]:
    """Apply basic checks to other draft formats."""
    return {
        "Mentions the location": _mentions_location(text, facts),
        "Within 300 words": len(text.split()) <= 300,
    }


def review_draft(
    draft: dict,
    facts: dict,
    known_numbers: set[str],
    english: bool,
) -> dict:
    """
    Review one draft.

    Returns its checks, quality score, and critical failures.
    """
    text = str(draft.get("text", ""))
    kind = str(draft.get("format", "")).strip().lower()

    if kind == "email":
        checks = _email_checks(text, facts, english)

    elif kind in {"phone", "call", "call_script"}:
        checks = _phone_checks(text, facts)

    else:
        checks = _generic_checks(text, facts)

    # Apply safety and template checks to every format.
    checks["No invented phone numbers"] = _no_invented_numbers(
        text,
        known_numbers,
    )

    checks["No unfilled { } placeholders"] = (
        not PLACEHOLDER.search(text)
    )

    score = round(
        sum(checks.values()) / len(checks),
        2,
    )

    critical_failures = [
        name
        for name, passed in checks.items()
        if name in CRITICAL_CHECKS and not passed
    ]

    return {
        "checks": checks,
        "score": score,
        "critical_failures": critical_failures,
        "passed": (
            score >= config.PASS_SCORE
            and not critical_failures
        ),
    }


def reviewer_node(state: AgentState) -> dict:
    """
    Review all generated drafts and update the workflow state.

    Reads state['draft'] and returns a review dictionary and log entries.
    """
    facts = state.get("facts", {})
    drafts = state.get("draft", [])
    language = str(state.get("language", "English"))

    if not isinstance(facts, dict):
        facts = {}

    english = language.strip().lower() == "english"

    # Handle missing or invalid draft collections.
    if not isinstance(drafts, list) or not drafts:
        review = {
            "score": 0.0,
            "passed": False,
            "failed": ["There is no draft to review."],
            "critical_failures": [],
            "per_draft": [],
        }

        return {
            "review": review,
            "log": ["Reviewer: no drafts to review."],
        }

    known = _known_numbers(state)

    per_draft = []
    failed = []
    critical_failures = []

    for index, draft in enumerate(drafts, start=1):
        if not isinstance(draft, dict):
            label = f"draft_{index}"
            message = f"{label}: expected a dictionary."

            failed.append(message)
            critical_failures.append(message)

            per_draft.append({
                "format": label,
                "score": 0.0,
                "passed": False,
                "checks": {
                    "Draft is a dictionary": False,
                },
                "critical_failures": [message],
            })

            continue

        result = review_draft(
            draft=draft,
            facts=facts,
            known_numbers=known,
            english=english,
        )

        label = str(draft.get("format") or f"draft_{index}")

        per_draft.append({
            "format": label,
            "score": result["score"],
            "passed": result["passed"],
            "checks": result["checks"],
            "critical_failures": result["critical_failures"],
        })

        # Record every failed check with an actionable label.
        for name, passed in result["checks"].items():
            if not passed:
                failed.append(f"{label}: {name}")

        for failure in result["critical_failures"]:
            critical_failures.append(f"{label}: {failure}")

    # The weakest draft determines the overall score.
    score = min(
        item["score"]
        for item in per_draft
    )

    passed = (
        score >= config.PASS_SCORE
        and not critical_failures
        and all(item["passed"] for item in per_draft)
    )

    review = {
        "score": score,
        "passed": passed,
        "failed": failed,
        "critical_failures": critical_failures,
        "per_draft": per_draft,
    }

    log = [
        f"Reviewer: score {score} across {len(drafts)} draft(s).",
        f"Reviewer: {'passed' if passed else 'failed'} quality review.",
    ]

    if critical_failures:
        log.append(
            "Reviewer: critical failures - "
            + "; ".join(critical_failures)
        )

    if failed:
        log.append(
            "Reviewer: failed checks - "
            + "; ".join(failed)
        )

    return {
        "review": review,
        "log": log,
    }