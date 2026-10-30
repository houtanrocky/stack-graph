# StackGraph scientific audit

**Verdict:** suitable for presentation as an exploratory, auditable Network Science case study. The observations support additional descriptive branch structure beyond the implemented time heuristic. They do not validate detection accuracy, workflow legitimacy, or human authorship. No major method or project feature was added.

## Scope inspected

Inspected `README.md`, `methodology.md`, `results.md`, `validation.md`; all five Python source files in `stackgraph/`; all three test files; the sample manifest, dependency pins, pytest configuration, and prior execution/verification artifacts. Parsed every byte of all 16 original cached JSON envelopes and payloads. All payload checksums passed, every cached HTTP status is 200, and the source URLs map to eight PR resources plus eight filtered native-stack lookups. `audit_evidence.json` inventories every source file and its full-file checksum.

The eight PRs are all in `cli/cli`, authored by `williammartin`, and created on 2026-09-04. Branch and stack metadata were retrieved on 2026-10-28. The original cache was not changed. Eight separate live GET observations, saved in `live_metadata_check.json`, agree with the original cache on author, creation time, base/head repository/ref/SHA, and the native stack field for every sampled PR. This cross-check corroborates API observations, not independent research labels.

## 1. Every dependency arrow verified

The graph orientation is **prerequisite → dependent**. For each arrow P → Q, Q targets the branch contributed by P. Both endpoint repositories are `cli/cli`; the parent head ref equals the child base ref, with exactly one sampled head matching that qualified ref. All four pairs also have equal parent-head/child-base SHAs.

