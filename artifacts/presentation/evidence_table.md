# Exact PR and edge evidence

All eight PRs are from `cli/cli`, authored by `williammartin`, and created on 2026-09-04. Times below are exact UTC creation times. Branch refs are case-sensitive; all base and head repositories are `cli/cli`. Membership and branch observations come from the saved 2026-10-28 snapshot, not creation-time reconstruction.

| Exact PR URL | Creation time (UTC) | Base ref | Head ref | Official membership |
| --- | --- | --- | --- | --- |
| [https://github.com/cli/cli/pull/14345](https://github.com/cli/cli/pull/14345) | 2026-09-04T12:13:01Z | `trunk` | `williammartin-issue-13153-plan` | PR stack field absent; filtered lookup returned [] |
| [https://github.com/cli/cli/pull/14346](https://github.com/cli/cli/pull/14346) | 2026-09-04T12:15:46Z | `trunk` | `williammartin-ssh-certificate-authority` | PR stack field absent; filtered lookup returned [] |
| [https://github.com/cli/cli/pull/14347](https://github.com/cli/cli/pull/14347) | 2026-09-04T14:13:21Z | `trunk` | `williammartin-fix-agentic-workflow` | PR stack field absent; filtered lookup returned [] |
| [https://github.com/cli/cli/pull/14348](https://github.com/cli/cli/pull/14348) | 2026-09-04T14:57:13Z | `trunk` | `williammartin-git-real-repo-test-harness` | Stack #14352, position 1/5 |
| [https://github.com/cli/cli/pull/14349](https://github.com/cli/cli/pull/14349) | 2026-09-04T15:10:43Z | `williammartin-git-real-repo-test-harness` | `williammartin-git-graph-tests` | Stack #14352, position 2/5 |
| [https://github.com/cli/cli/pull/14350](https://github.com/cli/cli/pull/14350) | 2026-09-04T15:25:04Z | `williammartin-git-graph-tests` | `williammartin-git-transport-tests` | Stack #14352, position 3/5 |
| [https://github.com/cli/cli/pull/14351](https://github.com/cli/cli/pull/14351) | 2026-09-04T15:36:50Z | `williammartin-git-transport-tests` | `williammartin-improve-git-tests` | Stack #14352, position 4/5 |
| [https://github.com/cli/cli/pull/14355](https://github.com/cli/cli/pull/14355) | 2026-09-04T15:50:28Z | `williammartin-improve-git-tests` | `williammartin-clean-git-test-seams` | Stack #14352, position 5/5 |

## Verified arrows: prerequisite → dependent

For every arrow, the child's base ref and repository equal the parent's head ref and repository. Only one sampled PR has that qualified head. Each pair also has equal SHAs, as recorded below. The program uses repository/ref equality; SHA equality is additional snapshot corroboration, not an input to the graph rule. These observations verify branch targeting, not code-level necessity or authorship.

### E1: #14348 → #14349

- Parent: https://github.com/cli/cli/pull/14348; child: https://github.com/cli/cli/pull/14349.
- Parent `head.repo.full_name` = child `base.repo.full_name` = `cli/cli`.
- Parent `head.ref` = child `base.ref` = `williammartin-git-real-repo-test-harness`.
- Parent `head.sha` = child `base.sha` = `e4995478338ac17dc108c7c30c157437df3b9874`.
- Direction: the child targets the parent's contributed branch; the arrow points from prerequisite to dependent.

### E2: #14349 → #14350

- Parent: https://github.com/cli/cli/pull/14349; child: https://github.com/cli/cli/pull/14350.
- Parent `head.repo.full_name` = child `base.repo.full_name` = `cli/cli`.
- Parent `head.ref` = child `base.ref` = `williammartin-git-graph-tests`.
- Parent `head.sha` = child `base.sha` = `091f872c5516b80296432ba257e7ef19681bfda5`.
- Direction: the child targets the parent's contributed branch; the arrow points from prerequisite to dependent.

### E3: #14350 → #14351

- Parent: https://github.com/cli/cli/pull/14350; child: https://github.com/cli/cli/pull/14351.
- Parent `head.repo.full_name` = child `base.repo.full_name` = `cli/cli`.
- Parent `head.ref` = child `base.ref` = `williammartin-git-transport-tests`.
- Parent `head.sha` = child `base.sha` = `ff5afe556034a6848cb9d408be9e6ae70c4e88db`.
- Direction: the child targets the parent's contributed branch; the arrow points from prerequisite to dependent.

### E4: #14351 → #14355

- Parent: https://github.com/cli/cli/pull/14351; child: https://github.com/cli/cli/pull/14355.
- Parent `head.repo.full_name` = child `base.repo.full_name` = `cli/cli`.
- Parent `head.ref` = child `base.ref` = `williammartin-improve-git-tests`.
- Parent `head.sha` = child `base.sha` = `0c11bdf04bca607bee27ab9ee4cd9eb0c114f2a0`.
- Direction: the child targets the parent's contributed branch; the arrow points from prerequisite to dependent.

## Source mapping and retrieval dates

All 16 saved responses have HTTP 200 and valid payload checksums. The CSV and JSON include all exact SHAs and timestamps. Absence of observed membership does not prove a PR was never stacked.

| PR | Saved PR JSON / UTC retrieval | Saved filtered lookup / UTC retrieval |
| --- | --- | --- |
| #14345 | [67d4e55328bcbaf81b31.json](../../data/cache/67d4e55328bcbaf81b31.json)<br>2026-10-28T05:01:46.795156+00:00 | [d290e9f6f498a1b32d3a.json](../../data/cache/d290e9f6f498a1b32d3a.json)<br>2026-10-28T05:01:48.854289+00:00 |
| #14346 | [2bb23ebc6f29c785f01a.json](../../data/cache/2bb23ebc6f29c785f01a.json)<br>2026-10-28T05:01:50.284642+00:00 | [f7fa34d2f3e3fc7e6577.json](../../data/cache/f7fa34d2f3e3fc7e6577.json)<br>2026-10-28T05:01:51.066046+00:00 |
| #14347 | [623e0b9983f0c82f2f4b.json](../../data/cache/623e0b9983f0c82f2f4b.json)<br>2026-10-28T05:01:52.472191+00:00 | [1d048c0a2fc17d472b0c.json](../../data/cache/1d048c0a2fc17d472b0c.json)<br>2026-10-28T05:01:53.691380+00:00 |
| #14348 | [29785060028927370525.json](../../data/cache/29785060028927370525.json)<br>2026-10-28T05:01:54.704925+00:00 | [e57e814a96573007a974.json](../../data/cache/e57e814a96573007a974.json)<br>2026-10-28T05:01:55.817656+00:00 |
| #14349 | [ea59b94791729e9592f6.json](../../data/cache/ea59b94791729e9592f6.json)<br>2026-10-28T05:01:57.404733+00:00 | [6699f2634e858289b8dc.json](../../data/cache/6699f2634e858289b8dc.json)<br>2026-10-28T05:01:58.859782+00:00 |
| #14350 | [b7353c97c73b6cc84740.json](../../data/cache/b7353c97c73b6cc84740.json)<br>2026-10-28T05:02:00.529681+00:00 | [e2d6155a439ff0034ff8.json](../../data/cache/e2d6155a439ff0034ff8.json)<br>2026-10-28T05:02:01.525640+00:00 |
| #14351 | [b87ccdc4744f087657d9.json](../../data/cache/b87ccdc4744f087657d9.json)<br>2026-10-28T05:02:02.574110+00:00 | [8019240fbcc477edd4c3.json](../../data/cache/8019240fbcc477edd4c3.json)<br>2026-10-28T05:02:03.874771+00:00 |
| #14355 | [cc04b8486aa199badb56.json](../../data/cache/cc04b8486aa199badb56.json)<br>2026-10-28T05:02:05.535690+00:00 | [3b79cf9d23933aeb0b51.json](../../data/cache/3b79cf9d23933aeb0b51.json)<br>2026-10-28T05:02:06.325819+00:00 |

A separate live GET cross-check agreed on all audited fields for 8/8 PRs. The full fresh responses and their own retrieval dates are in `live_metadata_check.json`; the original cache was not refreshed or changed. This live agreement checks the observed API values, not independent research labels.
