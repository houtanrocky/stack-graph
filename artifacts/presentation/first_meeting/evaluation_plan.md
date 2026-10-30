# Proposed follow-up evaluation

This is a design for discussion at a first professor meeting. No new dataset, method implementation, budget experiment, accuracy result, or maintainer adjudication has been added. The existing core and all prior research artifacts are preserved.

## Refined research question

**To what extent can dependency-graph information improve the identification of stacked pull-request workflows compared with event-based heuristics, under constrained GitHub API access?**

The measured target should be intentional stacked-workflow membership and direct prerequisite relationships, with definitions agreed before evaluation. “Legitimate,” “human-authored,” and “automated account” are different targets and are not inferred from this graph. A branch-targeting edge is an observed structural relationship; its correspondence to an intended prerequisite requires independent assessment.

## Separate three hypotheses

| Question | Controlled comparison | What it could support |
| --- | --- | --- |
| A. Additional dependency information | M versus E, using the same candidate frame and recorded acquisition costs | Value of enrichment beyond the chosen event heuristic |
| B. Incremental graph algorithms | G versus M, identical enriched fields, request order, matching rule, and metadata snapshot | Benefit of the specified global aggregation/analysis beyond the specified direct rules |
| C. Limited API budgets | Repeat the comparisons at predeclared request caps and missingness conditions | Accuracy/coverage/cost trade-offs under those conditions |

A graph drawing by itself does not establish an algorithmic benefit. G versus E mixes new information and global processing, so it cannot isolate B. A human-interface study comparing a branch table with a graph would be a separate representation/usability question; it is not executed here.

## Three proposed methods

Use **E/M/G** to avoid confusing the proposed methods with the existing A/B/C outputs. Existing B is native membership, not the proposed enriched-rule baseline.

| Proposed method | Inputs and decisions | Status |
| --- | --- | --- |
| E: event-only heuristic | Repository and observable PR-creation times; freeze the current successive-gap rule and threshold before evaluation | Existing rule can serve as a proxy baseline; current times came from PR resources, not captured Events API payloads |
| M: enriched metadata rules, no global graph algorithms | E inputs plus qualified base/head refs and availability states; apply the same unique direct branch-match predicate as G. Make pair-local same-stack/direct-dependency decisions; no transitive reachability, connected-component aggregation, ordering, or cycle analysis | Proposed only |
| G: graph-based dependency analysis | Exactly M's enriched records and direct matches; aggregate with weak components and, where appropriate, inspect reachability, prerequisite order, and cycles. Retain isolates and unknowns | Existing graph is a starting point; the controlled follow-up has not been executed |

M and G must share metadata, matching predicates, missingness masks, and acquisition order at every budget. Neither may receive native stack membership or independently adjudicated labels as features. Keep native membership as a separate descriptive comparison. Timing never creates a dependency edge. Unknown refs, fork collisions, ambiguous reuse, and cycles retain the existing safeguards.

This deliberately isolates direct matching from global aggregation. For a five-node chain, closure can create ten same-component pairs from four direct links; that is an expected consequence of aggregation, not evidence of a novel algorithm. With identical direct matching, M and G are expected to have identical direct-edge predictions unless an explicitly preregistered global validation/abstention rule changes them. Do not assume edge precision or recall will improve. A stronger recursive relational-rule baseline could reproduce G's groups exactly; report that equivalence rather than claiming a unique advantage of graph libraries. Any result is relative to the chosen baseline.

Before exact-stack scoring, specify a comparable group-output protocol for every method. Pair-local M decisions need not form a consistent partition; record this explicitly and do not silently apply transitive closure only to repair M during scoring. Pair precision/recall can be the initial common task. Report exact-stack cost only for methods with a predeclared comparable group decoder; otherwise mark it not applicable. Agree with the professor on whether this local-rule baseline is sufficiently strong before collecting evaluation data.

## Candidate frame, labels, and budget control

Start with frozen episode definitions, fixed repository/date windows, and a captured candidate/event frame. For an initial reconstruction task, give methods the same observed PR candidates. Separately measure which eligible PRs an activity feed failed to expose against an independently established inventory. Report reconstruction conditional on discovered candidates separately from discovery coverage and end-to-end recall. Do not silently remove invisible PRs from the population and then claim full coverage.

Define same-stack pair labels and directed adjacent-prerequisite labels through independent maintainer or code/history adjudication, blind to native membership and method outputs. Record evidence, uncertain cases, and annotation coverage. Existing body excerpts and native stack positions are not an independent label set. Freeze thresholds, candidate scope, acquisition policy, endpoints, metric definitions, and failure handling before scoring; do not tune on the selected eight-PR case and report it as held-out validation. A future representative label set would require separate collection; none is collected in this task.

