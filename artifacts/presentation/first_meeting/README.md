# StackGraph: first meeting with a Network Science professor

This revision preserves the validated core, original data, graph, reports, and all earlier presentation artifacts. It sharpens the question and proposes a bounded follow-up; it adds no new dataset or research method implementation.

**Research question:** To what extent can dependency-graph information improve the identification of stacked pull-request workflows compared with event-based heuristics, under constrained GitHub API access?

Use these materials:

- [One-page research brief](research_brief.pdf), with [Markdown source](research_brief.md).
- [90-second presentation script](presentation_script.md).
- [Follow-up design and metric definitions](evaluation_plan.md): separate information value, algorithm value, and API-budget value.
- [Claim-to-evidence audit](claim_support.md): cached case evidence, official API constraints, and the limited status of the Discord feedback.
- [Validation and changed-file report](validation.md), with [machine-readable outcomes](validation.json).

Continue showing the existing [graph](../graph.pdf) and keep the [exact PR evidence table](../evidence_table.md) available. The [earlier audit](../audit_report.md), [original brief](../research_brief.pdf), and all prior limitations remain intact.

The next proposed methods are E (event-only heuristic), M (enriched metadata rules), and G (graph analysis with M's identical inputs). These are not a relabeling of the existing A/B/C experiment: existing B is native membership. The production AgentScan classifier is not implemented or evaluated. Neither current group disagreements nor private feedback establishes an AgentScan error rate.

The present case demonstrates a verified branch-targeting chain and nearby isolated controls. It has no independently adjudicated performance labels. Metadata rules may already be sufficient, and global graph operations may produce no incremental accuracy benefit. API efficiency and missing-information coverage remain unmeasured. Structure establishes neither legitimacy nor human authorship.

The Discord motivation is explicitly presenter-reported private communication, without a supplied transcript or identified missed cases. The 300-event/30-day ceiling and request limits are documented GitHub activity-API constraints, with short source extracts in [context_sources.json](context_sources.json). Missing stack fields are an availability condition to check per payload/version; universal omission is not claimed.

To regenerate only this new brief from the project root:

```powershell
.\.venv\Scripts\python.exe artifacts/presentation/first_meeting/render_brief.py
```

The helper makes no network calls and writes only the new brief PDF and preview here. `preserved_files.json` records the SHA-256 hashes of all 59 pre-existing project and evidence files before this revision, including the original raw cache; the validation verifies they remain unchanged. Python bytecode, pytest's transient cache, and the virtual environment are excluded. Core tests and isolated offline reproduction are recorded under `validation/` without overwriting prior artifacts.

To rerun the preservation checks, all existing tests, cached-edge verification, and isolated offline reproduction:

```powershell
.\.venv\Scripts\python.exe artifacts/presentation/first_meeting/validate_materials.py
```
