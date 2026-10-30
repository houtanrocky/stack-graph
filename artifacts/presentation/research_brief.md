# StackGraph

Exploratory Network Science case study · audited snapshot: 28 October 2026

## Research problem

Closely spaced pull-request creation events can describe separate changes or a coordinated stack. An activity-only view lacks explicit dependency direction. This exploratory case examines what verified branch relationships add to that view.

## Research question

Within a selected public GitHub case, do repository-qualified branch relationships reveal an ordered PR workflow and distinguish nearby controls beyond chronological grouping? Workflow legitimacy and authorship are outside the measured target.

## Graph formulation

G = (V, E) is a directed, unweighted PR graph. For distinct P and Q, P → Q when P's head repository/ref uniquely matches Q's base repository/ref. The arrow means prerequisite → dependent in a branch-targeting sense. All PRs remain nodes. Timing, PR text, and official stack fields cannot create edges.

## Three methods compared

A: simplified time heuristic; group sampled PR creation events by successive gaps of at most 60 minutes within a repository. It is not AgentScan, which was not run. B: native GitHub stack membership, used descriptively. C: branch-derived directed graph; weak components support unordered membership comparisons.

## Actual observed findings

Eight PRs from cli/cli, one author, created 4 September 2026. A yields groups of sizes 2 and 6 (16 co-grouped pairs). B documents one five-PR stack (10 co-member pairs). C gives 8 nodes, 4 arrows, 4 weak components, 3 isolates, and no cycles: 14348 → 14349 → 14350 → 14351 → 14355. All four raw branch matches also have equal SHAs. Six A pairs cross C components: five pair control 14347 with stack members; one pairs controls 14345 and 14346. At 15/180 minutes, A gives 3/1 groups.

## Research limitations

One purposively selected stack; controls selected using branches and native membership; one repository/author; only sampled creation events. Branch and stack metadata are mutable retrieval-time observations. No direct stack-field leakage into C was found, but selection bias and conceptual overlap with GitHub's branch-chain definition remain. No independent labels: precision/recall are unset. General detection accuracy and legitimacy remain inconclusive; stacks do not establish human authorship.

## Next proposed experiment

Freeze the same rules and sample all PRs in predeclared repository/date windows. Obtain independently adjudicated intentional-stack membership from code/history review or maintainers, blind to method outputs and native stack labels. Keep uncertain cases unknown. Only then compare A/B/C and report precision/recall with the target and denominator stated.

Evidence: evidence_table.md and audit_evidence.json. Figure: graph.pdf. Full caveats: audit_report.md.
