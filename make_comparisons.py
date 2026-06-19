"""Build side-by-side comparison images: original paper figures vs reproductions.

Steps:
  1. Render the figure-bearing PDF pages (12-18) to PNGs.
  2. Crop each of the 13 figures from those pages (coordinates below, hand-tuned
     against the 200-DPI render).
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

# figure key -> (page file, x0, y0, x1, y1) crop box at 200 DPI (1700x2200 pages)
CROPS = {
    "fig02": ("page12", 350, 505, 1290, 895),
    "fig03": ("page12", 340, 1175, 1300, 1560),
    "fig04": ("page13", 340, 355, 1240, 745),
    "fig05": ("page14", 360, 135, 1190, 420),
    "fig06": ("page14", 360, 670, 1190, 970),
    "fig07": ("page14", 360, 1240, 1190, 1565),
    "fig08": ("page15", 400, 1185, 1200, 1630),
    "fig09": ("page16", 350, 445, 1250, 805),
    "fig10": ("page16", 350, 880, 1250, 1235),
    "fig11": ("page16", 350, 1495, 1250, 1800),
    "fig12": ("page17", 380, 1260, 1200, 1665),
    "fig13": ("page18", 330, 150, 1110, 435),
    "fig14": ("page18", 330, 735, 1110, 1035),
}

# figure key -> (reproduction filename, comparison title)
REPRO = {
    "fig02": ("fig02_growth.png", "Fig. 2 - Growth of lunar industry"),
    "fig03": ("fig03_production.png", "Fig. 3 - Production of materials & parts"),
    "fig04": ("fig04_launch_mass.png", "Fig. 4 - Mass launched to Moon"),
    "fig05": ("fig05_power.png", "Fig. 5 - Power available vs needed"),
    "fig06": ("fig06_duty_mass.png", "Fig. 6 - Asset mass by duty cycle"),
    "fig07": ("fig07_duty_robonauts.png", "Fig. 7 - Robonauts by duty cycle"),
    "fig08": ("fig08_printers.png", "Fig. 8 - Printers/set vs reproduction time"),
    "fig09": ("fig09_mass_by_year.png", "Fig. 9 - Asset mass by year"),
    "fig10": ("fig10_robonauts_by_year.png", "Fig. 10 - Robonauts by year"),
    "fig11": ("fig11_mass_vs_robonauts.png", "Fig. 11 - Gen-6 mass vs robonauts"),
    "fig12": ("fig12_rwpa_robonauts.png", "Fig. 12 - Robonauts by RWPA"),
    "fig13": ("fig13_rwpa_mass.png", "Fig. 13 - Asset mass by RWPA"),
    "fig14": ("fig14_rwpa_launch.png", "Fig. 14 - Launch mass by RWPA"),
}

# 1-based PDF pages that carry figures
PAGE_NUMBERS = [12, 13, 14, 15, 16, 17, 18]


def render_pages():
    import fitz
    os.makedirs(PAGES_DIR, exist_ok=True)
    doc = fitz.open(PDF)
    for pno in PAGE_NUMBERS:
        pix = doc[pno - 1].get_pixmap(dpi=DPI)
        pix.save(os.path.join(PAGES_DIR, f"page{pno:02d}.png"))
    print(f"rendered {len(PAGE_NUMBERS)} pages -> {PAGES_DIR}")


def crop_originals():
    os.makedirs(CROPS_DIR, exist_ok=True)
    cache = {}
    for key, (pg, x0, y0, x1, y1) in CROPS.items():
        cache.setdefault(pg, Image.open(os.path.join(PAGES_DIR, f"{pg}.png")))
        cache[pg].crop((x0, y0, x1, y1)).save(os.path.join(CROPS_DIR, f"{key}.png"))
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
