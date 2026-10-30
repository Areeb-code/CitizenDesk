from urllib.parse import urlparse

from app import config
from app.state import AgentState


# Common official government domain endings.
OFFICIAL_DOMAIN_ENDINGS = (
    ".gov.pk",
    ".gov",
    ".gop.pk",
    ".punjab.gov.pk",
)

# Contact channel types we recognize.
VALID_CHANNEL_TYPES = {
    "phone",
    "email",
    "website",
    "web form",
    "form",
    "portal",
    "address",
}


def _get_domain(url: str) -> str:
    """Extract a normalized domain from a URL."""
    if not url:
        return ""

    try:
        parsed = urlparse(
            url if "://" in url else f"https://{url}"
        )
        hostname = (parsed.hostname or "").lower()

        # Ignore common www prefixes.
        if hostname.startswith("www."):
            hostname = hostname[4:]

        return hostname

    except (ValueError, AttributeError):
        return ""


def _looks_official(channel: dict) -> bool:
    """
    Apply a basic domain heuristic.

    This is a preliminary signal, not proof that a source is genuine.
    """
    source_url = str(
        channel.get("source_url")
        or channel.get("url")
        or ""
    ).strip()

    domain = _get_domain(source_url)

    if not domain:
        return False

    return any(
        domain == ending.lstrip(".")
        or domain.endswith(ending)
        for ending in OFFICIAL_DOMAIN_ENDINGS
    )


def _verify_channel(channel: dict) -> dict:
    """Score the evidence available for one contact channel."""
    value = str(channel.get("value") or "").strip()
    channel_type = str(
        channel.get("type") or ""
    ).strip().lower()

    source_url = str(
        channel.get("source_url")
        or channel.get("url")
        or ""
    ).strip()

    source_title = str(
        channel.get("source_title")
        or channel.get("title")
        or ""
    ).strip()

    evidence = str(
        channel.get("evidence")
        or channel.get("source")
        or ""
    ).strip()

    official = _looks_official(channel)
    score = 0.0
    notes = []

    # A usable contact value must be present.
    if value:
        score += 0.30
        notes.append("Contact value is present.")
    else:
        notes.append("Contact value is missing.")

    # Recognize the kind of contact channel.
    if channel_type in VALID_CHANNEL_TYPES:
        score += 0.15
        notes.append("Contact channel type is recognized.")
    else:
        notes.append("Contact channel type is missing or unrecognized.")

    # A source URL allows the evidence to be traced.
    if source_url and _get_domain(source_url):
        score += 0.15
        notes.append("A source URL is provided.")
    else:
        notes.append("A usable source URL is missing.")

    # Official-looking domain is useful, but not conclusive.
    if official:
        score += 0.25
        notes.append(
            "Source domain matches a common government-domain pattern."
        )
    else:
        notes.append(
            "Source is not confirmed by the government-domain heuristic."
        )

    # Record supporting source information.
    if source_title or evidence:
        score += 0.15
        notes.append("Supporting source information is provided.")
    else:
        notes.append("Supporting source information is limited.")

    score = round(min(score, 1.0), 2)
    meets_threshold = score >= config.PASS_SCORE

    if not value:
        status = "rejected"
    elif meets_threshold and official:
        status = "candidate_passed"
    elif meets_threshold:
        status = "needs_manual_confirmation"
    else:
        status = "needs_more_evidence"

    # Return the original candidate with added verification metadata.
    verified = dict(channel)
    verified.update({
        "verification_score": score,
        "source_appears_official": official,
        "meets_verification_threshold": meets_threshold,
        "verification_notes": notes,
        "verification_status": status,
        "live_contact_tested": False,
    })

    return verified


def verifier_node(state: AgentState) -> dict:
    """
    Evaluate contact-channel candidates collected by the research workflow.
    """
    channels = state.get("channels", [])

    if not isinstance(channels, list):
        return {
            "channels": [],
            "status": "running",
            "log": [
                "Verifier stopped: channels must be a list."
            ],
        }

    if not channels:
        return {
            "channels": [],
            "status": "running",
            "log": [
                "Verifier found no contact channels to assess.",
                "Research or contact extraction must provide candidates first.",
            ],
        }

    verified_channels = []
    log = [
        f"Verifier started: assessing {len(channels)} contact candidate(s)."
    ]

    for index, channel in enumerate(channels, start=1):
        if not isinstance(channel, dict):
            log.append(
                f"Candidate {index} skipped: expected a dictionary."
            )
            continue

        verified = _verify_channel(channel)
        verified_channels.append(verified)

        log.append(
            f"Candidate {index}: "
            f"{verified['verification_status']} "
            f"(score {verified['verification_score']})."
        )

    passed_count = sum(
        1
        for channel in verified_channels
        if channel["verification_status"] == "candidate_passed"
    )

    log.append(
        f"Verifier completed: {passed_count} candidate(s) passed "
        "the preliminary checks."
    )
    log.append(
        "No live phone, email, or contact-channel test was performed."
    )

    return {
        "channels": verified_channels,
        "status": "running",
        "log": log,
    }