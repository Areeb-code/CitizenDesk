import operator
from typing import TypedDict, Annotated

class AgentState(TypedDict):
    #input from the user
    complaint: str
    language:str

    #intake
    facts: dict
    missing: list

    #Research
    authority: str #which body handle this problem
    research_results: list
    channels: list #ranked contracts: value, type, source e.t.c
    failed_channels: list
    research_mode: str #normal or extented
    attempt: int #how many reasearch round so far

    #Writing
    draft: list #one entry per channel [channel, format, text]
    review: dict
    revision:int

    #Control and Output
    status: str              # "running", "needs_info", or "done"
    saved_file: str
    log: Annotated[list, operator.add]   # every node ADDS lines, nothing is overwritten

    #feedback
    questions: list
    feedback_answers: dict

    # Friendly explanation when local services or extraction are unavailable.
    error_message: str
