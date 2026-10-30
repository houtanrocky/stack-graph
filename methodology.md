# Methodology

## Question and scope

The question is whether verified PR dependency relationships provide context beyond chronological event activity when identifying legitimate stacked-PR workflows. This prototype tests the narrower, observable question: can a branch-derived graph distinguish an explicitly layered workflow from nearby PR creation activity? It does not operationalize legitimacy as a measurable label. A graph can show organization without establishing that code or contributor behavior is legitimate.

The unit is a public GitHub pull request. Eight PRs from `cli/cli`, all created on 2026-09-04 by the same account, form a deliberately small case study. Creation times are historical events; base/head refs and stack membership are mutable observations at retrieval. This is not a reconstruction of the repository at creation time.

## Sampling and verification

The public [repository Stacks API](https://api.github.com/repos/cli/cli/stacks?per_page=10) was inspected during discovery. Open stack `cli/cli` stack number `14352` supplied PRs `14348`, `14349`, `14350`, `14351`, and `14355`. These are a purposively selected positive example. Discovery queries are not used by the analysis; the runner fetches and saves a filtered official lookup for every sampled PR.

Controls `14345`, `14346`, and `14347` were selected as nearby same-author creation events with distinct head branches targeting `trunk`. Their subjects are clipboard configuration, SSH clone URLs, and Go-update automation. Matching repository, author, and day reduces obvious differences while retaining a time baseline that can conflate distinct work. Selection used branch information and official membership, so these controls cannot serve as independent evaluation labels. They are structural non-stack controls at the saved snapshot. Their complete historical workflow status and possible semantic dependencies are unknown.

The stacked example is verified in a limited, auditable sense: the saved native metadata identifies the stack, the branch fields form a four-edge chain, and explicit PR body statements describe the layers. For example, [PR 14349](https://github.com/cli/cli/pull/14349) states that PR 14348 supplies its shared test harness. `analysis.json` records selected corroborating excerpts and checks their presence in cached bodies. This corroboration does not amount to independent blinded adjudication or code-level dependency analysis.

## Acquisition and provenance

For every identifier in `data/sample.json`, the runner makes two read-only requests:

```text
GET https://api.github.com/repos/cli/cli/pulls/NUMBER
GET https://api.github.com/repos/cli/cli/stacks?pull_request=NUMBER&per_page=100
```

It requests API version `2026-03-10`. Each cache file wraps the complete parsed response JSON with the requested URL, UTC retrieval timestamp, HTTP status, response Date, ETag when present, pagination link, API version, and SHA-256 of canonicalized response data. This preserves metadata including creation time, author, repository, base/head refs and repositories, and any native stack object. It stores parsed JSON, not byte-for-byte HTTP payloads; tokens and request authorization headers are excluded. SHA-256 detects accidental changes, not source authenticity or malicious alteration of both payload and checksum.

HTTP errors are retained as evidence. A failed PR fetch aborts the example. A failed stack lookup leaves official membership unknown unless the PR resource itself supplies it; 404/403 never becomes an empty stack. A successful, complete empty filtered response means no membership was observed at retrieval. An absent `stack` key is distinguished from explicit null. Conflicting nonempty official memberships are flagged and excluded from grouped membership. Positive evidence with an empty lookup is retained with a warning because the two requests may observe different states. Partial pagination cannot establish absence.

Sources are fetched sequentially and are not an atomic repository snapshot. API caching and edits during collection can cause inconsistencies. Offline mode verifies checksums and forbids HTTP; refresh archives previous snapshots. The offline run uses the active cache entries; a refresh changes that active set. Requests use bounded timeouts and limited retries for transient server errors.

## A: chronological creation-event grouping

Within each repository, sort PRs by creation time, breaking ties by PR identity. Put the next event in the same group when its gap from the previous event is at most 60 minutes; otherwise start a new group. This is single-link grouping: repeated short gaps can create a group lasting longer than one hour. Missing or invalid timestamps remain unknown and are not grouped.

A uses no author, branch, stack, or PR-body data. Its outputs are unordered activity groups, never dependency edges. The one-hour threshold is a transparent illustrative choice, not fitted to labels. The report also shows 15- and 180-minute thresholds. It includes only the sampled PR creation events, not all repository events, commits, comments, or updates. Selection can therefore change observed gaps.

This is a **simplified heuristic, not an AgentScan implementation or reproduction**. The local function `time_groups` performs only chronological grouping. There is no AgentScan dependency, account-profile scoring, event-detector suite, or account-classification output. The [AgentScan project](https://github.com/MatteoGabriele/agentscan) identifies [unveil-project/identity](https://github.com/unveil-project/identity) as its account-activity analysis library. Those upstream descriptions were checked during this audit; neither system was run here. These results cannot establish an improvement over AgentScan or an AgentScan false positive.

## B: explicit GitHub stack membership

Read the PR resource's native `stack` object when present and the filtered official Stacks API. Group sampled PRs by repository and stack number; report membership, no membership observed, explicit null, unknown, or conflicting membership. Preserve positions and other metadata in the raw cache. B reports membership only: co-membership does not imply an edge between every pair.

GitHub documents the [native stack API](https://docs.github.com/en/pull-requests/reference/stacked-pull-requests-apis-and-webhooks) and [REST endpoints](https://docs.github.com/en/rest/pulls/stacks). This experiment does not treat third-party text such as a `ghstack` body block as official GitHub metadata.

## C: directed branch dependency graph

Use NetworkX `DiGraph`. Keep every sampled PR as a node, including controls and incomplete observations. For distinct PRs P and Q, add:

```text
P → Q  iff  (P.head.repository, P.head.ref) == (Q.base.repository, Q.base.ref)
```

The arrow means **prerequisite → dependent**: Q targets the branch contributed by P. Both repository and ref must be known. Repository names are case-insensitive; branch names retain case. A shared name in different forks is insufficient. If multiple PRs expose the same qualified head branch, matching is ambiguous and no edge is added for that base. Self-targeting refs are flagged without a self edge. Duplicate PR identifiers are rejected.

Creation time is never used to construct, orient, or disambiguate an edge. Nor are author identity, titles, bodies, official stack labels, stack positions, or official group membership. Node metadata can be displayed without contributing to topology. Each edge stores its matching branch as evidence.

An edge verifies branch targeting in the sampled metadata, not a semantic need for another PR's code. Branch reuse across history can mislead this rule even with a unique observed match. Rebased, retargeted, deleted, fork-based, or third-party stack workflows may not be recovered. No commit-ancestry fetch or historical branch reconstruction is performed. Failure to recover an edge does not establish independence.

The presentation audit checks each edge directly against the two raw PR resources, including exact `head.repo.full_name`, `head.ref`, `base.repo.full_name`, and `base.ref` values. All four observed edges additionally have equal parent-head and child-base SHAs in the saved metadata. SHA equality is corroboration found during the audit, not an extra edge-generation rule or an independent label.

Weakly connected components are groups joined when arrow direction is ignored. They allow an unordered descriptive comparison with A and B. A directed acyclic graph (DAG) has no directed cycles and can represent a consistent prerequisite ordering. Cycles are retained and flagged using strongly connected components, rather than repaired or mistaken for a valid ordered stack. The figure uses a topological layout for DAG components and a circular layout for cyclic ones.

## Comparison and evaluation policy

Report group memberships, directed edges, isolated nodes, cycles, and unordered co-membership pair counts. For C, co-membership uses weak components; these pairs include indirect connections and are not direct dependency edges. B and C agreement is reported descriptively, without labeling disagreements as classification errors.

Official metadata helped select the sample and defines B. C uses fields available independently of stack metadata, but GitHub's [stack definition](https://docs.github.com/en/pull-requests/get-started/about-stacked-prs) itself uses branch chaining. Thus the input sources are separate while the concepts remain related. Agreement cannot be interpreted as independent validation of either method. Author statements were read after selection and are also not independent labels.

**No precision or recall is computed.** The JSON evaluation fields are null, with a reason. A future evaluation would need a larger sample collected without selecting only known stacks; a predeclared target (ordered dependency edge, stack co-membership, or another explicit task); independent positive and negative labels from blinded maintainer review or code/history inspection; recorded evidence and uncertainty; and a held-out evaluation. The same native membership must not be used both as model input and independent ground truth. Unknowns must not be silently converted to negatives.

## Authorship and limitations

Workflow structure is distinct from AI authorship. Saved PR bodies can contain self-disclosures, but StackGraph does not parse them into features or labels. Neither clustered activity nor a well-formed stack proves human or AI authorship. A coherent workflow also does not prove benign intent, code quality, or legitimacy.

One repository, one author, one selected stack, three selected controls, no historical reconstruction, and no independent benchmark sharply limit inference. The example can demonstrate additional descriptive context beyond the chosen time baseline. Any broader claim about detection accuracy or legitimate workflows remains **inconclusive**.
