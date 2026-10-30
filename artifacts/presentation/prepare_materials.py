"""Rebuild presentation evidence and static figures offline; no new research method.

Run from the project root: .venv/Scripts/python.exe artifacts/presentation/prepare_materials.py
"""

import csv
import hashlib
import json
import sys
import textwrap
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from stackgraph.__main__ import analyze
from stackgraph.source import GitHubCache, digest

OUT = Path(__file__).resolve().parent


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def evidence():
    inventory, snapshots = [], {}
    for path in sorted((ROOT / "data/cache").glob("*.json")):
        raw = path.read_bytes()
        record = json.loads(raw)
        assert record["data_sha256"] == digest(record["data"]), path
        assert record["http_status"] == 200, path
        snapshots[record["source_url"]] = (path, record)
        server = datetime.strptime(record["response_date"], "%a, %d %b %Y %H:%M:%S %Z")
        client = datetime.fromisoformat(record["retrieved_at"]).replace(tzinfo=None)
        inventory.append({"cache_file": path.relative_to(ROOT).as_posix(),
                          "source_url": record["source_url"],
                          "retrieved_at": record["retrieved_at"],
                          "response_date": record["response_date"],
                          "server_date_minus_client_seconds": (server - client).total_seconds(),
                          "http_status": record["http_status"],
                          "payload_checksum_valid": True,
                          "data_sha256": record["data_sha256"],
                          "file_sha256": hashlib.sha256(raw).hexdigest()})
    manifest = json.loads((ROOT / "data/sample.json").read_text(encoding="utf-8"))
    result, graph = analyze(manifest, GitHubCache(ROOT / "data/cache", offline=True))
    rows, prs = [], {}
    for number in manifest["pull_requests"]:
        url = f"https://api.github.com/repos/cli/cli/pulls/{number}"
        path, snapshot = snapshots[url]
        pr = snapshot["data"]
        prs[number] = pr
        lookup_url = f"https://api.github.com/repos/cli/cli/stacks?pull_request={number}&per_page=100"
        lookup_path, lookup = snapshots[lookup_url]
        native = pr.get("stack") or {}
        native_groups = [s["number"] for s in lookup["data"]
                         if number in [p["number"] for p in s["pull_requests"]]]
        if native:
            assert native_groups == [native["number"]]
            for stack in lookup["data"]:
                for entry in stack["pull_requests"]:
                    if entry["number"] == number:
                        assert entry["head"]["ref"] == pr["head"]["ref"]
                        assert entry["head"]["sha"] == pr["head"]["sha"]
        else:
            assert lookup["data"] == [] and lookup["next_page"] is None
        row = {"number": number, "pr_url": pr["html_url"], "api_url": url,
               "created_at_utc": pr["created_at"], "author": pr["user"]["login"],
               "base_repository": pr["base"]["repo"]["full_name"],
               "base_ref": pr["base"]["ref"], "base_sha": pr["base"]["sha"],
               "head_repository": pr["head"]["repo"]["full_name"],
               "head_ref": pr["head"]["ref"], "head_sha": pr["head"]["sha"],
               "native_stack_field": "documented" if native else "absent",
               "stack_number": native.get("number"), "stack_position": native.get("position"),
               "stack_size": native.get("size"), "filtered_stack_numbers": native_groups,
               "official_status": result["B_official"]["statuses"][f"cli/cli#{number}"],
               "pr_retrieved_at": snapshot["retrieved_at"],
               "lookup_retrieved_at": lookup["retrieved_at"], "lookup_url": lookup_url,
               "pr_cache_file": path.relative_to(ROOT).as_posix(),
               "lookup_cache_file": lookup_path.relative_to(ROOT).as_posix()}
        rows.append(row)
    verified = []
    # Explicit case edges were checked in the raw records, not obtained from B.
    expected = [(14348, 14349), (14349, 14350), (14350, 14351), (14351, 14355)]
    assert set(graph.edges) == {(f"cli/cli#{p}", f"cli/cli#{q}") for p, q in expected}
    for index, (p, q) in enumerate(expected, 1):
        parent, child = prs[p], prs[q]
        assert parent["head"]["repo"]["full_name"] == child["base"]["repo"]["full_name"]
        assert parent["head"]["ref"] == child["base"]["ref"]
        assert parent["head"]["sha"] == child["base"]["sha"]
        candidates = [n for n, raw in prs.items()
                      if (raw["head"]["repo"]["full_name"], raw["head"]["ref"])
                      == (child["base"]["repo"]["full_name"], child["base"]["ref"])]
        assert candidates == [p]
        verified.append({"edge_id": f"E{index}", "prerequisite": p, "dependent": q,
                         "parent_url": parent["html_url"], "child_url": child["html_url"],
                         "parent_head_repository": parent["head"]["repo"]["full_name"],
                         "child_base_repository": child["base"]["repo"]["full_name"],
                         "parent_head_ref": parent["head"]["ref"],
                         "child_base_ref": child["base"]["ref"],
                         "parent_head_sha": parent["head"]["sha"],
                         "child_base_sha": child["base"]["sha"],
                         "unique_matching_parent": True, "sha_equality_corroboration": True})
    live = json.loads((OUT / "live_metadata_check.json").read_text(encoding="utf-8"))
    live_checks = []
    for record in live:
        if record.get("http_status") != 200:
            live_checks.append({"source_url": record["source_url"], "verified": False,
                                "reason": record.get("error", "Non-200 response")})
            continue
        fresh = record["data"]
        saved = prs[fresh["number"]]
        fields = {"created_at": fresh["created_at"] == saved["created_at"],
                  "author": fresh["user"]["login"] == saved["user"]["login"],
                  "stack": fresh.get("stack") == saved.get("stack")}
        for side in ("base", "head"):
            for key in ("ref", "sha"):
                fields[f"{side}.{key}"] = fresh[side][key] == saved[side][key]
            fields[f"{side}.repo.full_name"] = fresh[side]["repo"]["full_name"] == saved[side]["repo"]["full_name"]
        live_checks.append({"number": fresh["number"], "source_url": record["source_url"],
                            "retrieved_at": record["retrieved_at"], "verified": all(fields.values()),
                            "fields_unchanged": fields})
    write_json("audit_evidence.json", {"cache_inventory": inventory, "pull_requests": rows,
                                     "verified_edges": verified, "separate_live_cross_check": live_checks,
                                     "graph_diagnostics": result["C_branch_graph"],
                                     "evaluation": result["evaluation"]})
    with (OUT / "evidence_table.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Exact PR and edge evidence", "",
             "All eight PRs are from `cli/cli`, authored by `williammartin`, and created on 2026-09-04. "
             "Times below are exact UTC creation times. Branch refs are case-sensitive; all base and head repositories are `cli/cli`. "
             "Membership and branch observations come from the saved 2026-10-28 snapshot, not creation-time reconstruction.", "",
             "| Exact PR URL | Creation time (UTC) | Base ref | Head ref | Official membership |",
             "| --- | --- | --- | --- | --- |"]
    for r in rows:
        membership = (f"Stack #{r['stack_number']}, position {r['stack_position']}/{r['stack_size']}"
                      if r["stack_number"] else "PR stack field absent; filtered lookup returned []")
        lines.append(f"| [{r['pr_url']}]({r['pr_url']}) | {r['created_at_utc']} | `{r['base_ref']}` | `{r['head_ref']}` | {membership} |")
    lines += ["", "## Verified arrows: prerequisite → dependent", "",
              "For every arrow, the child's base ref and repository equal the parent's head ref and repository. "
              "Only one sampled PR has that qualified head. Each pair also has equal SHAs, as recorded below. "
              "The program uses repository/ref equality; SHA equality is additional snapshot corroboration, not an input to the graph rule. "
              "These observations verify branch targeting, not code-level necessity or authorship.", ""]
    for edge in verified:
        lines += [f"### {edge['edge_id']}: #{edge['prerequisite']} → #{edge['dependent']}", "",
                  f"- Parent: {edge['parent_url']}; child: {edge['child_url']}.",
                  f"- Parent `head.repo.full_name` = child `base.repo.full_name` = `{edge['parent_head_repository']}`.",
                  f"- Parent `head.ref` = child `base.ref` = `{edge['parent_head_ref']}`.",
                  f"- Parent `head.sha` = child `base.sha` = `{edge['parent_head_sha']}`.",
                  "- Direction: the child targets the parent's contributed branch; the arrow points from prerequisite to dependent.", ""]
    lines += ["## Source mapping and retrieval dates", "",
              "All 16 saved responses have HTTP 200 and valid payload checksums. "
              "The CSV and JSON include all exact SHAs and timestamps. Absence of observed membership does not prove a PR was never stacked.", "",
              "| PR | Saved PR JSON / UTC retrieval | Saved filtered lookup / UTC retrieval |", "| --- | --- | --- |"]
    for r in rows:
        lines.append(f"| #{r['number']} | [{Path(r['pr_cache_file']).name}](../../{r['pr_cache_file']})<br>{r['pr_retrieved_at']} | "
                     f"[{Path(r['lookup_cache_file']).name}](../../{r['lookup_cache_file']})<br>{r['lookup_retrieved_at']} |")
    verified_count = sum(v["verified"] for v in live_checks)
    lines += ["", f"A separate live GET cross-check agreed on all audited fields for {verified_count}/{len(live_checks)} PRs. "
              "The full fresh responses and their own retrieval dates are in `live_metadata_check.json`; the original cache was not refreshed or changed. "
              "This live agreement checks the observed API values, not independent research labels.", ""]
    (OUT / "evidence_table.md").write_text("\n".join(lines), encoding="utf-8")
    return result, graph, verified


