"""MCP-Atlas Failure Taxonomy — single source of truth for failure mode definitions.

Two categories:
- Tool-call issues: problems with how the model interacted with tools
- Cognitive issues: problems with how the model reasoned about the task

11 modes total (4 tool-call + 7 cognitive).

This module is imported by the diagnosis pipeline and any reporting tooling.
"""

# ---------------------------------------------------------------------------
# Taxonomy definition
# ---------------------------------------------------------------------------

TOOL_CALL_MODES = {
    "malformed_call": {
        "description": "Right tool, wrong parameters: missing arguments, bad types, or wrong values.",
        "example": "Called mongodb_find with column name 'revenue' when the schema field is 'Revenue_USD'.",
    },
    "wrong_tool": {
        "description": "Picked an inappropriate tool for the subtask.",
        "example": "Used wikipedia_search when the data lives in airtable, querying the wrong data source.",
    },
    "no_tool_use": {
        "description": "Answered from internal knowledge without calling any tool, despite tools being required.",
        "example": "Reported a historical date directly without querying any source.",
    },
    "err_recovery": {
        "description": "A tool returned an error and the model could not adapt: it retried identically, looped uselessly, or gave up.",
        "example": "Hit a rate limit, then retried the same call five times instead of backing off or trying an alternative.",
    },
}

COGNITIVE_MODES = {
    "task_misunderstanding": {
        "description": "Answered a different question than the one asked, or missed a key requirement in the prompt.",
        "example": "Prompt asked for 'average revenue in December' but the model returned total revenue for the full year.",
    },
    "faulty_synthesis": {
        "description": "Had the right tool outputs but combined or interpreted them incorrectly. Not a logic error.",
        "example": "Queried the right table, got the right rows, then averaged the wrong column in the final answer.",
    },
    "response_misparsing": {
        "description": "Got valid tool output but misread its structure or extracted the wrong field.",
        "example": "Tool returned a list of 10 records; the model picked the wrong row or read the wrong field.",
    },
    "early_termination": {
        "description": "Understood the task but stopped before completing all the required steps.",
        "example": "Found the first half of a two-part answer and produced a final answer without addressing the second.",
    },
    "hallucinated_fact": {
        "description": "Stated something in the final answer that was not present in any tool output.",
        "example": "Tool returned a population of 45,000 but the model wrote 54,000 in its answer.",
    },
    "logical_error": {
        "description": "Multi-step reasoning chain was flawed even though the underlying data were correct.",
        "example": "Correctly retrieved the date and database records but applied the wrong conditional to filter them.",
    },
    "constraint_violation": {
        "description": "Ignored an explicit condition or filter stated in the prompt.",
        "example": "Prompt said 'only premium units built in 2017' but the model queried all units across all years.",
    },
}


# ---------------------------------------------------------------------------
# Derived constants (used by the diagnosis pipeline)
# ---------------------------------------------------------------------------

FAILURE_TAXONOMY = {
    "tool_call": TOOL_CALL_MODES,
    "cognitive": COGNITIVE_MODES,
}

# Flat list of all mode names, used for schema enum validation.
ALL_MODES = list(TOOL_CALL_MODES.keys()) + list(COGNITIVE_MODES.keys())

# Mode -> category lookup.
MODE_TO_CATEGORY = {}
for mode in TOOL_CALL_MODES:
    MODE_TO_CATEGORY[mode] = "tool_call"
for mode in COGNITIVE_MODES:
    MODE_TO_CATEGORY[mode] = "cognitive"


def get_taxonomy_prompt_text() -> str:
    """Render the failure-mode definitions for inclusion in the judge prompt."""
    lines = []
    lines.append("TOOL CALL ISSUES — Problems with how the model interacted with tools:")
    for mode, info in TOOL_CALL_MODES.items():
        lines.append(f"- {mode}: {info['description']} (e.g., {info['example']})")
    lines.append("")
    lines.append("COGNITIVE ISSUES — Problems with how the model reasoned about the task:")
    for mode, info in COGNITIVE_MODES.items():
        lines.append(f"- {mode}: {info['description']} (e.g., {info['example']})")
    return "\n".join(lines)


def get_diagnosis_schema() -> dict:
    """JSON schema for the structured diagnosis output."""
    failure_entry_schema = {
        "type": "object",
        "properties": {
            "mode": {"type": "string", "enum": ALL_MODES},
            "category": {"type": "string", "enum": ["tool_call", "cognitive"]},
            "is_root_cause": {"type": "boolean"},
            "explanation": {"type": "string"},
        },
        "required": ["mode", "category", "is_root_cause", "explanation"],
    }

    return {
        "type": "object",
        "properties": {
            "primary_failure": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ALL_MODES},
                    "category": {"type": "string", "enum": ["tool_call", "cognitive"]},
                    "explanation": {"type": "string"},
                },
                "required": ["mode", "category", "explanation"],
            },
            "all_failures": {
                "type": "array",
                "items": failure_entry_schema,
            },
            "confidence": {"type": "number"},
            "summary": {"type": "string"},
        },
        "required": ["primary_failure", "all_failures", "confidence", "summary"],
    }
