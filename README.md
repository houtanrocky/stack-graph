# StackGraph

Can verified GitHub pull-request dependency relationships provide useful context beyond chronological event activity when identifying legitimate stacked-PR workflows?

StackGraph is a small Python research prototype comparing time grouping, native GitHub stack membership, and a directed graph built from base/head branch relationships. It uses eight real public PRs from `cli/cli`: one five-layer stack and three nearby same-author controls. The study measures descriptive structure; general identification performance and workflow legitimacy remain **inconclusive**. It does not detect AI authorship.

## Run

Tested with Python 3.13.9. Run commands from this directory. No token is required for public GitHub metadata, subject to API rate limits.

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m stackgraph --offline
```

macOS/Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m stackgraph --offline
```

The saved source JSON makes the example reproducible without GitHub access. Dependency installation still needs a package index. The four direct dependencies are pinned in `requirements.txt`; `requirements-lock.txt` records the full tested environment. Use `-r requirements-lock.txt` for the exact tested dependency versions. Figure bytes may differ across platforms/fonts, while the saved analysis is deterministic for the same sources.

To fetch current public metadata, use:

```powershell
.\.venv\Scripts\python.exe -m stackgraph --refresh
```

Without flags, the runner reuses each cached source and fetches cache misses. `--offline` fails on any cache miss and makes no network requests. `--refresh` archives existing snapshots and retrieves new ones; PRs can change, so new observations need not reproduce the original findings. Copy `data/cache/` before a refresh if you want to retain the original active snapshot set. An optional `GITHUB_TOKEN` environment variable raises authenticated rate limits; it is never saved in source JSON or logs.

## Read the experiment

- [methodology.md](methodology.md): definitions, input separation, sampling, limitations, and evaluation policy.
- [results.md](results.md): generated observations, source links, retrieval dates, and interpretation.
- [artifacts/graph.png](artifacts/graph.png): labeled branch graph, including isolated controls.
- [artifacts/analysis.json](artifacts/analysis.json): normalized PR metadata and all three comparisons.
- [validation.md](validation.md): commands actually executed and observed outcomes.

The analysis uses:

| Comparison | Inputs | Output |
| --- | --- | --- |
| A: time only | Repository and PR creation time | Groups separated by successive gaps over 60 minutes |
| B: official membership | Native `stack` field and filtered GitHub Stacks API responses | Observed stack memberships; explicit unknown/absence states |
| C: branch graph | PR identity and repository-qualified base/head refs | NetworkX directed graph; prerequisite → dependent |

**Baseline identity:** A is a simplified, repository-local creation-time grouping heuristic implemented in `time_groups`. It does not execute AgentScan or its `@unveil/identity` scoring library. This study makes no comparison with AgentScan classifications, detection performance, or false-positive rates. AgentScan describes an account-level automation analysis in its [upstream README](https://github.com/MatteoGabriele/agentscan); that is a different task from PR activity grouping.

C adds `P → Q` only when P's head repository and branch equal Q's base repository and branch, and the head match is unique in the sample. Time, author identity, PR text, and official stack fields never create edges. All PRs remain nodes. Unmatched or missing relationships can leave isolated nodes; isolation is relative to this sample.

For example, `#14349` targets the head branch of `#14348`, so the arrow is `#14348 → #14349`. The one-hour baseline also groups the separate `#14347` creation event with this chain. This illustrates extra structural context; it is not an accuracy estimate.

## Small code map

```text
stackgraph/source.py     Read-only HTTP requests and dated JSON cache
stackgraph/model.py      Normalization and the three comparisons
stackgraph/plot.py       Matplotlib graph PNG; no external layout software
stackgraph/__main__.py   Reproducible command-line runner and report
data/sample.json        Fixed PR identifiers and selection rationale
data/cache/             Original API JSON inside provenance envelopes
tests/                  Deterministic synthetic edge cases and cache checks
```

The runner writes `results.md` and `artifacts/`. It retains `execution-live.json` and `execution-offline.json` separately, alongside the latest `execution.json`. Acquisition uses only HTTP GET. There is no dashboard, database, learned model, or GNN.

## Research boundary

Native stack membership helped select the example, so the sample is biased toward that workflow. The official metadata is a descriptive comparison, never independent evaluation ground truth. Branch fields are independently available inputs but are not statistically independent of GitHub's stack definition. PR body statements corroborate this example after selection; they are not a blinded benchmark. Precision and recall remain unset until an independently validated positive-and-negative label set exists.

Stack topology describes workflow organization. It cannot establish authorship, maintainership intent, code quality, safety, or whether a workflow is legitimate.

The audited presentation package is in [artifacts/presentation/](artifacts/presentation/README.md), including a one-page research brief, verified edge evidence, a publication figure, and speaking notes.
