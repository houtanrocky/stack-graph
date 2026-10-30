"""Render only the new first-meeting brief. Core and prior artifacts are untouched."""

from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

OUT = Path(__file__).resolve().parent


def main():
    content = (OUT / "research_brief.md").read_text(encoding="utf-8")
    lines = content.splitlines()
    sections = []
    for block in content.split("\n## ")[1:]:
        heading, body = block.split("\n\n", 1)
        body = body.split("\n\nSources:", 1)[0].strip()
        sections.append((heading, body))
    plt.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42})
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    text_items = []
    text_items.append(fig.text(0.075, 0.955, "StackGraph", fontsize=19, fontweight="bold"))
    text_items.append(fig.text(0.075, 0.927, lines[2], fontsize=9.5, color="#475569"))
    y = 0.891
    for heading, body in sections:
        text_items.append(fig.text(0.075, y, heading, fontsize=10.1, fontweight="bold"))
        y -= 0.020
        for line in textwrap.wrap(body, width=104):
            text_items.append(fig.text(0.075, y, line, fontsize=9.2))
            y -= 0.0148
        y -= 0.010
    assert y > 0.045, f"Brief overflow: final y={y:.3f}"
    footer = ("[1] GitHub REST events  [2] GitHub event types  [3] GitHub REST rate limits\n"
              "Exact links/evidence: claim_support.md. Metric definitions/proposal: evaluation_plan.md. Prior graph retained.")
    text_items.append(fig.text(0.075, 0.025, footer, fontsize=7.1, color="#475569", linespacing=1.5))
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    bounds = fig.bbox
    for item in text_items:
        box = item.get_window_extent(renderer)
        assert box.x0 >= 0 and box.x1 <= bounds.x1, f"Horizontal clipping: {item.get_text()}"
        assert box.y0 >= 0 and box.y1 <= bounds.y1, f"Vertical clipping: {item.get_text()}"
    with PdfPages(OUT / "research_brief.pdf", metadata={"Title": "StackGraph first-meeting research brief", "CreationDate": None}) as pdf:
        pdf.savefig(fig)
        assert pdf.get_pagecount() == 1
    fig.savefig(OUT / "brief_preview.png", dpi=150)
    plt.close(fig)
    print("Rendered one A4 page; all text bounds fit; existing artifacts untouched.")


if __name__ == "__main__":
    main()
