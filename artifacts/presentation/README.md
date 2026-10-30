# StackGraph presentation package

Present this as an **exploratory Network Science case study**. The defensible finding is that explicit branch targeting adds ordering and provenance beyond a simplified chronological grouping heuristic in this selected example. General detection accuracy and workflow legitimacy remain inconclusive.

Start here:

- [research_brief.pdf](research_brief.pdf): one-page handout covering the problem, question, graph, methods, observations, limitations, and next experiment. [Markdown source](research_brief.md).
- [graph.pdf](graph.pdf): publication-style vector graph for slides or printing. [300-dpi PNG](graph.png) and [caption](figure_caption.md).
- [presentation_notes.md](presentation_notes.md): a 90-second explanation and five difficult questions with answers.
- [evidence_table.md](evidence_table.md): all eight exact PR URLs, creation times, branches, native membership, and the four verified arrows. [CSV](evidence_table.csv).
- [audit_report.md](audit_report.md): scientific audit, baseline identity, leakage findings, and fresh validation outcomes.

Supporting evidence:

- `audit_evidence.json`: inventory/checksums for every original cache record, raw-field edge proofs, SHA corroboration, and comparison to fresh observations.
- `live_metadata_check.json`: eight separate read-only live PR responses collected during this audit; the original cache is unchanged.
- `pytest.xml`, `pytest.log`: full rerun of the test suite.
- `validation_audit.json`: executed command results, offline runs, checksum comparison, and source-cache preservation check.
- `offline_run_1.log`, `offline_run_2.log`: fresh offline reproduction stdout.

Reproduction commands, from the project root (PowerShell):

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=artifacts/presentation/pytest.xml
.\.venv\Scripts\python.exe -m stackgraph --offline
.\.venv\Scripts\python.exe artifacts/presentation/prepare_materials.py
```

The helper regenerates static presentation evidence and layouts from the saved data; it adds no new research method and makes no network calls. It reads the separate saved live cross-check rather than re-fetching it. The one-page brief is emitted as exactly one PDF page. Fonts/rendering were visually checked in the tested Windows environment; cross-platform figure bytes may differ. `brief_preview.png` is the inspected raster preview of the brief.

Method A is **not AgentScan**. Official GitHub membership is not independent ground truth. Four direct edges must not be confused with ten unordered co-member pairs. The controls are snapshot-specific structural controls, not established historical negatives. Stacked PRs do not establish human authorship.
