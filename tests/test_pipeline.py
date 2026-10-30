"""Regression of the bundled real snapshot, not independent label evaluation."""

import json
import copy
from pathlib import Path

from stackgraph.__main__ import analyze
from stackgraph.source import GitHubCache


ROOT = Path(__file__).resolve().parents[1]


def test_bundled_real_snapshot_replays_offline_with_expected_observations(monkeypatch):
    manifest = json.loads((ROOT / "data/sample.json").read_text(encoding="utf-8"))
    cache = GitHubCache(ROOT / "data/cache", offline=True)
    def forbidden(*args, **kwargs):
        raise AssertionError("Bundled example test must never use the network")
    monkeypatch.setattr(cache.session, "get", forbidden)
    result, graph = analyze(manifest, cache)
    expected = [(14348, 14349), (14349, 14350), (14350, 14351), (14351, 14355)]
    assert set(graph.edges) == {(f"cli/cli#{a}", f"cli/cli#{b}") for a, b in expected}
    assert result["C_branch_graph"]["isolated_prs"] == [f"cli/cli#{n}" for n in (14345, 14346, 14347)]
    assert result["C_branch_graph"]["is_dag"]
    assert result["B_official"]["groups"] == {
        "cli/cli/stack/14352": [f"cli/cli#{n}" for n in (14348, 14349, 14350, 14351, 14355)]}
    assert result["descriptive_agreement"]["A_pair_count"] == 16
    assert result["descriptive_agreement"]["C_component_pair_count"] == 10
    assert all(e["found_in_cached_body"] for e in result["author_statement_corroboration"])
    assert len(result["sources"]) == 16
    assert all(s["http_status"] == 200 for s in result["sources"])
    assert cache.network_requests == 0
    assert cache.cache_hits == 16
    assert result["evaluation"]["precision"] is None
    assert result["evaluation"]["recall"] is None
    assert result["evaluation"]["independently_validated_labels"] is False


def test_real_graph_and_time_groups_survive_official_metadata_ablation():
    manifest = json.loads((ROOT / "data/sample.json").read_text(encoding="utf-8"))
    original, _ = analyze(manifest, GitHubCache(ROOT / "data/cache", offline=True))

    class WithoutOfficialMetadata(GitHubCache):
        def get(self, api_path):
            snapshot = copy.deepcopy(super().get(api_path))
            if "/stacks?" in api_path:
                snapshot["data"] = []
            else:
                snapshot["data"].pop("stack", None)
                snapshot["data"]["body"] = ""
                snapshot["data"]["labels"] = []
            return snapshot

    changed_manifest = copy.deepcopy(manifest)
    changed_manifest["stack_candidates"], changed_manifest["structural_controls"] = (
        manifest["structural_controls"], manifest["stack_candidates"])
    changed, _ = analyze(changed_manifest, WithoutOfficialMetadata(ROOT / "data/cache", offline=True))
    assert original["B_official"]["groups"]
    assert not changed["B_official"]["groups"]
    assert changed["C_branch_graph"] == original["C_branch_graph"]
    assert changed["A_time_only"] == original["A_time_only"]
    assert changed["evaluation"] == original["evaluation"]
