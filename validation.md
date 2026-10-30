# Executed validation

Validation was completed on 2026-10-28 using Python 3.13.9 on Windows, from `S:\Repos\stack-graph`.

| Executed command or check | Observed outcome |
| --- | --- |
| `python -m venv .venv` | Virtual environment created successfully. |
| `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` | All four pinned direct dependencies and their dependencies installed successfully. The complete installed versions are in `requirements-lock.txt`. |
| `python -m stackgraph` | Real public-data run succeeded: 16 HTTP GET responses saved, all HTTP 200, no cache hits; eight PR nodes and four branch-derived edges. Source retrieval ran from 05:01:46 to 05:02:06 UTC. This acquisition used the system Python with the same three pinned runtime package versions. |
| `python -m compileall -q stackgraph tests` | Completed successfully after the implementation was finished. |
| `.\.venv\Scripts\python.exe -m pytest -q --junitxml=artifacts/pytest.xml` | **31 passed in 2.76 seconds**, exit code 0. |
| `.\.venv\Scripts\python.exe -m pip check` | `No broken requirements found.` |
| `.\.venv\Scripts\python.exe -m pip freeze` | Successfully recorded the complete installed dependency versions for `requirements-lock.txt`. |
| `.\.venv\Scripts\python.exe -m stackgraph --offline` | Real cached example succeeded: 16 cache hits, zero network requests; eight nodes, four edges, three isolated controls, no cycles. Generated the analysis JSON, graph PNG, and results report. |
| Second successive offline execution via `subprocess.run([sys.executable, '-m', 'stackgraph', '--offline'], check=True, ...)` in the virtual environment | Succeeded with 16 cache hits and zero network requests. SHA-256 hashes of `artifacts/analysis.json`, `artifacts/graph.png`, and `results.md` exactly matched the preceding offline run. |
| JUnit/provenance assertions | Confirmed 31 test cases with no failures/errors, all 16 source statuses equal to 200, and the recorded live/offline request counts. |
| Visual inspection of `artifacts/graph.png` | Checked the generated image: five PRs in a labeled directed chain, three separately displayed isolated controls, branch evidence on edges, and an explicit prerequisite → dependent direction. |

The deterministic tests use synthetic fixtures for direction, temporal proximity, isolated PRs, missing branch fields, missing or invalid timestamps, different forks, ambiguous reused branches, duplicate PRs, self-targeting refs, cycles, and official membership availability/conflicts. Cache tests check provenance, offline replay, integrity failures, cache misses, HTTP errors, and refresh archival using mocked responses. One test also replays the bundled real snapshot entirely offline and checks its observed structure and the absence of evaluation metrics. These expected snapshot observations are regression checks, not independent research labels.

Machine-readable evidence:

- [artifacts/pytest.xml](artifacts/pytest.xml): test results.
- [artifacts/execution-live.json](artifacts/execution-live.json): successful live acquisition run.
- [artifacts/execution-offline.json](artifacts/execution-offline.json): final offline run.
- [artifacts/verification.json](artifacts/verification.json): replay checksums, both final offline execution records, and confirmed test/request counts.

The exact byte comparison applies to two runs in this tested environment. Cross-platform rendering was not tested. The README's macOS/Linux commands and live `--refresh` mode were not executed; refresh archival was tested with mocked responses. Installing directly from `requirements-lock.txt` was not separately exercised; that file records the successfully installed environment.

The observed branch graph is:

```text
14348 → 14349 → 14350 → 14351 → 14355

14345   14346   14347   (isolated within this sample)
```

The one-hour baseline has two groups and 16 co-grouped pairs. Official membership identifies one five-PR stack with 10 co-member pairs. Branch components also contain 10 co-member pairs; six time-grouped pairs cross those components. This is descriptive agreement, not a performance estimate. No independent label set was available, so precision and recall were not calculated. General identification performance and workflow legitimacy remain inconclusive.

## Presentation audit

The baseline is a simplified creation-gap heuristic, not AgentScan. Neither AgentScan nor its identity library was executed. The original validation above records the preliminary run; fresh test and offline reproduction evidence, raw-field edge verification, and the leakage audit are saved in [artifacts/presentation/audit_report.md](artifacts/presentation/audit_report.md). Presentation work does not change the graph construction or grouping algorithms.
