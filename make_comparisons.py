"""Build side-by-side comparison images: original paper figures vs reproductions.

A curated set of representative figures is used (not all 14): four strong
successes spanning different analyses, plus the one known divergence. The full
set of reproductions lives in figures/ and is summarized in README.md.

Steps:
  1. Render the needed PDF pages to PNGs.
  2. Crop each selected figure (coordinates hand-tuned against the 200-DPI render).
  3. Compose each original crop next to its reproduction from figures/.

Requires: pymupdf (fitz), pillow, matplotlib.
Run:  python make_comparisons.py
Outputs: figures/original_pages/, figures/original_crops/, figures/comparisons/
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image

HERE = os.path.dirname(__file__)
PDF = os.path.join(HERE, "docs",
                   "Affordable-rapid-bootstrapping-of-space-industry-and-solar-system-civilization.pdf")
PAGES_DIR = os.path.join(HERE, "figures", "original_pages")
CROPS_DIR = os.path.join(HERE, "figures", "original_crops")
COMP_DIR = os.path.join(HERE, "figures", "comparisons")
DPI = 200

# Curated set. key -> (page number (1-based), x0, y0, x1, y1) at 200 DPI
# (pages are 1700x2200). Crops verified to include legends and axes, no caption.
CROPS = {
    "fig02": (12, 350, 505, 1290, 895),
    "fig03": (12, 340, 1175, 1300, 1560),
    "fig04": (13, 340, 355, 1240, 745),
    "fig08": (15, 400, 1128, 1230, 1560),
    "fig11": (16, 350, 1495, 1250, 1800),
    "fig12": (17, 380, 1298, 1200, 1665),
}

# key -> (reproduction filename, comparison title)
REPRO = {
    "fig02": ("fig02_growth.png", "Fig. 2 - Growth of lunar industry"),
    "fig03": ("fig03_production.png", "Fig. 3 - Production of materials & parts"),
    "fig04": ("fig04_launch_mass.png", "Fig. 4 - Mass launched to Moon"),
    "fig08": ("fig08_printers.png", "Fig. 8 - Printers/set vs reproduction time"),
    "fig11": ("fig11_mass_vs_robonauts.png", "Fig. 11 - Gen-6 mass vs robonauts (known divergence)"),
    "fig12": ("fig12_rwpa_robonauts.png", "Fig. 12 - Robonauts by robonaut productivity"),
}


def render_pages():
    import fitz
    os.makedirs(PAGES_DIR, exist_ok=True)
    doc = fitz.open(PDF)
    for pno in sorted({c[0] for c in CROPS.values()}):
        doc[pno - 1].get_pixmap(dpi=DPI).save(os.path.join(PAGES_DIR, f"page{pno:02d}.png"))
    print(f"rendered pages -> {PAGES_DIR}")


def crop_originals():
    os.makedirs(CROPS_DIR, exist_ok=True)
    cache = {}
    for key, (pno, x0, y0, x1, y1) in CROPS.items():
        cache.setdefault(pno, Image.open(os.path.join(PAGES_DIR, f"page{pno:02d}.png")))
        cache[pno].crop((x0, y0, x1, y1)).save(os.path.join(CROPS_DIR, f"{key}.png"))
    print(f"cropped {len(CROPS)} figures -> {CROPS_DIR}")


def compose():
    os.makedirs(COMP_DIR, exist_ok=True)
    for key, (repro, title) in REPRO.items():
        orig = mpimg.imread(os.path.join(CROPS_DIR, f"{key}.png"))
        rep = mpimg.imread(os.path.join(HERE, "figures", repro))
        fig, (a, b) = plt.subplots(1, 2, figsize=(12, 4.0))
        a.imshow(orig); a.axis("off"); a.set_title("Original (paper)", fontsize=11, weight="bold")
        b.imshow(rep); b.axis("off"); b.set_title("Reproduction", fontsize=11, weight="bold")
        fig.suptitle(title, fontsize=13, weight="bold", y=1.02)
        fig.tight_layout()
        fig.savefig(os.path.join(COMP_DIR, f"compare_{key}.png"), dpi=110, bbox_inches="tight")
        plt.close(fig)
    print(f"composed {len(REPRO)} comparisons -> {COMP_DIR}")


if __name__ == "__main__":
    render_pages()
    crop_originals()
    compose()
