# Third-Party Licenses

The MCP-Atlas evaluation invokes 36 production Model Context Protocol
servers, each maintained by an independent upstream project. The
dataset and harness in this release do **not** redistribute these
servers; instead, agent runs against them are recorded as derived
claim scores under the dataset license (CC-BY-4.0).

This file lists the upstream MCP servers used in the February 2026
benchmark snapshot, and the upstream license that governs each. The
snapshot is fixed for the leaderboard; live re-evaluation requires
the user to install each server from its upstream source.

Server list (alphabetical):

| Server | Upstream license |
|---|---|
| airtable | Upstream-MIT |
| alchemy | Upstream-Apache-2.0 |
| arxiv | Upstream-MIT |
| brave-search | Upstream-MIT |
| calculator | Upstream-MIT |
| cli-mcp-server | Upstream-MIT |
| clinicaltrialsgov-mcp-server | Upstream-MIT |
| context7 | Upstream-MIT |
| ddg-search | Upstream-MIT |
| desktop-commander | Upstream-MIT |
| e2b-server | Upstream-Apache-2.0 |
| exa | Upstream-MIT |
| fetch | Upstream-MIT |
| filesystem | Upstream-MIT |
| git | Upstream-MIT |
| github | Upstream-MIT |
| google-maps | Upstream-MIT |
| google-workspace | Upstream-MIT |
| lara-translate | Upstream-MIT |
| mcp-code-executor | Upstream-MIT |
| mcp-server-code-runner | Upstream-MIT |
| memory | Upstream-MIT |
| met-museum | Upstream-MIT |
| mongodb | Upstream-Apache-2.0 |
| national-parks | Upstream-MIT |
| notion | Upstream-MIT |
| open-library | Upstream-MIT |
| osm-mcp-server | Upstream-MIT |
| oxylabs | Upstream-MIT |
| pubmed | Upstream-MIT |
| slack | Upstream-MIT |
| twelvedata | Upstream-MIT |
| weather | Upstream-MIT |
| weather-data | Upstream-MIT |
| whois | Upstream-MIT |
| wikipedia | Upstream-MIT |

The "Upstream-*" placeholders reflect the licenses observed at the
time of the February 2026 snapshot. Final upstream license strings
will be confirmed and replaced with canonical SPDX identifiers in the
camera-ready release. If an upstream project relicenses, the snapshot
license remains the one that governed the benchmark run.

Tool outputs captured during evaluation are governed by the upstream
APIs' terms of service. We release only the agent's final-answer text
and the per-claim scores derived from it, never the raw tool
responses.
