import textwrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages
txt = open("report.md").read()
with PdfPages("report.pdf") as pdf:
    fig = plt.figure(figsize=(8.5, 11)); fig.text(0.06, 0.96, "", fontsize=8)
    y = 0.96
    for line in txt.splitlines():
        for w in (textwrap.wrap(line, 105) or [""]):
            fig.text(0.06, y, w, fontsize=7.5, family="monospace", va="top"); y -= 0.0165
    pdf.savefig(fig); plt.close(fig)
    fig = plt.figure(figsize=(8.5, 5)); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.imshow(mpimg.imread("calibration.png"))
    pdf.savefig(fig); plt.close(fig)
