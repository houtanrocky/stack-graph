# Presentation notes

## A 90-second explanation

Approximately 200 words. Rehearse once aloud and pause while pointing to the chain.

“StackGraph asks whether PR dependency structure gives useful context beyond activity timing. This is an exploratory case study of eight public pull requests from one repository and one author.

I compare three views. First, a simple heuristic groups sampled PR creation events when successive gaps are at most one hour. This is not AgentScan; I have not run AgentScan. Second, I read GitHub's native stack membership. Third, I build a directed graph from repository-qualified base and head branches.

An arrow goes from a prerequisite PR to the PR targeting its branch. The four arrows here are verified against raw branch metadata, with matching commit SHAs as additional corroboration. They form a five-PR chain, while three controls remain isolated within the sample.

The one-hour heuristic mixes one control with the five stack members and also groups the other two controls. The graph therefore supplies order and concrete branch evidence that timing alone lacks.

The limitation is that I deliberately selected a known stack. Agreement with GitHub membership is descriptive, not independent validation. There are no accuracy estimates, and this says nothing about human authorship or workflow legitimacy. My next experiment would use predeclared sampling windows and independently adjudicated workflow labels.”

## Five difficult questions and accurate answers

**1. Isn't the agreement between B and C circular?**

There is conceptual overlap and selection bias. GitHub's stack definition itself uses branch chains, and official metadata helped select this case. The graph code does not read stack labels: `normalize` excludes them, and `dependency_graph` only matches qualified refs. Removing official metadata, body text, and manifest role assignments leaves C unchanged in the added real-snapshot regression. That demonstrates input separation, not independent validation. B–C agreement cannot establish accuracy or generalization.

**2. Does a branch match prove a dependency, and why does the arrow point that way?**

It proves an observed targeting relationship under our operational definition. For E1, PR 14349's base repository/ref equals PR 14348's head repository/ref, so the arrow is 14348 → 14349: prerequisite → dependent. The saved SHAs also agree. This does not prove code-level necessity or causal influence. Reused refs, retargeting, and unobserved history can mislead us. Cycles would be retained and flagged rather than forced into a DAG; this sample has none.

**3. Did you reproduce AgentScan? Why choose one hour?**

No. A is a simplified repository-local creation-gap heuristic; AgentScan's account-level scoring library was neither imported nor run. The hour is an illustrative threshold, not an optimized or validated parameter. At 15, 60, and 180 minutes, A produces 3, 2, and 1 groups respectively. Only eight sampled creation events enter A, so sampling itself affects the gaps. This study cannot support an AgentScan performance comparison or an AgentScan false-positive claim.

**4. Are the controls true negatives? Are the six extra pairs false positives?**

They are structural controls at retrieval: distinct heads, `trunk` bases, and successful empty official stack lookups. We have not independently established their historical status or semantic independence. Six time-grouped pairs cross graph components: five pair control 14347 with stack members, and one pairs controls 14345 and 14346. They are descriptive disagreements, not validated errors. Also distinguish four direct graph edges from ten unordered co-component pairs. Precision/recall require an independently defined target and adjudicated positive/negative labels.

**5. What is the Network Science contribution, and what can you claim from eight nodes?**

The contribution here is an auditable representation: direction expresses branch prerequisites; reachability expresses indirect ordering; weak components separate connected work; isolates and cycle checks expose boundaries or inconsistent ordering. This is a small demonstration, not a novel detection algorithm or statistical result. It establishes neither legitimacy nor human authorship. The next experiment should freeze the rules, sample all PRs in predeclared repository/date windows, and obtain independent intentional-stack co-membership labels, keeping uncertain cases unknown. Only then would predictive evaluation be appropriate.

## What to show and what to say

Open `graph.pdf` while speaking; give the professor `research_brief.pdf`. Keep `evidence_table.md` available for exact URLs, times, refs, and SHAs. Use “verified branch-targeting relationship,” “selected case,” and “descriptive agreement.” Avoid “validated detector,” “AgentScan false positive,” “six classification errors,” and “a stack proves a human wrote it.” The broad detection claim remains inconclusive.
