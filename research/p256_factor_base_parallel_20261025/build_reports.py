"""Render the new study reports with Typst; never replace an earlier report.

Requires the typst Python wheel. Raw scientific outputs are not changed.
Markdown is rendered as literal text blocks, headings, lists and tables; the
original Markdown remains the authoritative prose source.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent


def quote(text):
    return json.dumps(text, ensure_ascii=False)


def plain(text):
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    return text.replace("**", "").replace("`", "")


def render_markdown(source):
    lines = source.splitlines()
    output = []
    paragraph = []

    def flush():
        if paragraph:
            output.append("#text(" + quote(plain(" ".join(paragraph))) + ")\n#parbreak()")
            paragraph.clear()

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            flush()
        elif line.startswith("```"):
            flush()
            code = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.extend(textwrap.wrap(lines[i], 104, replace_whitespace=False,
                                           drop_whitespace=False) or [""])
                i += 1
            output.append("#text(size: 7.2pt)[#raw(" + quote("\n".join(code)) + ", block: true)]")
        elif re.match(r"^#{1,6} ", line):
            flush()
            level = len(line)-len(line.lstrip("#"))
            output.append(f"#heading(level: {min(level,3)})[#text({quote(plain(line[level+1:]))})]")
        elif re.match(r"^!\[([^]]*)\]\(([^)]+)\)$", line.strip()):
            flush()
            match = re.match(r"^!\[([^]]*)\]\(([^)]+)\)$", line.strip())
            output.append("#figure(image("+quote(match[2])+", width: 100%, height: 6.4cm, fit: \"contain\"), caption: [#text("+quote(match[1])+")])")
        elif line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [plain(x.strip()) for x in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c.replace(" ", "")) for c in cells):
                    rows.append(cells)
                i += 1
            i -= 1
            width = max(map(len, rows))
            cells = [f"[#text(size: 8pt, {quote(c)})]" for row in rows for c in row+[""]*(width-len(row))]
            output.append(f"#table(columns: {width}, inset: 4pt, stroke: 0.3pt + rgb(\"#b0bdc9\"), " + ",\n".join(cells)+")")
        elif re.match(r"^\s*[-*] ", line):
            flush()
            bullet = re.sub(r"^\s*[-*] ", "", line)
            output.append("#block(inset: (left: 8pt))[#text(" + quote("• "+plain(bullet)) + ")]")
        else:
            paragraph.append(line.strip())
        i += 1
    flush()
    return "\n\n".join(output)


def document(markdown, diagram):
    body = render_markdown(markdown)
    visual = ("\n#figure(image("+quote(diagram)+", width: 100%, height: 5.4cm, fit: \"contain\"), "
              "caption: [Editable study diagram; exact scope and evidence paths appear in the report.])\n") if diagram else ""
    first, separator, rest = body.partition("\n\n")
    return ("#set page(paper: \"a4\", margin: (x: 1.6cm, y: 1.5cm), "
            "footer: context align(right, text(size: 8pt, counter(page).display(\"1\"))))\n"
            "#set text(font: \"Liberation Sans\", size: 9pt, lang: \"en\", ligatures: false)\n"
            "#show raw: set text(font: \"Liberation Mono\")\n"
            "#set par(justify: false, leading: 0.55em)\n"
            "#set heading(numbering: none)\n"
            "#show heading: set block(above: 0.8em, below: 0.4em)\n"
            + first + visual + separator + rest + "\n")


def build(directory, stem, source_name):
    import typst
    if source_name == "report.md" and (directory/"report-with-clarification.md").exists():
        source_name = "report-with-clarification.md"
    source = directory / source_name
    target = directory / (stem+".typ")
    pdf = directory / (stem+".pdf")
    if target.exists() or pdf.exists():
        raise RuntimeError(f"Refusing to overwrite {directory}'s report; use a new report directory")
    diagram = ("publication-diagram.svg" if (directory/"publication-diagram.svg").exists()
               else "diagram.svg" if (directory/"diagram.svg").exists() else None)
    if diagram:
        original = (directory/diagram).read_text()
        corrected = original.replace(".arrow{", ".arrow{fill:none;")
        if corrected != original:
            diagram = "diagram-render.svg"
            (directory/diagram).write_text(corrected)
    target.write_text(document(source.read_text(), diagram))
    with tempfile.TemporaryDirectory(prefix="p256-pdf-render-") as staging:
        raw = Path(staging)/"typst.pdf"
        typst.compile(str(target), output=str(raw), root=str(ROOT))
        subprocess.run([
            "gs", "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.7", "-dPDFSETTINGS=/prepress",
            "-dCompressFonts=true", "-dSubsetFonts=true", "-dPreserveMarkedContent=true",
            "-dQUIET", "-dNOPAUSE", "-dBATCH", "-sOutputFile="+str(pdf), str(raw)], check=True)
        text = ["".join(subprocess.check_output(
            ["pdftotext", "-layout", str(p), "-"], text=True).split()) for p in [raw, pdf]]
        if text[0] != text[1]:
            raise RuntimeError("Compaction changed extracted text; output requires correction")
        if pdf.stat().st_size > 65536:
            raise RuntimeError("PDF exceeds the repository's in-Git data limit")
    print(json.dumps({"source": str(source.relative_to(ROOT)),
                      "pdf": str(pdf.relative_to(ROOT)), "bytes": pdf.stat().st_size}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directories", nargs="+", help="Report directories relative to study root")
    parser.add_argument("--stem", default="report-publication", help="Fresh output stem")
    parser.add_argument("--source", default="report.md", help="Markdown source filename")
    args = parser.parse_args()
    for name in args.directories:
        build(ROOT/name, args.stem, args.source)
