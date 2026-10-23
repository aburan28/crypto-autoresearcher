from pathlib import Path
import typst
p=Path(__file__).with_name("report.typ")
typst.compile(str(p),output=str(p.with_suffix(".pdf")))
