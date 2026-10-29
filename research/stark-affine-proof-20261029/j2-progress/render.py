from pathlib import Path
import typst
p=Path(__file__).resolve().parent
typst.compile(str(p/"report.typ"), output=str(p/"report.pdf"))