Declare per-episode request caps and replay the same acquisition schedule for M and G. Do not let G fetch more fields than M and attribute the resulting gain to algorithms. Keep graph-guided acquisition as a separate future question. E can leave enrichment budget unused; report actual usage as well as the cap. Record initial discovery requests, pagination, detail requests, native lookups if used for context, retries, failures, cache hits, and authentication mode. Separate offline computation cost and evaluation-only label collection from model acquisition cost. Compare cold-start and warm-cache conditions separately. A missing response consumes any request actually made and remains unknown, not a negative relationship.

## Possible metrics; all currently unmeasured

| Metric | Proposed operational definition |
| --- | --- |
| Stack-membership precision and recall | Treat an unordered PR pair as positive when both belong to the same independently adjudicated intentional stack. Precision = TP/(TP+FP); recall = TP/(TP+FN). Freeze eligible pairs and distinguish direct links from indirect co-membership. Report per-episode results and an aggregate; pairs within a case are not independent samples. |
| Dependency-edge precision and recall | Score ordered adjacent prerequisite pairs; both endpoint identity and direction must match the independently adjudicated definition. Do not score all reachable pairs as direct edges. Use TP/(TP+FP) and TP/(TP+FN) on the predeclared universe. |
| API calls per correctly reconstructed stack | Total observed acquisition HTTP attempts / number of exactly reconstructed gold stack member sets, with no extra or missing members. If correct direction is required, state that extra requirement and report it separately. Count shared discovery costs consistently. Zero correct stacks makes the ratio undefined; report zero successes and the call count, not a fabricated finite efficiency score. |
| Coverage under unavailable information | Report candidate-discovery coverage, usable-branch-field coverage, and non-abstaining decision coverage separately. For decisions, coverage = eligible units with a decision / all eligible units; state whether the unit is a PR, unordered pair, or ordered pair. Also report independent-label coverage. |

Precision with no positive predictions and recall with no gold positives are undefined; report numerator/denominator and N/A. Unknown labels are not gold negatives. Method abstentions are not negative labels either, but independently confirmed positives left unreconstructed still count as misses in end-to-end recall. Report any conditional performance restricted to usable observations alongside coverage, never as a replacement for overall performance. No precision/recall or calls-per-correct-stack value can currently be populated from the selected case's descriptive agreement.

## Real-world constraints and provenance

1. **300-event/30-day activity ceiling.** GitHub documents activity timelines as capped at up to 300 events, restricted to the preceding 30 days. This does not cap all PR, issue, or search APIs, and it does not guarantee 30 complete days for a busy account. The existing September PR creations were older than 30 days at the October retrieval. Their metadata was acquired directly, so the current case is not an observed Events API coverage or truncation experiment. [GitHub REST events](https://docs.github.com/en/rest/activity/events).
2. **Missing stack information in activity events.** Handle absent required fields as unavailable. The documented PullRequestEvent payload refers to a nested `pull_request` object and does not explicitly define a native stack field in that section. It does not establish that all nested event objects always omit stack information. Availability must be checked for the specific payload/API version; the current cache contains PR/stack resources, not activity-event responses. Avoid confusing activity events with richer PR resources or webhooks. [GitHub event types](https://docs.github.com/en/rest/using-the-rest-api/github-event-types#pullrequestevent).
3. **Additional request cost.** Detail lookups consume request budget and can add latency. GitHub documents 60 unauthenticated public REST requests/hour, with authentication-dependent and secondary limits. This study has not measured latency or monetary cost. Its original cold collection saved 16 responses: eight PR details and eight filtered stack lookups. Offline replay uses zero network requests. Neither number establishes minimum cost or a validated calls-per-correct-stack metric. [GitHub REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api).
4. **Maintainer feedback about false negatives.** The presenter reports that a maintainer mentioned false negatives in a private Discord conversation. No transcript, specific missed cases, version, or causal explanation was supplied. This is explicitly attributed informal motivation, not a confirmed StackGraph or AgentScan error, an estimate of missed stacks, or a gold label. Account-classification false negatives and stacked-workflow reconstruction misses are different outcomes and must not be conflated. No Discord access or outreach was performed.

The three official documentation extracts are cached in `context_sources.json` with URLs, retrieval dates, and source-response hashes. They are supporting documentation, not a new PR dataset. The private-feedback entry records what is and is not known; it is not presented as independent documentary evidence.

## Current boundary

Preserve the original findings: eight PRs, four verified branch-targeting edges, one five-PR component, three isolates, no cycles; time groups of sizes 2 and 6; one documented five-PR native stack; 32 existing tests; deterministic offline execution. Selection used native/branch information, source metadata is mutable, and there is no independent benchmark. No direct stack-field leakage was found, but concept overlap and sample-selection bias remain. General detection accuracy, algorithmic improvement, budget efficiency, legitimacy, and authorship are unproven. The existing event-only baseline is **not AgentScan's production classifier**, and AgentScan was not run.
