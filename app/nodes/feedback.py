from app.state import AgentState


def feedback_node(state: AgentState) -> dict:
    """
    Ask the citizen for missing information or process their answers.
    """

    facts = state.get("facts", {})
    missing = state.get("missing", [])
    answers = state.get("feedback_answers", {})

    if not isinstance(facts, dict):
        facts = {}

    if not isinstance(missing, list):
        missing = []

    if not isinstance(answers, dict):
        answers = {}

    facts = dict(facts)
    remaining_missing = []
    log = []

    # Process answers supplied by the citizen.
    for item in missing:
        field = str(item).strip()

        if not field:
            continue

        answer = answers.get(field)

        if answer is not None and str(answer).strip():
            facts[field] = str(answer).strip()
            log.append(f"Received an answer for: {field}.")
        else:
            remaining_missing.append(field)

    # Build clear questions for missing information.
    questions = []

    question_templates = {
        "issue": "What problem are you reporting?",
        "category": "What category does the problem belong to?",
        "country": "In which country did the problem occur?",
        "city": "In which city did the problem occur?",
        "location": "What is the specific location of the problem?",
        "duration": "How long has this problem been happening?",
        "impact": "How is this problem affecting you or others?",
        "language": "Which language would you prefer for your complaint?",
    }

    for field in remaining_missing:
        question = question_templates.get(
            field,
            f"Please provide the following information: {field}.",
        )
        questions.append({
            "field": field,
            "question": question,
        })

    if remaining_missing:
        status = "needs_info"
        log.append(
            f"Citizen clarification is required for "
            f"{len(remaining_missing)} field(s)."
        )
    else:
        status = "running"
        log.append(
            "No required information is missing. "
            "The workflow can continue."
        )

    return {
        "facts": facts,
        "missing": remaining_missing,
        "questions": questions,
        "status": status,
        "log": log,
    }