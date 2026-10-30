# A 90-second presentation script

198 words; rehearse aloud and leave a short pause while showing the existing graph. At roughly 140 words per minute, the text takes about 85 seconds before pauses.

> My question is: To what extent can dependency-graph information improve the identification of stacked pull-request workflows compared with event-based heuristics, under constrained GitHub API access?
>
> The prototype examines one selected case: eight public PRs, four verified branch-targeting edges, and three isolated controls. Thirty-two tests pass, and offline execution is reproducible.
>
> The timing heuristic mixes separate work with a five-PR chain. The graph exposes order, but detection accuracy remains unproven. This baseline is not AgentScan's production classifier.
>
> I want to separate information value, algorithm value, and budget value. Does dependency metadata help beyond timing? Do graph algorithms add anything beyond rules using identical metadata? What survives when API access is restricted?
>
> The proposed comparison is event-only grouping, enriched metadata rules, and graph analysis under matched enrichment budgets. Equal algorithm performance is a valid result.
>
> I would measure membership and edge precision and recall, requests per correctly reconstructed stack, and coverage under missing information.
>
> Activity feeds have a 300-event, 30-day ceiling; needed stack information may be missing. Informal Discord feedback about false negatives motivates the question but provides no evaluation labels.
>
> The next decision is a precise target and independent adjudication. The current graph establishes neither legitimacy nor human authorship.

Use the existing [graph](../graph.pdf). Definitions, budget accounting, caveats, and sources are in [evaluation_plan.md](evaluation_plan.md). The reported Discord feedback is private communication relayed by the presenter, not an archived or independently verified error report. Do not claim a measured AgentScan false negative or a graph-algorithm improvement.
