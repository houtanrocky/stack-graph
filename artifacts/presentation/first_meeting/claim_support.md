# Claim support and boundaries

The first-meeting materials refine the question and propose an evaluation. They do not replace prior artifacts or create new observations of PR workflows. The existing [audit report](../audit_report.md), [exact PR evidence](../evidence_table.md), [graph](../graph.pdf), and original brief remain unchanged. All earlier limitations, including timestamp provenance cautions, remain applicable.

## Observed case: independently checkable against the saved data

| Claim | Saved support | Boundary |
| --- | --- | --- |
| 8 real PRs, one repository and author | `../../analysis.json`: `pull_requests`; `../evidence_table.csv`; eight raw PR JSON bodies in `../../../data/cache/` | Selected `cli/cli` case, not a representative sample |
| 4 verified branch-targeting arrows | `../audit_evidence.json`: `verified_edges`; two raw endpoint records per arrow | Repository/ref equality and matching SHAs verify targeting; no independent semantic/intent labels |
| Chain 14348 → 14349 → 14350 → 14351 → 14355 | Raw `head.repo.full_name`, `head.ref`, `base.repo.full_name`, `base.ref`; full SHA corroboration in the edge evidence | Direction is prerequisite → dependent; no timing inference |
| 3 isolates, 4 weak components, no cycles | `../../analysis.json`: `C_branch_graph` | Isolation is within this sample, not proof of historical independence |
| Time groups have sizes 2 and 6 | `../../analysis.json`: `A_time_only.groups` | Creation times were read from PR resources, not actual Events API collection |
| 16 time-co-grouped pairs versus 10 graph-component pairs | `../../analysis.json`: `descriptive_agreement` | Direct graph edge count is 4, not 10; pair agreement is not accuracy |
| 6 time pairs cross graph components | `descriptive_agreement.A_pairs_outside_C_components` | Five involve control 14347 and stack members; one pairs controls 14345/14346; not validated false positives |
| No C component pairs separated by A | `descriptive_agreement.C_pairs_not_grouped_by_A` is empty | This selected case does not establish event-heuristic recall |
| Native metadata documents one five-PR stack | Raw native `stack` fields and five matching filtered stack responses; original B output | Selection used this metadata; not independent evaluation ground truth |
| Native/graph membership agreement: 10 pairs, no disagreements | `B_C_common_pairs` and `B_C_disagreeing_pairs` | Conceptual overlap with native branch-chain definitions remains |
| Thresholds 15/60/180 minutes yield 3/2/1 groups and 11/16/28 pairs | `../../analysis.json`: `A_sensitivity` | Illustrative sensitivity, not threshold validation |
| 16 responses in the original cold collection; 0 requests offline | `../../execution-live.json`; `../validation_audit.json` | Eight PR details and eight filtered stack lookups; not a minimal-query benchmark |
| 32 passing tests and stable offline reproduction | `../pytest.xml`, `../validation_audit.json`; fresh first-meeting validation is recorded in `validation.json` | Software correctness checks are not independent workflow labels |
| No direct official-stack input leakage observed | `../../../stackgraph/model.py`; real-snapshot metadata-ablation test in `../../../tests/test_pipeline.py` | Selection bias and conceptual dependence remain |
| Precision/recall unset; general accuracy unproven | `../../analysis.json`: `evaluation` | A new evaluation needs independent labels; no metrics are inferred from descriptive agreement |

The first-meeting validation rechecks every raw payload checksum and all four endpoint matches, reruns the existing tests and offline CLI, and hashes all pre-existing files to ensure preservation. `validation.json` and `validation.md` record actual outcomes, not planned outcomes.

## Operational constraints: documented, inferred, or privately reported

| Statement | Evidence class and source | Defensible wording |
| --- | --- | --- |
| Up to 300 activity events within the last 30 days | Official GitHub documentation; cached `context_sources.json`, key `events` | REST activity timeline ceiling, not a cap on all GitHub data access or a measured truncation result in this case |
| Missing stack information in activity events | Availability concern; official event schema extract, key `event_types` | Required fields may be absent; verify a particular payload/version. The docs reference a nested PR object and do not explicitly specify native stack membership there. Universal absence is not established; no Events API payloads are cached |
| Extra lookups cost requests | Official rate-limit documentation, key `rate_limits`; actual saved collection count | Request-budget cost; latency/money not measured. Primary unauthenticated public REST limit is documented as 60 requests/hour; other credentials/secondary limits differ |
| Maintainer feedback about false negatives | User-reported private Discord communication; `context_sources.json.private_communication` | Informal motivation. No transcript, identity, specific cases, version, missed-stack count, or cause is supplied. Not independently verified and not a gold label |
| Existing baseline is not AgentScan production | Inspect `time_groups`, dependencies, and prior audit | No AgentScan invocation or classification exists. Do not attribute current grouping disagreements to AgentScan |

Documentation URLs and retrieval dates:

- [GitHub REST events](https://docs.github.com/en/rest/activity/events), checked and excerpted 2026-10-28 UTC.
- [GitHub event types](https://docs.github.com/en/rest/using-the-rest-api/github-event-types#pullrequestevent), checked and excerpted 2026-10-28 UTC.
- [GitHub REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api), checked and excerpted 2026-10-28 UTC.

The local context cache contains short extracted sections, source-response hashes, timestamps, and interpretation limits, not a new PR dataset. Neither an omitted schema property nor a private conversation is presented as an empirical availability experiment. The current historical PR case was obtained through direct resource APIs after its creation events were older than 30 days; it cannot demonstrate how much activity an Events API consumer would recover.

## Proposals, not findings

E/M/G comparisons, matched budget sweeps, independent annotation, stack/edge precision and recall, exact-stack reconstruction efficiency, and missing-information coverage are all proposed only. No new method, dataset, algorithmic advantage, cost saving, false-negative count, classifier accuracy, or human-authorship inference has been produced.

The comparison must allow the scientifically useful outcome that direct metadata rules are sufficient and graph algorithms add no measurable improvement. A recursive relational rule can implement the same closure as a graph algorithm. Any future claim must name the actual baseline and computation rather than treating a graph library as an independent source of information.