| ID | Arrow | Parent `head.ref` = child `base.ref` | Audit result |
| --- | --- | --- | --- |
| E1 | [14348](https://github.com/cli/cli/pull/14348) → [14349](https://github.com/cli/cli/pull/14349) | `williammartin-git-real-repo-test-harness` | Repository/ref match; SHA match |
| E2 | [14349](https://github.com/cli/cli/pull/14349) → [14350](https://github.com/cli/cli/pull/14350) | `williammartin-git-graph-tests` | Repository/ref match; SHA match |
| E3 | [14350](https://github.com/cli/cli/pull/14350) → [14351](https://github.com/cli/cli/pull/14351) | `williammartin-git-transport-tests` | Repository/ref match; SHA match |
| E4 | [14351](https://github.com/cli/cli/pull/14351) → [14355](https://github.com/cli/cli/pull/14355) | `williammartin-improve-git-tests` | Repository/ref match; SHA match |

Exact URLs, UTC creation/retrieval times, raw cache mappings, repository/ref fields, and full 40-character SHAs are recorded in [evidence_table.md](evidence_table.md), [evidence_table.csv](evidence_table.csv), and `audit_evidence.json`. The verification compares raw PR resource fields, not stack positions or chronological order. SHA equality was found during the audit and does not change the existing graph-generation rule. “Verified dependency” means verified branch targeting here; semantic code dependency and historical intent were not independently established.

PRs 14345, 14346, and 14347 have distinct heads, target `trunk`, and remain isolated in the sampled graph. Their PR resources omit the `stack` key; their successful, complete filtered lookups return `[]`. This supports “no membership observed at retrieval,” not “never stacked” or “has no semantic dependencies.”

## 2. Baseline identity: simplified heuristic, not AgentScan

`stackgraph/model.py:46`, `time_groups`, sorts sampled creation events within each repository, then groups consecutive events whose gap is at most 60 minutes. It uses no profile attributes, cross-event scoring rules, account classification, or authorship detector. There is no AgentScan or identity dependency or invocation anywhere in the implementation. It is a **simplified chronological grouping heuristic**.

For external context, the [AgentScan upstream README](https://github.com/MatteoGabriele/agentscan) says its account-activity analysis is powered by identity. The [identity upstream README](https://github.com/unveil-project/identity) describes an account-and-events classification/scoring interface. These primary descriptions were inspected during this audit. Neither system was run or reproduced, and no AgentScan account score or classification is part of this case. The experiment cannot support a claim of outperforming AgentScan or correcting an AgentScan false positive.

The initial local documentation did not name AgentScan; it also did not explicitly exclude that interpretation. The README, methodology, generated results template, current results, validation note, research brief, and speaking notes now make the distinction explicit. “Independent branch-field graph” was changed to “branch-derived targeting graph” in the generated results table to avoid implying statistical independence.

## 3. Leakage audit

| Possible route | Finding | Scientific consequence |
| --- | --- | --- |
| Official fields into C topology | No direct route found. `normalize` (`model.py:28`) keeps identity/display metadata and qualified refs, excluding `stack`, labels, and body. `dependency_graph` (`model.py:105`) matches only qualified head/base refs. | Code-level input separation is supported. |
| Time or author into C edges | Neither is used to create, orient, or disambiguate edges. These fields are retained for display. | A close creation time or shared author cannot create an edge. |
| Official lookup into graph construction | `analyze` constructs C before computing B (`__main__.py:34–36`); B's output is not passed into C. | Official membership is a descriptive comparison. |
| Manifest role assignments into topology | `stack_candidates` is descriptive manifest data; `structural_controls` is used to print a report table. Neither constructs edges. | Role labels do not force graph membership. |
| Native labels as independent evaluation truth | No such scoring path exists. `evaluation` fixes independent-label availability to false and precision/recall to null. B–C pair counts are explicitly descriptive agreement. | No independently validated performance metric exists. |
| Native labels in sample selection | Present: official membership selected the known positive stack, and branches/membership informed controls. | Material ascertainment bias remains; input separation cannot remove it. |
| Conceptual relationship between B and C | Present: GitHub's native stack concept itself uses branch chaining. | Agreement is expected and cannot independently validate either method. |
| Text corroboration | Selected body excerpts are checked after selection. They are not edge features or an adjudicated evaluation set. | Useful case context, not independent ground truth. |

The new real-snapshot ablation regression removes official fields, replaces native lookup data with empty lists, removes PR text/labels, and swaps manifest stack/control assignments. B's membership result changes; C's full graph summary, A's groups, and the unset evaluation result remain identical. This is a software audit of input separation, not a new experiment measuring predictive performance.

## 4. Observations checked and how to describe them

| View | Observed result |
| --- | --- |
| A: 60-minute simplified time heuristic | Groups `{14345,14346}` and `{14347,14348,14349,14350,14351,14355}`; 16 unordered co-grouped pairs |
| B: native membership | Stack 14352, positions 1–5: 14348, 14349, 14350, 14351, 14355; 10 unordered co-member pairs |
| C: branch graph | 8 nodes; 4 directed edges; 4 weak components with sizes 5,1,1,1; 3 isolates; no cycles |
| Descriptive disagreement | Six A pairs cross C components: five pair 14347 with chain members; one pairs 14345 with 14346 |
| B–C agreement | Ten unordered membership pairs agree; zero disagreements within this selected sample |
| Threshold sensitivity | 15/60/180 minutes give 3/2/1 time groups and 11/16/28 co-grouped pairs |

Four direct graph edges and ten weak-component co-membership pairs are different quantities. The latter include indirect connections. The six cross-component time pairs are not validated false positives. No precision, recall, significance test, or generalization estimate is supported. The result demonstrates an ordered representation and a concrete explanation for each connection, beyond the chosen time grouping.

## 5. Remaining research limitations and provenance cautions

- One repository, one account, one purposively selected stack, and three selected controls. There is no representative sample or held-out benchmark.
- A includes only eight selected PR creation events, not a complete event stream. Sampling changes gaps. The 60-minute threshold is illustrative; the sensitivity outputs do not validate it.
- Branches and memberships are mutable snapshots observed well after creation. Equal SHAs confirm observed branch alignment, not complete commit ancestry or historical reconstruction.
- Native membership may mechanically influence the branch structure being observed. Separate fields are not separate causal or statistical evidence.
- Controls are structural at retrieval; unobserved workflows and semantic dependencies remain possible. Missing matches or fields must not become established negatives.
- Cached client retrieval timestamps and server `Date` headers differ: server dates are about 44.2–46.5 seconds later in these envelopes. The cause was not established. Both are preserved. Do not assume sub-minute clock synchronization or use retrieval times to infer event order. A uses the PR payload's `created_at`, so this offset does not change the reported time groups or edges.
- The SHA-256 checks are integrity checks, not independent source-authenticity proofs. Fresh API agreement adds a source cross-check while preserving the original snapshot.
- The runner's conclusion is a case-specific narrative, not a fitted or evaluated classifier. Applying its reporting template to another sample would require inspecting that narrative again.
- Workflow topology cannot establish human/AI authorship, intent, code quality, or legitimacy. Saved authorship disclosures were not used as labels or independently verified.

## 6. Presentation outputs

The one-page [research brief](research_brief.pdf) contains the problem, question, graph formulation, three methods, actual findings, limitations, and next proposed experiment. [Figure 1](graph.pdf) is a vector PDF with an accompanying 300-dpi [PNG](graph.png); it shows exact PR identities/titles, verified directed edges E1–E4, their branch evidence key, and isolated controls. The [caption](figure_caption.md) states the operational meaning and limits of an arrow. Layout is topological; distance is not time. Color uses connectivity, not official labels.

[presentation_notes.md](presentation_notes.md) contains a short 90-second script and five difficult questions with accurate answers. The proposed next experiment is a predeclared repository/date-window sample, frozen rules, independent intentional-stack co-membership adjudication blind to outputs/native labels, unknowns retained, and predictive metrics only after an appropriate label set exists.

## 7. Fresh execution results

Executed in the existing Python 3.13.9 virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=artifacts/presentation/pytest.xml
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m stackgraph --offline
.\.venv\Scripts\python.exe -m stackgraph --offline
.\.venv\Scripts\python.exe artifacts/presentation/prepare_materials.py
```

- **32 tests passed in 1.44 seconds**; zero failures, errors, or skips. This includes the new real-snapshot leakage ablation regression. JUnit evidence is in `pytest.xml`.
- `pip check`: `No broken requirements found.`
- Both fresh offline runs exited successfully with **16 cache hits and zero network requests each**. Both recovered the same eight nodes, four edges, three isolates, and no cycles.
- SHA-256 hashes of `artifacts/analysis.json`, `artifacts/graph.png`, and `results.md` agree between the two fresh offline runs.
- The analysis JSON and original graph PNG also match their pre-audit versions. `results.md` changed intentionally to clarify the heuristic/AgentScan distinction; observations did not change.
- Every original cache file remains byte-for-byte unchanged. All 16 checksums pass.
- The new graph and brief were generated and visually inspected. The brief PDF has exactly one page; the generator also asserts the page count. The figure PNG is 300 dpi.
- The separate live cross-check returned eight HTTP-200 responses and agreed on every audited PR field. It was not used to replace the original dataset or to create evaluation labels.

**Test, evidence-verification, and reproduction failures: none.** `validation_audit.json` records the current command outcomes, both offline execution records, output hashes, PDF page count, and cache preservation checks. Earlier `artifacts/verification.json` records the preliminary run's hashes; this audit record supersedes it for the current clarified report. Cross-platform rendering, actual AgentScan execution, independent semantic adjudication, and predictive accuracy evaluation were not performed.
