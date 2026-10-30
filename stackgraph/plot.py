"""A static research figure. Layout and colors use C's topology only."""

import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import Patch


def draw_graph(graph, path):
    components = sorted(nx.weakly_connected_components(graph),
                        key=lambda c: (-len(c), sorted(c)))
    connected = [c for c in components if len(c) > 1]
    isolated = sorted(nx.isolates(graph))
    positions = {}
    for row, component in enumerate(connected):
        subgraph = graph.subgraph(component)
        if nx.is_directed_acyclic_graph(subgraph):
            layers = list(nx.topological_generations(subgraph))
            for col, layer in enumerate(layers):
                for offset, node in enumerate(sorted(layer)):
                    positions[node] = (col * 3.8, -row * 3.0 - offset * 1.6)
        else:
            layout = nx.circular_layout(subgraph)
            positions.update({node: (float(x) * 3, float(y) - row * 3)
                              for node, (x, y) in layout.items()})
    for index, node in enumerate(isolated):
        positions[node] = (index * 5.7, -max(1, len(connected)) * 3.0)
    height = max(7, 3.0 * (len(connected) + bool(isolated)))
    fig, ax = plt.subplots(figsize=(19, height))
    colors = ["#9ecae1" if graph.degree(n) else "#dddddd" for n in graph]
    nx.draw_networkx_nodes(graph, positions, node_size=2200, node_color=colors,
                           edgecolors="#334155", ax=ax)
    nx.draw_networkx_edges(graph, positions, arrowstyle="-|>", arrowsize=24,
                           node_size=2200, width=2, edge_color="#334155", ax=ax)
    labels = {n: f"#{data['number']}"
              for n, data in graph.nodes(data=True)}
    nx.draw_networkx_labels(graph, positions, labels=labels, font_size=11, ax=ax)
    edge_labels = {(u, v): "base = head\n" + "\n".join(textwrap.wrap(
        d["branch"].split(":", 1)[1], width=24, break_on_hyphens=True))
        for u, v, d in graph.edges(data=True)}
    nx.draw_networkx_edge_labels(graph, positions, edge_labels=edge_labels,
                                font_size=8, rotate=False, label_pos=0.5, ax=ax)
    # Branch details make the three isolated controls interpretable in the image.
    for node, (x, y) in positions.items():
        d = graph.nodes[node]
        date = (d["created_at"] or "unknown time").replace("T", " ").replace("Z", " UTC")
        title = "\n".join(textwrap.wrap(d["title"], width=34))
        base_note = f"\nbase: {d['base_ref'] or '?'}" if graph.in_degree(node) == 0 else ""
        ax.text(x, y - 0.55, f"@{d['author'] or '?'} | {date}\n{title}{base_note}",
                ha="center", va="top", fontsize=8, color="#334155")
    repos = ", ".join(sorted({d["repository"] for _, d in graph.nodes(data=True)}))
    ax.set_title(f"StackGraph — {repos}\nC: branch-derived dependency graph; prerequisite → dependent",
                 fontsize=16, pad=24)
    ax.legend(handles=[Patch(facecolor="#9ecae1", edgecolor="#334155", label="Branch-connected PR"),
                       Patch(facecolor="#dddddd", edgecolor="#334155", label="Isolated within this sample")],
              loc="upper right", frameon=False)
    ax.margins(x=0.14, y=0.35)
    ax.axis("off")
    fig.text(0.5, 0.025, "Edges require equal repository-qualified branch refs. Timing and official stack membership do not create edges.\n"
             "Isolation is sample-relative; workflow structure does not establish AI authorship or code quality.",
             ha="center", fontsize=10)
    fig.savefig(path, dpi=160, bbox_inches="tight", metadata={"Software": "StackGraph"})
    plt.close(fig)
