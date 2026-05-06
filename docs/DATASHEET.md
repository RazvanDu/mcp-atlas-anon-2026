# Datasheet for MCP-Atlas

Following the structure of *Datasheets for Datasets*
(Gebru et al., 2021). Author identification is anonymized for
double-blind review and will be restored at camera-ready.

## Motivation

**For what purpose was the dataset created?**
MCP-Atlas evaluates the tool-use competency of large language models
acting as agents over real Model Context Protocol (MCP) servers. The
benchmark targets a gap left by toy or synthetic tool-use benchmarks:
production MCP servers exhibit messy real-world behavior — rate limits,
authentication flows, schema drift, partial failures — that small
hand-crafted environments do not capture.

**Who created the dataset and on behalf of which entity?**
[Anonymized for double-blind review.]

**Who funded the creation of the dataset?**
[Anonymized for double-blind review.]

## Composition

**What do the instances represent?**
Each instance is a tool-use task: a single-turn natural-language user
request, paired with (a) a list of atomic factual claims that any correct
answer must contain, (b) a reference solution trajectory executed against
real MCP servers, (c) a reference final answer, and (d) the curated set
of MCP tools made available to the agent (including deliberate
distractors).

**How many instances are there in total?**
1,000 tasks total: 500 in the public split (released here under
CC-BY-4.0) and 500 in the private split (held back during peer review,
released alongside the camera-ready paper).

**Does the dataset contain all possible instances or is it a sample?**
A curated sample. Tasks were authored to span 36 production MCP servers
and to require multi-tool reasoning where appropriate. The sample is not
intended to be statistically representative of any natural distribution
over user requests.

**What data does each instance consist of?**
See `docs/DATA_SCHEMA.md`. Each row is text (prompts, claims, reference
answers) and structured JSON (trajectories, tool lists). No images,
audio, or sensor data.

**Is there a label or target?**
Yes. The atomic-claims list (`GTFA_CLAIMS`) is the target; an LLM judge
scores each claim independently against the model's response and the
mean determines whether the task passes (mean ≥ 0.75).

**Is any information missing from individual instances?**
No required fields are missing across the 500 public-split rows.

**Are relationships between individual instances made explicit?**
Tasks are independent. Some tasks share required servers; the
co-occurrence matrix is recoverable from `REQUIRED_SERVERS`.

**Are there recommended data splits?**
Yes: a public split (released) and a private split (held back). The
intended use is evaluation, not training. Public-private split assignment
was randomized at task-authoring time.

**Are there errors, sources of noise, or redundancies?**
- Live MCP servers may drift between the February 2026 snapshot when the
  benchmark was authored and the time of any re-evaluation. Some servers
  expose rate-limited or paginated APIs whose results vary day-to-day.
- The LLM judge introduces a ceiling estimated at 2–5 percentage points
  of pass-rate variance under independent re-execution.
- The coverage metric assigns equal weight to each claim within a task,
  which can disadvantage tasks whose claims have non-uniform difficulty.

**Is the dataset self-contained?**
The released CSV is self-contained for scoring. Live re-evaluation
requires installing the upstream MCP servers (see
`THIRD-PARTY-LICENSES.md`) and providing an LLM endpoint.

