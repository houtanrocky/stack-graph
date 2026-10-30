"""Three deliberately separate comparisons. Only C produces dependency edges."""

from dataclasses import asdict, dataclass
from datetime import datetime
from itertools import combinations

import networkx as nx


@dataclass(frozen=True)
class PullRequest:
    id: str
    number: int
    repository: str
    author: str | None
    created_at: str | None
    title: str
    url: str
    base_repo: str | None
    base_ref: str | None
    head_repo: str | None
    head_ref: str | None

    def as_dict(self):
        return asdict(self)


def normalize(raw, repository):
    def branch(side):
        value = raw.get(side) or {}
        repo = (value.get("repo") or {}).get("full_name")
        return repo.casefold() if repo else None, value.get("ref")

    base_repo, base_ref = branch("base")
    head_repo, head_ref = branch("head")
    repository = repository.casefold()
    number = raw["number"]
    return PullRequest(
        f"{repository}#{number}", number, repository,
        (raw.get("user") or {}).get("login"), raw.get("created_at"),
        raw.get("title", ""), raw["html_url"],
        base_repo, base_ref, head_repo, head_ref,
    )


def time_groups(prs, window_minutes=60):
    """A: simplified creation-gap heuristic, not AgentScan; no authors/branches."""
    if window_minutes <= 0:
        raise ValueError("window_minutes must be positive")
    by_repo = {}
    missing = []
    for pr in prs:
        try:
            date = datetime.fromisoformat(pr.created_at.replace("Z", "+00:00"))
            if date.tzinfo is None:
                raise ValueError("timezone required")
        except (AttributeError, TypeError, ValueError):
            missing.append(pr.id)
            continue
        by_repo.setdefault(pr.repository, []).append((date, pr.id))
    groups = []
    for repo in sorted(by_repo):
        previous = None
        for date, key in sorted(by_repo[repo]):
            if previous is None or (date - previous).total_seconds() > window_minutes * 60:
                groups.append([])
            groups[-1].append(key)
            previous = date
    return {"window_minutes": window_minutes, "groups": groups, "unknown_time": sorted(missing)}


def official_membership(raw_prs, lookup_snapshots, repository):
    """B: membership only. Missing fields and failed API lookups remain unknown."""
    groups, statuses, warnings = {}, {}, []
    for raw, snapshot in zip(raw_prs, lookup_snapshots, strict=True):
        key = f"{repository.casefold()}#{raw['number']}"
        membership = raw.get("stack")
        stack_numbers = set()
        if isinstance(membership, dict) and isinstance(membership.get("number"), int):
            stack_numbers.add(membership["number"])
        lookup_ok = snapshot["http_status"] == 200 and isinstance(snapshot["data"], list)
        if lookup_ok:
            for stack in snapshot["data"]:
                if any(p.get("number") == raw["number"] for p in stack.get("pull_requests", [])):
                    stack_numbers.add(stack["number"])
        if len(stack_numbers) > 1:
            statuses[key] = "conflicting_membership"
            warnings.append(f"{key}: conflicting official stack numbers")
        elif stack_numbers:
            number = stack_numbers.pop()
            groups.setdefault(f"{repository.casefold()}/stack/{number}", []).append(key)
            statuses[key] = "member"
            if lookup_ok and not snapshot["data"]:
                warnings.append(f"{key}: PR stack field disagrees with empty lookup")
        elif lookup_ok and not snapshot["next_page"] and not snapshot["data"]:
            statuses[key] = "no_membership_observed"
        elif "stack" in raw and membership is None:
            statuses[key] = "explicit_null"
        else:
            statuses[key] = "unknown"
    return {"groups": {k: sorted(v) for k, v in sorted(groups.items())},
            "statuses": statuses, "warnings": warnings}


def dependency_graph(prs):
    """C: prerequisite -> dependent iff qualified head == qualified base, uniquely."""
    graph = nx.DiGraph()
    warnings = []
    heads = {}
    for pr in prs:
        if pr.id in graph:
            raise ValueError(f"Duplicate PR: {pr.id}")
        graph.add_node(pr.id, **pr.as_dict())
        if pr.head_repo and pr.head_ref:
            heads.setdefault((pr.head_repo, pr.head_ref), []).append(pr.id)
        else:
            warnings.append(f"{pr.id}: missing head repository/ref")
    for child in prs:
        if not child.base_repo or not child.base_ref:
            warnings.append(f"{child.id}: missing base repository/ref")
            continue
        matches = heads.get((child.base_repo, child.base_ref), [])
        if len(matches) > 1:
            warnings.append(f"{child.id}: ambiguous base matches {sorted(matches)}; no edge added")
        elif matches and matches[0] != child.id:
            graph.add_edge(matches[0], child.id,
                           evidence="repository-qualified head == base",
                           branch=f"{child.base_repo}:{child.base_ref}")
        elif matches:
            warnings.append(f"{child.id}: self-targeting branch; no self edge added")
    cycles = sorted(sorted(c) for c in nx.strongly_connected_components(graph) if len(c) > 1)
    return graph, {"warnings": warnings, "cycle_components": cycles,
                   "is_dag": nx.is_directed_acyclic_graph(graph),
                   "isolated_prs": sorted(nx.isolates(graph))}


def co_membership_pairs(groups):
    """Unordered pairs for descriptive comparison only, never dependency edges."""
    return sorted({tuple(sorted(pair)) for group in groups for pair in combinations(group, 2)})