def figure(graph, edges):
    plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42})
    fig = plt.figure(figsize=(12, 7.2), facecolor="white")
    ax = fig.add_axes([0.045, 0.25, 0.91, 0.56])
    ax.set_xlim(-0.3, 11.3)
    ax.set_ylim(0.1, 4.1)
    ax.axis("off")
    chain = [14348, 14349, 14350, 14351, 14355]
    positions = {number: (0.9 + i * 2.3, 3.0) for i, number in enumerate(chain)}
    positions.update({number: (2.05 + i * 3.45, 1.05) for i, number in enumerate([14345, 14346, 14347])})
    ax.text(-0.1, 3.95, "a  Branch-connected PRs", fontweight="bold", fontsize=11)
    ax.text(-0.1, 1.95, "b  Isolated controls within this sample", fontweight="bold", fontsize=11)
    for number, (x, y) in positions.items():
        node = graph.nodes[f"cli/cli#{number}"]
        color = "#e0edf5" if graph.degree(f"cli/cli#{number}") else "#f0f0f0"
        ax.add_patch(FancyBboxPatch((x - 0.86, y - 0.44), 1.72, 0.88,
                                   boxstyle="round,pad=0.025,rounding_size=0.06",
                                   facecolor=color, edgecolor="#34495e", linewidth=1.1))
        ax.text(x, y + 0.29, f"#{number}", ha="center", va="center", fontsize=11, fontweight="bold")
        ax.text(x, y + 0.10, "\n".join(textwrap.wrap(node["title"], width=24)),
                ha="center", va="top", fontsize=8.4, linespacing=1.2)
        time = node["created_at"][11:19]
        ax.text(x, y - 0.63, f"{time} UTC", ha="center", fontsize=9, color="#475569")
        if graph.in_degree(f"cli/cli#{number}") == 0:
            ax.text(x, y - 0.83, "base: trunk", ha="center", fontsize=8.5, color="#475569")
    for edge in edges:
        x, y = positions[edge["prerequisite"]]
        end_x, end_y = positions[edge["dependent"]]
        ax.add_patch(FancyArrowPatch((x + 0.91, y), (end_x - 0.91, end_y),
                                    arrowstyle="-|>", mutation_scale=15, linewidth=1.5,
                                    color="#163c58"))
        ax.text((x + end_x) / 2, y + 0.24, edge["edge_id"], ha="center", fontsize=9.5,
                fontweight="bold", color="#163c58")
    fig.text(0.055, 0.948, "StackGraph: verified branch-targeting relationships", fontsize=17, fontweight="bold")
    fig.text(0.055, 0.906, "cli/cli  •  eight PRs by @williammartin  •  creation date: 4 September 2026", fontsize=10.5, color="#475569")
    fig.text(0.055, 0.87, "Arrows: prerequisite → dependent. Edge labels map to exact branch evidence below.", fontsize=10.5)
    fig.text(0.055, 0.246, "Verified edges: parent head = child base (repository = cli/cli for every endpoint)", fontsize=10.5, fontweight="bold")
    for index, edge in enumerate(edges):
        fig.text(0.055, 0.213 - index * 0.027, f"{edge['edge_id']}   {edge['parent_head_ref']}", fontsize=9.3)
    fig.text(0.055, 0.058, "Snapshot: 28 October 2026. Node color follows branch connectivity; official stack fields and timing create no edges.", fontsize=9, color="#475569")
    fig.text(0.055, 0.031, "Isolation is sample-relative. Branch structure does not establish semantic dependency, workflow legitimacy, or human authorship.", fontsize=9, color="#475569")
    fig.savefig(OUT / "graph.png", dpi=300, metadata={"Software": "StackGraph presentation audit"})
    fig.savefig(OUT / "graph.pdf", metadata={"Title": "StackGraph verified branch-targeting graph", "CreationDate": None, "ModDate": None})
    plt.close(fig)


