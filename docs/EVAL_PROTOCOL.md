# Evaluation Protocol (offline reference)

This document echoes the evaluation protocol from the paper's Appendix
B for offline reading. The paper is the authoritative source.

## Agent system prompt

**No agent system prompt is used.** Each task is presented as a single
user message containing the verbatim `PROMPT` field, with no preceding
instructions on tool usage, planning, output format, or stopping
behavior.

This choice isolates each model's intrinsic tool-use disposition from
prompt-engineered scaffolding and removes a per-provider tuning
surface that would otherwise confound cross-provider comparison.

The harness exposes an optional system-prompt flag (`--system-prompt`)
for downstream users who want to study the effect of system-level
instruction. It is disabled in every leaderboard run reported in the
paper.

## Claim evaluator prompt (verbatim)

The judge is invoked once per claim, not once per task. It receives
the claim text and the model's final answer and assigns a categorical
label which is then mapped to a numeric score
(`fulfilled` → 1.0, `partially_fulfilled` → 0.5, `not_fulfilled` → 0.0).

```
You are evaluating how well a model's response addresses a specific
expert-defined claim.

SCORING CRITERIA:
- fulfilled: Claim is completely and accurately addressed. The
  response covers all key details.
- partially_fulfilled: Claim is partially addressed. The response
  covers some but not all key details.
- not_fulfilled: Claim is not addressed. The response does not
  include any key details.

NUMERICAL COMPARISON GUIDELINES:
- For numerical values, use reasonable approximation thresholds:
  * Exact match NOT required for decimals
  * Values within 5% of the claimed number are considered matching
  * For percentages, +/-1 percentage points is acceptable
  * Round to appropriate significant figures based on context
- Consider the precision appropriate to the domain:
  * Scientific measurements may need higher precision
  * General statistics/estimates can have looser matching
  * Financial figures should match to reasonable business precision
- If a number is expressed differently but mathematically equivalent
  (e.g., "0.5" vs "50%" vs "half"), consider it a match.

CLAIM TO EVALUATE:
{claim}

MODEL RESPONSE TO ANALYZE:
{response}

INSTRUCTIONS:
1. Determine if the core requirement of the claim is met.
2. Check if all key components from the claim appear substantively in
   the response. For numerical values, apply the flexible matching
   guidelines above.
3. Assign the appropriate coverage_outcome.
4. Provide specific justification referencing what was or was not
   covered. When numbers differ slightly, note if they fall within
   acceptable range.
5. Provide a confidence level (0.0-1.0) for your assessment.

Be rigorous but fair in your assessment. Focus on whether the response
conveys the same information as the claim, not on exact numerical
precision unless precision is critical to the claim's meaning.
```

## Run config

| Setting | Value |
|---|---|
| max_tool_calls | 100 |
| max_turns | 256 |
| pass threshold | coverage >= 0.75 |
| primary judge | `gemini/gemini-3.1-pro-preview` |
| cross-judges | `openai/gpt-5.4`, `anthropic/claude-opus-4-6` |
| agent system prompt | none |

## Coverage computation

For a task with k claims, coverage is the mean of the k per-claim
scores in {0.0, 0.5, 1.0}. Each claim is scored by an independent
judge call with only the claim text and the model's full response as
input. A task passes at coverage >= 0.75.