**Does the dataset contain confidential or sensitive information?**
No. All tasks query public APIs, public data sources, or use synthetic
in-memory state (e.g. the `memory` server's local graph). Tasks were
authored to use no PII.

**Does the dataset contain content that might be offensive, insulting, or
threatening?**
No. Authors avoided controversial topics and used general-knowledge,
research-aid, and information-retrieval prompts.

**Does the dataset relate to people?**
A small fraction of tasks reference public figures (musicians, athletes,
scientists) by name in the context of factoids about them. No private
individuals.

## Collection process

**How was the data acquired?**
Tasks were authored manually by a research team. Each author drafted
prompts, executed reference solutions against live MCP servers in a
containerized sandbox, and recorded the resulting trajectory and final
answer. Atomic claims were distilled from the reference answer by the
author and verified by an automated LLM verifier plus a secondary
reviewer.

**What mechanisms or procedures were used to collect the data?**
A dedicated authoring environment provided the same sandboxed MCP server
fleet used at evaluation time. Reference solutions were captured from a
strong frontier LLM under expert supervision, then edited by the author
for fidelity.

**Over what timeframe was the data collected?**
Authoring took place between mid-2025 and early 2026. The MCP server
behavior snapshot is February 2026.

**Were any ethical review processes conducted?**
Authoring guidelines required avoiding PII, sensitive personal
attributes, and topics likely to produce harmful outputs. No formal IRB
review (no human subjects).

## Preprocessing, cleaning, labeling

**Was any preprocessing/cleaning/labeling done?**
- Prompts containing tool or server names were rewritten to use natural
  language (e.g. "search the web" rather than "use brave-search").
- Reference final answers were distilled into atomic verifiable claims.
- A four-layer QA pipeline was applied to every task: (1) author
  correctness review, (2) tool/server name leakage review, (3) automated
  LLM verification of claim completeness, (4) random-sample manual audit.

**Is the preprocessing software available?**
The claim evaluator (`harness/score_claims.py`), v2 failure-mode
diagnostic (`harness/single_model_diagnostic_v2.py`), and the failure
taxonomy (`harness/mcp_failure_taxonomy.py`) are released in this
artifact. The authoring tooling is internal.

## Uses

**Has the dataset been used for any tasks already?**
Yes — to produce the leaderboard reported in the accompanying paper,
covering 20 frontier models from Anthropic, OpenAI, Google, Meta, and
several open-source projects.

**Is there a repository linking to papers or systems that use the
dataset?**
[Anonymized for double-blind review.]

**What other tasks could the dataset be used for?**
- Capability evaluation of new tool-using LLM agents.
- Failure-mode taxonomy research (the `runs/diagnosis_v2/` artifact
  classifies every failed task into one of 11 categories).
- Cost/efficiency tradeoff analysis (per-task `trajectory_time` enables
  Pareto-frontier studies).
- Contamination monitoring against public benchmarks (the public/private
  split was designed for this).

**Is there anything about the composition of the dataset or the way it
was collected and preprocessed/cleaned/labeled that might impact future
uses?**
- The leaderboard is sensitive to the agent system prompt. The shipped
  numbers use no system prompt. Different prompting scaffolds will
  produce different absolute pass rates.
- All prompts are English. The dataset is not suitable for multilingual
  agent evaluation as released.
- Server behavior drifts. Pass rates obtained months after the February
  2026 snapshot are not directly comparable to the leaderboard.

**Are there tasks for which the dataset should not be used?**
- Training data. The dataset is intended exclusively for evaluation.
  Training on it will overfit a small benchmark and is unlikely to
  generalize.
- Safety or robustness evaluation. The benchmark targets capability, not
  alignment; tasks were not adversarially constructed.

## Distribution

**Will the dataset be distributed to third parties?**
Yes. The public split is released here for peer review and will receive
a persistent DOI at camera-ready. The private split is held back until
camera-ready.

**How will the dataset be distributed?**
Tarball release with Croissant 1.0 metadata
(`data/croissant.jsonld`) and CC-BY-4.0 license (`LICENSE-DATA`).

**When will the dataset be distributed?**
Public split: with this submission. Private split: on paper acceptance
or at the publication date, whichever is later.

**Will the dataset be distributed under a copyright or other IP license?**
Public split data: CC-BY-4.0 (`LICENSE-DATA`). Harness code: Apache 2.0
(`LICENSE-CODE`). Tool-call outputs captured during evaluation are
governed by the upstream APIs' terms of service and are not
redistributed; we release only the agent's final-answer text and the
per-claim scores derived from it.

**Have any third parties imposed IP-based or other restrictions on the
data?**
The upstream MCP servers carry their own licenses (see
`THIRD-PARTY-LICENSES.md`). The dataset itself does not include server
code; live re-evaluation requires installing each server from its
upstream source.

**Do any export controls or other regulatory restrictions apply?**
None known.

## Maintenance

**Who will be supporting/hosting/maintaining the dataset?**
[Anonymized for double-blind review.]

**How can the owner/curator/manager be contacted?**
[Anonymized for double-blind review.]

**Is there an erratum?**
None at release. Errata, if any, will accompany versioned re-releases.

**Will the dataset be updated?**
Yes — the leaderboard is intended to track new model releases. Versioned
updates will preserve the schema; major schema changes will bump the
major version. Updates do not retroactively change the leaderboard
numbers in past releases.

**Are older versions of the dataset continued to be supported / hosted /
maintained?**
Past releases will remain accessible at their DOIs.

**If others want to extend/augment/build on this dataset, is there a
mechanism for them to do so?**
The CC-BY-4.0 license permits derivatives. Authors are encouraged to
contribute new tasks via the public repository at camera-reveal time.
