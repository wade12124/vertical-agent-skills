# Vertical Agent Skills — English Guide

A set of **vertical-scenario** Agent Skills following the [Agent Skills open specification](https://agentskills.io/specification). Unlike generic coding-skill collections, these packages encode industry workflows that an agent would otherwise get wrong: report contracts for unattended data tracking, funnel diagnostics for screening charters, pre-application company due diligence, Chinese genre-fiction craft with a hard copyright boundary, and WebMCP page-tool invocation.

Every skill is a folder of `SKILL.md` (frontmatter + instructions) plus optional `scripts/` and `references/`, loadable by any compliant client (Claude Code, Codex, Gemini CLI, Cursor, Qoder, etc.). Drop the folder into your client's skills directory — many clients scan `~/.agents/skills/<skill-name>/`.

## 1. recurring-data-tracking-report

**Problem it solves:** scheduled "track X and write a report" agents silently degrade when the task prompt depends on conversation context — the artifact becomes unreproducible, numbers get recycled from previous periods, and gaps are never declared.

**What it provides:** a 10-point output contract that must be written *inline* into every task prompt — self-containment, absolute-path naming with YYYYMMDD, source priority with declared fallback channels, per-value source and data-cutoff date, a hard "no fabrication" red line, market-holiday baselines, a fixed four-column threshold check table, mandatory next-period watch list and data-gap list, period-over-period loop (read the latest artifact before running), and post-creation task validation (dedupe same-schedule tasks). Includes a fill-in-the-blank prompt template and an acceptance checklist.

**When to trigger:** the user asks for a weekly/daily automated tracker report, wants cloud automation converted into local file artifacts, or asks whether an existing prompt is transferable.

## 2. screening-funnel-diagnosis

**Problem it solves:** multi-gate screening charters (stock/fund selection rules, index-methodology replicas) accumulate "both-and" conditions until the candidate pool collapses, and nobody can say which gate actually binds.

**What it provides:** a four-step diagnostic — sequential funnel replay, leave-one-out marginal constraint (including the terminal-scope gate, often the real bottleneck), Jaccard redundancy matrix between gates, and blocked-vs-passed candidate quality comparison (medians, not extremes) — with five read-out rules that distinguish idle gates, degenerate Jaccard rows, and the key finding that low-overlap AND conditions *swap* samples instead of stacking safety. `scripts/funnel_diagnose.py` runs all of it on an exported CSV with a pluggable gate config. Output is a mechanism diagnosis, explicitly not investment advice.

**When to trigger:** the user asks "is my screening too strict", "which condition binds most", "are these conditions redundant".

## 3. company-background-check

**Problem it solves:** job seekers evaluating an offer need registration, litigation, and enforcement history checked before accepting, but doing it manually on official sites is slow and captcha-blocked.

**What it provides:** a two-round parallel protocol — one entity-resolution call first, then 5–6 concurrent calls (registration, change records, judicial-document search keyed on the exact legal name, two web searches, optional representative-landscape probe) — plus a red-flag/normal/positive rubric (e.g., batch labor-arbitration entries and high-frequency legal-rep changes are red; ordinary commercial disputes at small firms are not disqualifying) and a conclusion-first output template with honest coverage caveats (zero hits ≠ no litigation; official channels remain the final verifier). Works with any business-registry + court-document data connectors; degrades gracefully to web-search snapshots with the fallback explicitly labeled.

## 4. douban-genre-craft

**Problem it solves:** writing original Chinese genre fiction (mystery, official-case, political, romance) without either copying bestseller surface features or drifting into telegraphic fragments and essayistic openings.

**What it provides:** 12 transferable techniques extracted from real Douban Read bestseller rankings via public metadata only (opening-abnormality hook, high-concept through-line, repetition-as-hook, craft-expert POV, dragged-in protagonist, observer protagonist, secret-carrying ensemble, contract-driven relationships, moral complexity, fictional-but-textured worlds, dual titling strategies, serial chapter hooks), a per-genre technique combinatorics guide, and a two-layer QA gate: `scripts/gate.py` mechanically checks CJK density, Latin intrusions, self-correction tics, title self-reference, and short-sentence ratio; a human audit checklist covers what scripts cannot catch. A strict copyright boundary is stated before everything else: borrow method, never copy protected expression, characters, or plot.

## 5. webmcp-bridge

**Problem it solves:** WebMCP-enabled pages register tools under `navigator.modelContextTesting`, but browser-evaluate contexts forbid top-level `await` and return MCP-shaped nested JSON that agents routinely mis-parse.

**What it provides:** the async-IIFE calling convention, availability probing, `listTools()` discovery with annotation handling (`readOnlyHint` / `destructiveHint` / `idempotentHint`), argument-passing as JSON strings, result unwrapping via `content[0].text`, four worked parameter-shape examples, and a pitfalls table. Requires `chrome://flags/#enable-webmcp-testing`.

## Boundaries

- No personal paths, credentials, or machine-specific configuration anywhere in this repo; example data in scripts is illustrative only.
- `funnel_diagnose.py` outputs screening-mechanism diagnostics, not investment advice; threshold changes must go through the charter's own revision process.
- `douban-genre-craft` redistributes only public ranking metadata analysis (titles, authors, categories, public blurbs, counts); no paywalled text was collected, and the full snapshot is referenced by source URL rather than redistributed.

## License

[MIT](../LICENSE)
