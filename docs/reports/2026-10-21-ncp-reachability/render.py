"""Render the reachability diagram and one-page evidence PDF."""

from pathlib import Path
import subprocess

from reportlab import rl_config
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg


ROOT = Path(__file__).resolve().parent
rl_config.invariant = 1
renderPDF.drawToFile(svg2rlg(str(ROOT / "diagram.svg")), str(ROOT / "diagram.pdf"))
subprocess.run(["tectonic", "report.tex", "--outdir", "."], cwd=ROOT, check=True)