BRIEF_SECTIONS = [
    ("Research problem", "Closely spaced pull-request creation events can describe separate changes or a coordinated stack. An activity-only view lacks explicit dependency direction. This exploratory case examines what verified branch relationships add to that view."),
    ("Research question", "Within a selected public GitHub case, do repository-qualified branch relationships reveal an ordered PR workflow and distinguish nearby controls beyond chronological grouping? Workflow legitimacy and authorship are outside the measured target."),
    ("Graph formulation", "G = (V, E) is a directed, unweighted PR graph. For distinct P and Q, P → Q when P's head repository/ref uniquely matches Q's base repository/ref. The arrow means prerequisite → dependent in a branch-targeting sense. All PRs remain nodes. Timing, PR text, and official stack fields cannot create edges."),
    ("Three methods compared", "A: simplified time heuristic; group sampled PR creation events by successive gaps of at most 60 minutes within a repository. It is not AgentScan, which was not run. B: native GitHub stack membership, used descriptively. C: branch-derived directed graph; weak components support unordered membership comparisons."),
    ("Actual observed findings", "Eight PRs from cli/cli, one author, created 4 September 2026. A yields groups of sizes 2 and 6 (16 co-grouped pairs). B documents one five-PR stack (10 co-member pairs). C gives 8 nodes, 4 arrows, 4 weak components, 3 isolates, and no cycles: 14348 → 14349 → 14350 → 14351 → 14355. All four raw branch matches also have equal SHAs. Six A pairs cross C components: five pair control 14347 with stack members; one pairs controls 14345 and 14346. At 15/180 minutes, A gives 3/1 groups."),
    ("Research limitations", "One purposively selected stack; controls selected using branches and native membership; one repository/author; only sampled creation events. Branch and stack metadata are mutable retrieval-time observations. No direct stack-field leakage into C was found, but selection bias and conceptual overlap with GitHub's branch-chain definition remain. No independent labels: precision/recall are unset. General detection accuracy and legitimacy remain inconclusive; stacks do not establish human authorship."),
    ("Next proposed experiment", "Freeze the same rules and sample all PRs in predeclared repository/date windows. Obtain independently adjudicated intentional-stack membership from code/history review or maintainers, blind to method outputs and native stack labels. Keep uncertain cases unknown. Only then compare A/B/C and report precision/recall with the target and denominator stated."),
]


