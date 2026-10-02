"""eswa_patch.py -- import before running a figure script to produce submission-ready figures:
no figure-level titles (ESWA: the title belongs in the caption), single-axes figures lose their axes title, and every savefig also writes
a vector PDF and a 300-dpi PNG to figures_eswa/. Panel titles of multi-panel figures are kept (they are panel labels)."""
import os
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "figures_eswa")
os.makedirs(OUT, exist_ok=True)
Figure.suptitle = lambda self, *a, **k: None
_orig = Figure.savefig
def savefig(self, fname, *a, **k):
    axes = [ax for ax in self.axes if ax.get_visible() and ax.bbox.width > 50]
    if len(axes) == 1: axes[0].set_title("")
    base = os.path.splitext(os.path.basename(str(fname)))[0]
    k2 = {kk: v for kk, v in k.items() if kk != "dpi"}
    _orig(self, os.path.join(OUT, base + ".pdf"), **k2)
    _orig(self, os.path.join(OUT, base + ".png"), dpi=300, **k2)
Figure.savefig = savefig
