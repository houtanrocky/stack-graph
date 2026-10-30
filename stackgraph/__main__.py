"""Run with python -m stackgraph; default analysis reuses the fixed public sample."""

import argparse
import importlib.metadata
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import networkx as nx

from .model import (co_membership_pairs, dependency_graph, normalize,
                    official_membership, time_groups)
from .plot import draw_graph
from .source import GitHubCache


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def analyze(manifest, cache):
    repository = manifest["repository"]
    raw_prs, stack_snapshots = [], []
    for number in manifest["pull_requests"]:
        snapshot = cache.get(f"/repos/{repository}/pulls/{number}")
        if snapshot["http_status"] != 200:
            raise RuntimeError(f"PR retrieval failed: {snapshot['source_url']} (HTTP {snapshot['http_status']})")
        raw_prs.append(snapshot["data"])
        stack_snapshots.append(cache.get(
            f"/repos/{repository}/stacks?pull_request={number}&per_page=100"))
    prs = [normalize(raw, repository) for raw in raw_prs]
    graph, diagnostics = dependency_graph(prs)
    a = time_groups(prs)
    b = official_membership(raw_prs, stack_snapshots, repository)
    components = sorted((sorted(c) for c in nx.weakly_connected_components(graph)),
                        key=lambda c: (-len(c), c))
    pairs_a = set(co_membership_pairs(a["groups"]))
    pairs_b = set(co_membership_pairs(b["groups"].values()))
    pairs_c = set(co_membership_pairs(components))
    # These are agreement counts, not independent predictive performance.
    agreement = {"A_pair_count": len(pairs_a), "B_pair_count": len(pairs_b),
                 "C_component_pair_count": len(pairs_c),
                 "A_pairs_outside_C_components": sorted(pairs_a - pairs_c),
                 "C_pairs_not_grouped_by_A": sorted(pairs_c - pairs_a),
                 "B_C_common_pairs": len(pairs_b & pairs_c),
                 "B_C_disagreeing_pairs": sorted(pairs_b ^ pairs_c)}
    # Short, explicitly selected author statements corroborate the case; they
    # are not algorithm inputs or an independently adjudicated evaluation set.
    anchors = {14349: "PR #14348 provides the shared real-repository harness this layer builds on.",
               14350: "This is layer 3 above draft PR #14349",
               14351: "Parent draft: #14350.",
               14355: "This is the final code layer above draft PR #14351."}
    corroboration = [{"pr": pr.id, "source_url": pr.url,
                      "excerpt": anchors[pr.number],
                      "found_in_cached_body": anchors[pr.number] in (raw.get("body") or "")}
                     for pr, raw in zip(prs, raw_prs, strict=True)
                     if pr.number in anchors and repository.casefold() == "cli/cli"]
    return {
        "sample": manifest,
        "pull_requests": [p.as_dict() for p in prs],
        "A_time_only": a,
        "A_sensitivity": [time_groups(prs, w) for w in (15, 60, 180)],
        "B_official": b,
        "C_branch_graph": {
            "node_count": graph.number_of_nodes(), "edge_count": graph.number_of_edges(),
            "edges": [{"prerequisite": u, "dependent": v, **d}
                      for u, v, d in sorted(graph.edges(data=True))],
            "weak_components": components, **diagnostics,
        },
        "descriptive_agreement": agreement,
        "author_statement_corroboration": corroboration,
        "evaluation": {
            "independently_validated_labels": False,
            "precision": None, "recall": None,
            "reason": "No independent, blinded, positive-and-negative adjudication set is available. Official membership and branch matching are structurally related; their agreement is not independent validation.",
            "conclusion": "Branch relationships provide additional descriptive workflow structure in this selected case. General identification performance and workflow legitimacy remain inconclusive.",
        },
        "sources": cache.sources,
    }, graph


