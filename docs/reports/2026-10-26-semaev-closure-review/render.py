"""Render an additive scope-corrected view of the frozen 80-draw SVG.

Only explanatory text changes. All rectangles, positions, category colors,
draw labels, and values remain byte-identical to the archived chart.
"""

from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET


SOURCE = "docs/reports/2026-10-22-semaev-first-fall-replay/draws.svg"
OUTPUT = Path(__file__).with_name("direct-row-grades.svg")


def replace_once(svg, before, after):
    if svg.count(before) != 1:
        raise RuntimeError("source chart label changed: " + before)
    return svg.replace(before, after)


def main():
    source_svg = subprocess.check_output(["git", "show", "HEAD:" + SOURCE]).decode()
    svg = source_svg
    if svg.count("<g><title>n=") != 80:
        raise RuntimeError("source chart no longer has 80 draw tiles")
    labels = (
        ("Archived and Boolean-parity first-fall grades by draw",
         "Archived and parity-corrected direct-row grades by draw"),
        ("Eight cells of ten deterministic toy draws. Two archived degree-two grades become degree three when duplicate monomials cancel over F2.",
         "Eight cells of ten fixed toy draws. Corrected direct-row grades use F2 parity. Closed-filtration first-fall grades are not established."),
        ("Toy Semaev first fall: archive → Boolean parity",
         "Toy Semaev direct-row grades: archive → parity"),
        ("Each tile is one seed; grades show archived set union → corrected F₂ multiplication.",
         "Each tile is one seed; grades use selected row spans, not a proved closed filtration."),
        ("Verified transitions", "Verified row transitions"),
        ("Corrected first fall: 68 at degree two, 12 at degree three; seven degree-three targets are nonzero.",
         "Direct-row grades: 68 at degree two, 12 at degree three; closed-filtration grades unverified."),
        ("Source: evidence/draws.json; n=4..7, n′=3,4, ten seeds per cell. Validation data, not a timing or attack-cost plot.",
         "Source: frozen draws.json; n=4..7, n′=3,4, ten seeds per cell. No cost inference."),
    )
    for before, after in labels:
        svg = replace_once(svg, before, after)
    svg = svg.replace('font-size="12" fill="#193444">Direct-row grades:',
                      'font-size="11" fill="#193444">Direct-row grades:')
    if svg.count("<g><title>n=") != 80:
        raise RuntimeError("draw tiles changed during relabeling")
    svg_ns = "{http://www.w3.org/2000/svg}"
    old_tiles = [ET.tostring(group) for group in
                 ET.fromstring(source_svg).findall(".//" + svg_ns + "g")]
    new_tiles = [ET.tostring(group) for group in
                 ET.fromstring(svg).findall(".//" + svg_ns + "g")]
    if len(old_tiles) != 80 or old_tiles != new_tiles:
        raise RuntimeError("draw geometry, labels, or values changed")
    OUTPUT.write_text(svg)


if __name__ == "__main__":
    main()
