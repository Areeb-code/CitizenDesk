from app.graph import graph


initial_state = {
    "complaint": (
        "Stray dogs have been roaming near Street 5, "
        "Model Town, Lahore, Pakistan, for two weeks. "
        "Residents feel unsafe, and children are afraid "
        "to walk to school. Please arrange a humane response."
    ),
    "language": "English",
    "facts": {},
    "missing": [],
    "questions": [],
    "feedback_answers": {},
    "authority": "",
    "research_results": [],
    "channels": [],
    "failed_channels": [],
    "research_mode": "normal",
    "attempt": 0,
    "draft": [],
    "review": {},
    "revision": 0,
    "status": "running",
    "saved_file": "",
    "log": [],
}


print("\nStarting CitizenDesk workflow...\n")

try:
    result = graph.invoke(initial_state)

    print("\n========== FINAL RESULT ==========")
    print("Status:", result.get("status"))
    print("Authority:", result.get("authority"))
    print("Saved file:", result.get("saved_file"))

    print("\n========== GENERATED DRAFTS ==========")
    for draft in result.get("draft", []):
        print(draft)

    print("\n========== WORKFLOW LOG ==========")
    for entry in result.get("log", []):
        print("-", entry)

except Exception as error:
    print("\nWORKFLOW FAILED")
    print(type(error).__name__, ":", error)
    raise