def render_results(result):
    a, b, c = (result[k] for k in ("A_time_only", "B_official", "C_branch_graph"))
    agreement = result["descriptive_agreement"]
    creation_dates = sorted({p["created_at"][:10] for p in result["pull_requests"] if p["created_at"]})
    def short(nodes):
        return ", ".join(f"#{n.split('#')[-1]}" for n in nodes)
    lines = ["# StackGraph results", "",
             "This is a purposive public-data case study, not a performance benchmark. "
             "General identification performance and workflow legitimacy are **inconclusive**.", "",
             f"Sample: {len(result['pull_requests'])} PRs from `{result['sample']['repository']}`. "
             f"Observed creation dates: {', '.join(creation_dates) or 'unknown'}. "
             "Branch relationships and stack membership are retrieval-time snapshots.", "",
             "## Three comparisons", "",
             "| Comparison | Observed output |", "| --- | --- |",
             f"| A: simplified time heuristic, 60-minute successive gaps | {len(a['groups'])} groups; {agreement['A_pair_count']} unordered co-grouped pairs |",
             f"| B: official GitHub stack membership | {len(b['groups'])} observed stack(s); {agreement['B_pair_count']} unordered co-member pairs |",
             f"| C: branch-derived targeting graph | {c['node_count']} nodes, {c['edge_count']} directed edges; {len(c['weak_components'])} weak components |", "",
             "A is a simplified creation-time grouping heuristic, not AgentScan or its identity scoring logic. "
             "AgentScan was not run; this is not a comparison of AgentScan classifications or detection accuracy.", "",
             "A's groups:", ""]
    lines += [f"- {short(g)}" for g in a["groups"]]
    lines += ["", "B's official memberships:", ""]
    lines += [f"- `{stack}`: {short(nodes)}" for stack, nodes in b["groups"].items()]
    lines += [f"- {key}: `{status}`" for key, status in b["statuses"].items() if status != "member"]
    lines += ["", "C's edges (prerequisite → dependent):", ""]
    lines += [f"- {edge['prerequisite']} → {edge['dependent']}; equal branch `{edge['branch']}`."
              for edge in c["edges"]]
    lines += ["", f"Isolated within this sample: {short(c['isolated_prs'])}. "
              f"DAG: {c['is_dag']}. Cycle components: {len(c['cycle_components'])}.", "",
              f"A groups {len(agreement['A_pairs_outside_C_components'])} pairs that C places in different components. "
              f"C has {len(agreement['C_pairs_not_grouped_by_A'])} component pairs separated by A. "
              f"B and C share {agreement['B_C_common_pairs']} co-membership pairs, with "
              f"{len(agreement['B_C_disagreeing_pairs'])} disagreements. These counts describe agreement, not accuracy.", "",
              "## Sensitivity of the time baseline", "",
              "| Maximum successive gap (minutes) | Groups | Co-grouped pairs |", "| --- | --- | --- |"]
    lines += [f"| {entry['window_minutes']} | {len(entry['groups'])} | {len(co_membership_pairs(entry['groups']))} |"
              for entry in result["A_sensitivity"]]
    lines += ["", "The thresholds are illustrative and were not optimized. Single-link groups can span longer than the gap threshold. "
              "Only sampled creation events are included; this is not a complete repository event stream.", "",
              "## Evidence and interpretation", "",
              "The official membership and branch graph are shown above. The following selected author statements "
              "provide additional case context; each presence flag is checked against the saved body. "
              "Text was inspected after case selection and is not a model input or an independent label set.", ""]
    for evidence in result["author_statement_corroboration"]:
        lines.append(f"- [{evidence['pr']}]({evidence['source_url']}): `{evidence['excerpt']}` "
                     f"(present in saved body: {evidence['found_in_cached_body']}).")
    lines += ["", "The manifest designates the following structural controls:", "",
              "| PR | Subject | Base | Official status |", "| --- | --- | --- | --- |"]
    lines += [f"| [#{p['number']}]({p['url']}) | {p['title']} | `{p['base_ref']}` | `{b['statuses'][p['id']]}` |"
              for p in result["pull_requests"] if p["number"] in result["sample"].get("structural_controls", [])]
    lines += ["", "These are snapshot-specific structural controls, not independently established historical negatives. "
              "No claim is made that they lack all semantic dependencies.", "",
              "C adds an order and a concrete branch reason for each connection that A cannot supply. "
              "The observed agreement with B is expected from GitHub's branch-chain definition; it cannot establish predictive accuracy. "
              "No independently validated labels are available, so **precision and recall are not reported** (JSON values are null). "
              "This small selected example supports descriptive usefulness only. It cannot show general detection performance, "
              "maintainer intent, code quality, or whether a workflow is legitimate.", "",
              "Workflow structure and AI authorship are separate questions. Some saved PR bodies contain authorship disclosures; "
              "the pipeline does not parse or score them. Timing, graph position, or stack membership cannot establish AI authorship.", "",
              "![Branch-derived graph](artifacts/graph.png)", "",
              "## Provenance", "",
              "Every source body is saved under `data/cache/`, with retrieval time, HTTP status, source URL, "
              "API version, and a SHA-256 checksum. `artifacts/analysis.json` contains the complete normalized comparison. "
              "`artifacts/execution.json` records the last run and package versions. "
              "[validation.md](validation.md) records executed checks and their observed outcomes.", "",
              "| Source | Retrieved (UTC) | HTTP |", "| --- | --- | --- |"]
    lines += [f"| [API JSON]({s['source_url']}) | {s['retrieved_at']} | {s['http_status']} |" for s in result["sources"]]
    lines += ["", "## Diagnostics", ""]
    warnings = c["warnings"] + b["warnings"]
    lines += [f"- {warning}" for warning in warnings] or ["No graph or membership warnings."]
    return "\n".join(lines) + "\n"


def main():
    started_at = datetime.now(timezone.utc).isoformat()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sample", type=Path, default=Path("data/sample.json"))
    parser.add_argument("--cache", type=Path, default=Path("data/cache"))
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    parser.add_argument("--results", type=Path, default=Path("results.md"))
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="Require the cache; never contact GitHub")
    mode.add_argument("--refresh", action="store_true", help="Fetch a new snapshot and archive old cache entries")
    args = parser.parse_args()
    manifest = json.loads(args.sample.read_text(encoding="utf-8"))
    cache = GitHubCache(args.cache, offline=args.offline, refresh=args.refresh)
    result, graph = analyze(manifest, cache)
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / "analysis.json", result)
    draw_graph(graph, args.output / "graph.png")
    args.results.write_text(render_results(result), encoding="utf-8")
    execution = {
        "started_at": started_at,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "arguments": sys.argv[1:],
        "python": platform.python_version(),
        "packages": {name: importlib.metadata.version(name)
                     for name in ("networkx", "requests", "matplotlib")},
        "offline": args.offline, "refresh": args.refresh,
        "network_requests": cache.network_requests, "cache_hits": cache.cache_hits,
        "source_count": len(cache.sources),
        "node_count": graph.number_of_nodes(), "edge_count": graph.number_of_edges(),
        "outputs": [str(args.output / "analysis.json"), str(args.output / "graph.png"), str(args.results)],
    }
    write_json(args.output / "execution.json", execution)
    mode_name = "offline" if args.offline else "live" if cache.network_requests else "cached"
    write_json(args.output / f"execution-{mode_name}.json", execution)
    print(json.dumps(execution, indent=2))


if __name__ == "__main__":
    main()
