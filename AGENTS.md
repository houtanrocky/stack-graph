# Repository Guidelines

## Project Structure & Module Organization

StackGraph is a Python research prototype comparing PR creation-time groups, official GitHub stack membership, and branch-derived dependency graphs.

- `stackgraph/`: `source.py` handles HTTP acquisition and caching; `model.py` normalizes metadata and implements comparisons; `plot.py` renders graphs; `__main__.py` runs the pipeline and generates reports.
- `tests/`: synthetic model cases, cache checks, and bundled-snapshot regression tests.
- `data/sample.json` defines the fixed sample; `data/cache/` holds provenance-bearing API snapshots.
- `results.md` and `artifacts/` contain generated reports, analysis JSON, execution metadata, and figures. `artifacts/presentation/` contains presentation materials and supporting scripts.
- Read `methodology.md` for research boundaries and `validation.md` for recorded checks.

## Build, Test, and Development Commands

Run from the repository root. Python 3.13.9 is the documented tested version; no separate build step is configured.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m stackgraph --offline
```

Use `requirements-lock.txt` instead for the exact tested dependency versions. The offline runner regenerates `results.md` and outputs under `artifacts/`. Use `--output` and `--results` to direct experimental outputs elsewhere. `--refresh` fetches current metadata and archives previous snapshots; copy `data/cache/` first to preserve the original active snapshot set.

## Coding Style & Naming Conventions

Follow existing Python conventions: four-space indentation, `snake_case` functions and variables, `PascalCase` classes, and descriptive module docstrings. Keep acquisition, comparison logic, plotting, and reporting in their respective modules. No formatter or linter is configured. Preserve deterministic ordering and UTF-8 JSON output with two-space indentation.

## Testing Guidelines

Use pytest; `pytest.ini` limits discovery to `tests/`. Name files `test_*.py` and functions `test_<behavior>`. Add focused regression cases for changed behavior. Use synthetic fixtures, `tmp_path`, and `monkeypatch`; tests should avoid live network requests. Preserve offline snapshot replay and cache-integrity checks. No numeric coverage threshold is configured.

## Commit & Pull Request Guidelines

This checkout has no Git history available to establish commit conventions. Use concise, imperative subjects, such as `Fix ambiguous branch matching`. PRs should explain behavior changes, link relevant issues, and record validation commands and outcomes. Include updated figures when rendering changes and explain any snapshot or generated-report updates.

## Research & Configuration Boundaries

Keep `GITHUB_TOKEN` in the environment; never save it in snapshots or logs. Only repository-qualified branch relationships create graph edges. Preserve unknown metadata states and provenance checks. Keep claims descriptive: stack structure does not establish AI authorship or workflow legitimacy.
