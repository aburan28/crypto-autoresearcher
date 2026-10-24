#!/usr/bin/env python3
"""README.md -> report.typ -> report.pdf (Typst). Run from this directory."""
import re
import sys

BOLD = "\x00B\x00"
ITAL = "\x00I\x00"


def esc(seg: str) -> str:
    seg = re.sub(r"\*\*(.+?)\*\*", lambda m: BOLD + m.group(1) + BOLD, seg)
    seg = re.sub(r"(?<![*\w])\*([^*\s][^*]*?)\*(?![*\w])",
                 lambda m: ITAL + m.group(1) + ITAL, seg)
    for ch in "\\#$@<>_*~[]=":
        seg = seg.replace(ch, "\\" + ch)
    return seg.replace(BOLD, "*").replace(ITAL, "_")


def inline(text: str) -> str:
    parts = re.split(r"(`[^`]*`)", text)
    return "".join(p if p.startswith("`") else esc(p) for p in parts)


def convert(md: str) -> str:
    out = ['#set page(paper: "a4", margin: 2cm)',
           '#set text(size: 9.5pt)',
           '#set par(justify: false)',
           '#show raw: set text(size: 8.5pt)', '']
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        ln = lines[i]
        m = re.match(r"^(#+) (.*)$", ln)
        img = re.match(r"^!\[(.*)\]\((.*)\)$", ln)
        if m:
            out.append("=" * len(m.group(1)) + " " + inline(m.group(2)))
        elif img:
            out.append(f'#figure(image("{img.group(2)}", width: 92%), '
                       f'caption: [{inline(img.group(1))}])')
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            n = len(rows[0])
            body = ", ".join(f"[{inline(c)}]" for r in rows for c in r)
            out.append(f"#table(columns: {n}, inset: 4pt, "
                       f"stroke: 0.4pt + luma(180), {body})")
            continue
        elif re.match(r"^\s*- ", ln):
            depth = (len(ln) - len(ln.lstrip())) // 2
            item = [ln.strip()[2:]]
            while i + 1 < len(lines) and lines[i + 1].startswith("  " * (depth + 1)) \
                    and not re.match(r"^\s*(- |\d+\. )", lines[i + 1]):
                i += 1
                item.append(lines[i].strip())
            out.append("  " * depth + "- " + inline(" ".join(item)))
        elif re.match(r"^\d+\. ", ln):
            item = [re.sub(r"^\d+\. ", "", ln)]
            while i + 1 < len(lines) and lines[i + 1].startswith("   ") \
                    and not re.match(r"^\s*- ", lines[i + 1]):
                i += 1
                item.append(lines[i].strip())
            out.append("+ " + inline(" ".join(item)))
        elif ln.strip():
            para = [ln]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(
                    r"^(#|!\[|\||\s*- |\d+\. )", lines[i + 1]):
                i += 1
                para.append(lines[i])
            out.append(inline(" ".join(para)))
        else:
            out.append("")
        i += 1
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import typst
    open("report.typ", "w").write(convert(open("README.md").read()))
    typst.compile("report.typ", output="report.pdf")
    print("report.pdf written")