def brief():
    lines = ["# StackGraph", "", "Exploratory Network Science case study · audited snapshot: 28 October 2026", ""]
    for heading, paragraph in BRIEF_SECTIONS:
        lines += [f"## {heading}", "", paragraph, ""]
    lines += ["Evidence: evidence_table.md and audit_evidence.json. Figure: graph.pdf. Full caveats: audit_report.md.", ""]
    (OUT / "research_brief.md").write_text("\n".join(lines), encoding="utf-8")
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    fig.text(0.08, 0.945, "StackGraph", fontsize=20, fontweight="bold")
    fig.text(0.08, 0.914, "Exploratory Network Science case study", fontsize=11.4)
    fig.text(0.08, 0.89, "Audited public-data snapshot: 28 October 2026", fontsize=9, color="#475569")
    y = 0.851
    for heading, paragraph in BRIEF_SECTIONS:
        fig.text(0.08, y, heading, fontsize=10.7, fontweight="bold")
        y -= 0.023
        for line in textwrap.wrap(paragraph, width=99):
            fig.text(0.08, y, line, fontsize=9.7)
            y -= 0.016
        y -= 0.014
    assert y > 0.045, f"Brief exceeds one page: bottom={y}"
    fig.text(0.08, 0.03, "Evidence: evidence_table.md / audit_evidence.json   |   Figure: graph.pdf   |   Full audit: audit_report.md", fontsize=7.5, color="#475569")
    with PdfPages(OUT / "research_brief.pdf", metadata={"Title": "StackGraph one-page research brief", "CreationDate": None}) as pdf:
        pdf.savefig(fig)
        assert pdf.get_pagecount() == 1
    fig.savefig(OUT / "brief_preview.png", dpi=130)
    plt.close(fig)


if __name__ == "__main__":
    result, graph, verified = evidence()
    figure(graph, verified)
    brief()
    print("Audited 16 cached records; verified 4 directed edges; wrote evidence, graph PNG/PDF, and one-page brief.")
