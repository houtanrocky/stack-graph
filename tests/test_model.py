"""Synthetic fixtures test logic; they are never presented as research data."""

from dataclasses import replace

import pytest

from stackgraph.model import (PullRequest, dependency_graph, normalize,
                              official_membership, time_groups)


def pr(number, base="main", head=None, repository="lab/project", **changes):
    value = PullRequest(
        id=f"{repository}#{number}", number=number, repository=repository,
        author="researcher", created_at="2026-01-01T12:00:00Z", title="fixture",
        url=f"https://github.com/{repository}/pull/{number}",
        base_repo=repository, base_ref=base,
        head_repo=repository, head_ref=head or f"topic-{number}",
    )
    return replace(value, **changes)


def test_edge_is_prerequisite_to_dependent_even_if_creation_order_is_reversed():
    parent = pr(1, head="foundation", created_at="2026-01-02T12:00:00Z")
    child = pr(2, base="foundation", head="feature")
    graph, info = dependency_graph([child, parent])
    assert set(graph.edges) == {(parent.id, child.id)}
    assert graph.edges[parent.id, child.id]["branch"] == "lab/project:foundation"
    assert info["is_dag"]


def test_chronological_proximity_and_shared_author_do_not_create_edges():
    a, b = pr(1), pr(2)
    graph, info = dependency_graph([a, b])
    assert graph.number_of_edges() == 0
    assert info["isolated_prs"] == [a.id, b.id]
    assert time_groups([a, b])["groups"] == [[a.id, b.id]]


def test_isolated_control_is_kept_beside_a_chain():
    a, b, control = pr(1), pr(2, base="topic-1"), pr(3)
    graph, info = dependency_graph([a, b, control])
    assert set(graph) == {a.id, b.id, control.id}
    assert info["isolated_prs"] == [control.id]


@pytest.mark.parametrize("missing", ["base_repo", "base_ref", "head_repo", "head_ref"])
def test_missing_branch_information_does_not_create_an_edge(missing):
    a, b = pr(1), pr(2, base="topic-1")
    if missing.startswith("head"):
        a = replace(a, **{missing: None})
    else:
        b = replace(b, **{missing: None})
    graph, info = dependency_graph([a, b])
    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 0
    assert any("missing" in message for message in info["warnings"])


def test_equal_branch_names_in_different_forks_do_not_match():
    a = pr(1, head="feature", head_repo="alice/project")
    b = pr(2, base="feature", base_repo="bob/project")
    graph, _ = dependency_graph([a, b])
    assert graph.number_of_edges() == 0


def test_ambiguous_reused_head_branches_are_not_arbitrarily_resolved():
    a, b, c = pr(1, head="reused"), pr(2, head="reused"), pr(3, base="reused")
    graph, info = dependency_graph([a, b, c])
    assert graph.number_of_edges() == 0
    assert any("ambiguous" in message for message in info["warnings"])


def test_cycle_is_preserved_and_flagged_instead_of_silently_repaired():
    a, b = pr(1, base="b", head="a"), pr(2, base="a", head="b")
    graph, info = dependency_graph([a, b])
    assert set(graph.edges) == {(a.id, b.id), (b.id, a.id)}
    assert not info["is_dag"]
    assert info["cycle_components"] == [[a.id, b.id]]


def test_self_target_does_not_become_a_dependency():
    a = pr(1, base="same", head="same")
    graph, info = dependency_graph([a])
    assert graph.number_of_edges() == 0
    assert any("self-targeting" in message for message in info["warnings"])


def test_duplicate_pr_is_rejected():
    with pytest.raises(ValueError, match="Duplicate PR"):
        dependency_graph([pr(1), pr(1)])


def test_normalization_handles_deleted_fork_and_casefolds_repository_only():
    raw = {"number": 1, "html_url": "https://github.com/Lab/Project/pull/1",
           "head": {"ref": "Topic", "repo": None},
           "base": {"ref": "Main", "repo": {"full_name": "Lab/Project"}}}
    result = normalize(raw, "Lab/Project")
    assert result.base_repo == "lab/project"
    assert result.base_ref == "Main"
    assert result.head_repo is None
    assert result.author is None


def test_changing_official_metadata_cannot_change_C():
    raw = {"number": 1, "html_url": "https://github.com/lab/project/pull/1",
           "head": {"ref": "a", "repo": {"full_name": "lab/project"}},
           "base": {"ref": "main", "repo": {"full_name": "lab/project"}}}
    original = normalize(raw, "lab/project")
    raw.update(stack={"number": 99, "position": 4}, body="Depends on #7", labels=["stack"])
    assert normalize(raw, "lab/project") == original
    graph, _ = dependency_graph([normalize(raw, "lab/project"), pr(2)])
    assert graph.number_of_edges() == 0


def test_time_groups_use_successive_gaps_include_boundary_and_sort_inputs():
    values = [pr(3, created_at="2026-01-01T14:00:00Z"),
              pr(1), pr(2, created_at="2026-01-01T13:00:00Z")]
    assert time_groups(values)["groups"] == [["lab/project#1", "lab/project#2", "lab/project#3"]]


@pytest.mark.parametrize("date", [None, "bad", "2026-01-01T12:00:00"])
def test_missing_or_invalid_time_is_unknown(date):
    a = pr(1, created_at=date)
    assert time_groups([a])["unknown_time"] == [a.id]
    assert time_groups([a])["groups"] == []


def test_time_groups_do_not_cross_repositories():
    assert len(time_groups([pr(1), pr(2, repository="lab/other")])["groups"]) == 2


def lookup(data=None, status=200, next_page=None):
    return {"data": [] if data is None else data, "http_status": status, "next_page": next_page}


def test_official_missing_field_and_404_are_unknown():
    result = official_membership([{"number": 1}], [lookup(status=404)], "lab/project")
    assert result["statuses"]["lab/project#1"] == "unknown"


def test_official_successful_empty_lookup_is_observed_absence():
    result = official_membership([{"number": 1}], [lookup()], "lab/project")
    assert result["statuses"]["lab/project#1"] == "no_membership_observed"


def test_official_null_is_distinct_from_missing():
    result = official_membership([{"number": 1, "stack": None}], [lookup(status=403)], "lab/project")
    assert result["statuses"]["lab/project#1"] == "explicit_null"


def test_official_membership_is_read_from_native_endpoint_when_field_missing():
    data = [{"number": 12, "pull_requests": [{"number": 1}, {"number": 2}]}]
    result = official_membership([{"number": 1}], [lookup(data)], "lab/project")
    assert result["groups"] == {"lab/project/stack/12": ["lab/project#1"]}


def test_conflicting_official_sources_are_flagged():
    data = [{"number": 12, "pull_requests": [{"number": 1}]}]
    result = official_membership([{"number": 1, "stack": {"number": 13}}], [lookup(data)], "lab/project")
    assert not result["groups"]
    assert result["statuses"]["lab/project#1"] == "conflicting_membership"


def test_incomplete_pagination_does_not_establish_absence():
    result = official_membership([{"number": 1}], [lookup(next_page="https://example.test/page2")], "lab/project")
    assert result["statuses"]["lab/project#1"] == "unknown"
