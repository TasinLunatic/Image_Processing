"""
Experiment 2: Image Enhancement
================================
Digital Image Processing lab (OpenCV + NumPy + Matplotlib).

Part 1 -- night.png (FirstI):
    1. R / G / B channel histograms and the luminance histogram
       (statistics printed + plotted)
    2. Linear (alpha/beta) and non-linear (gamma) brightness enhancement
    3. Histogram equalization on the Y channel of YCrCb (no color distortion)
       + CLAHE as an improved method

Part 2 -- peppers.jpg (SecI):
    1. Add Gaussian noise                      -> NoiseI
    2. Smoothing filters (mean / Gaussian / median) -> SmoothI
    3. Sharpening (Unsharp masking + Laplacian)

Every figure and every intermediate image is saved into ./results.
Run:  python experiment2.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")  # headless backend: figures go to disk, no GUI window
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

NIGHT_PATH = SCRIPT_DIR / "night.png"
PEPPERS_PATH = SCRIPT_DIR / "peppers.JPG"

BINS = 256  # number of histogram bins

STATS: list[str] = []  # collected statistics, written to stats_summary.txt


def note(line: str = "") -> None:
    """Record one statistics line and echo it to the console."""
    print(line)
    STATS.append(line)


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------
def load_bgr(path: Path, name: str) -> np.ndarray:
    """Load an image as BGR; exit with a clear message if the file is missing."""
    if not path.exists():
        sys.exit(f"[ERROR] Could not find {name} at {path}. "
                 f"Put the image next to the script and run again.")
    img = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if img is None:
        sys.exit(f"[ERROR] OpenCV could not decode {name} ({path}).")
    note(f"[OK] Loaded {name}: {img.shape[1]}x{img.shape[0]}, dtype={img.dtype}")
    return img


def save_image(img: np.ndarray, name: str) -> None:
    cv2.imwrite(str(RESULTS_DIR / name), img)


def save_figure(fig: plt.Figure, name: str) -> None:
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / name, dpi=150, bbox_inches="tight")
    plt.close(fig)
    note(f"[OK] Figure saved: results/{name}")


def channel_stats(bgr: np.ndarray, label: str) -> str:
    """Return a multi-line string with per-channel statistics."""
    b, g, r = cv2.split(bgr)
    lines = [f"--- {label} ({bgr.shape[1]}x{bgr.shape[0]}) ---"]
    for name, ch in (("B", b), ("G", g), ("R", r)):
        lines.append(f"  {name}: mean={ch.mean():7.2f}  std={ch.std():7.2f}  "
                     f"min={ch.min():3d}  max={ch.max():3d}  median={np.median(ch):7.1f}")
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    lines.append(f"  Luminance: mean={gray.mean():7.2f}  std={gray.std():7.2f}  "
                 f"min={gray.min():3d}  max={gray.max():3d}")
    return "\n".join(lines)


def luminance_hist(img: np.ndarray) -> np.ndarray:
    """256-bin histogram of the luminance (gray) image."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.calcHist([gray], [0], None, [BINS], [0, 256])


def psnr(ref: np.ndarray, img: np.ndarray) -> float:
    """Peak Signal-to-Noise Ratio in dB (ref = noise-free reference)."""
    mse = np.mean((ref.astype(np.float64) - img.astype(np.float64)) ** 2)
    if mse == 0.0:
        return float("inf")
    return 20.0 * np.log10(255.0 / np.sqrt(mse))


def sharpness_metric(img: np.ndarray) -> float:
    """Variance of the Laplacian: large = more edges / detail (or noise!)."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


# ---------------------------------------------------------------------------
# Enhancement operators
# ---------------------------------------------------------------------------
def linear_transform(img: np.ndarray, alpha: float, beta: float) -> np.ndarray:
    """Point operation:  out = alpha * in + beta  (alpha = gain/contrast,
    beta = brightness offset). Values are clipped to [0, 255]."""
    return np.clip(alpha * img.astype(np.float32) + beta, 0, 255).astype(np.uint8)


def gamma_correct(img: np.ndarray, gamma: float) -> np.ndarray:
    """Power-law (gamma) transform via LUT:  out = 255 * (in/255)^(1/gamma).
    gamma > 1 brightens the image, gamma < 1 darkens it."""
    table = (np.arange(BINS, dtype=np.float32) / 255.0) ** (1.0 / gamma) * 255.0
    table = np.clip(table, 0, 255).astype(np.uint8)
    return cv2.LUT(img, table)


def equalize_y(img: np.ndarray) -> np.ndarray:
    """Histogram equalization applied ONLY to the Y channel of YCrCb, then
    converted back to BGR. Equalizing color channels directly would shift
    the hue and produce unnatural colors."""
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y_eq = cv2.equalizeHist(y)
    return cv2.cvtColor(cv2.merge([y_eq, cr, cb]), cv2.COLOR_YCrCb2BGR)


def clahe_y(img: np.ndarray, clip_limit: float = 3.0, tile: tuple[int, int] = (8, 8)) -> np.ndarray:
    """CLAHE (Contrast Limited Adaptive Histogram Equalization) on the Y
    channel. clip_limit bounds the contrast amplification; the tile grid
    makes the equalization local (per tile) instead of global."""
    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile)
    y_cl = clahe.apply(y)
    return cv2.cvtColor(cv2.merge([y_cl, cr, cb]), cv2.COLOR_YCrCb2BGR)


def add_gaussian_noise(img: np.ndarray, sigma: float = 25.0, seed: int = 42) -> np.ndarray:
    """Add zero-mean Gaussian noise with standard deviation `sigma`."""
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, sigma, img.shape)
    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)


def unsharp_mask(img: np.ndarray, k: float = 1.5, kernel: tuple[int, int] = (5, 5),
                 sigma: float = 1.5) -> np.ndarray:
    """Unsharp masking:  sharp = img + k * (img - blur(img)).
    k is the amount of the high-frequency detail that is added back."""
    blur = cv2.GaussianBlur(img, kernel, sigma)
    return cv2.addWeighted(img, 1.0 + k, blur, -k, 0)


LAPLACIAN_KERNEL_4 = np.array([[0, -1, 0],
                               [-1, 5, -1],
                               [0, -1, 0]], dtype=np.float32)  # 4-neighbour composite


def laplacian_sharpen(img: np.ndarray, kernel: np.ndarray = LAPLACIAN_KERNEL_4) -> np.ndarray:
    """Sharpening with the composite Laplacian kernel (f + Laplacian(f)).
    The 8-neighbour alternative is [[-1,-1,-1],[-1,9,-1],[-1,-1,-1]]."""
    return cv2.filter2D(img, -1, kernel)


# ---------------------------------------------------------------------------
# ============================ PART 1: night.png ============================
# ---------------------------------------------------------------------------
def part1(first: np.ndarray) -> None:
    note("\n" + "=" * 60)
    note("PART 1 - night.png (FirstI): brightness enhancement")
    note("=" * 60)
    note(channel_stats(first, "FirstI (original)"))

    # --- 1.1 R, G, B and luminance histograms ------------------------------
    b, g, r = cv2.split(first)
    gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    hists = {"R": cv2.calcHist([r], [0], None, [BINS], [0, 256]),
             "G": cv2.calcHist([g], [0], None, [BINS], [0, 256]),
             "B": cv2.calcHist([b], [0], None, [BINS], [0, 256]),
             "Luminance": cv2.calcHist([gray], [0], None, [BINS], [0, 256])}

    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    colors = {"R": "tab:red", "G": "tab:green", "B": "tab:blue", "Luminance": "black"}
    for ax, (name, hist) in zip(axes.ravel(), hists.items()):
        ax.plot(hist.ravel(), color=colors[name], lw=1.2)
        ax.axvline(hist.argmax(), color="gray", ls=":", lw=1,
                   label=f"peak at {int(hist.argmax())}")
        ax.set_title(f"{name} channel histogram")
        ax.set_xlabel("Intensity (0-255)")
        ax.set_ylabel("Pixel count")
        ax.legend(fontsize=8)
        ax.set_xlim([0, 255])
    fig.suptitle("FirstI: R, G, B channel histograms and luminance histogram")
    save_figure(fig, "fig1_histograms.png")

    # --- 1.2 Linear and gamma transformations ------------------------------
    ALPHA, BETA = 2.2, 25      # linear: out = alpha*in + beta
    GAMMA = 2.2                # gamma > 1 -> brighten (image is very dark)

    lin = linear_transform(first, ALPHA, BETA)
    gam = gamma_correct(first, GAMMA)

    note(f"\nLinear transform  (alpha={ALPHA}, beta={BETA}): "
         f"mean {first.mean():.1f} -> {lin.mean():.1f}")
    note(f"Gamma transform   (gamma={GAMMA}):            "
         f"mean {first.mean():.1f} -> {gam.mean():.1f}")
    save_image(lin, "12_linear.png")
    save_image(gam, "13_gamma.png")

    titles = ["Original (dark)",
              f"Linear: $\\alpha$={ALPHA}, $\\beta$={BETA}",
              f"Gamma: $\\gamma$={GAMMA}"]
    imgs = [first, lin, gam]
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 7))
    for ax, im, t in zip(axes[0], imgs, titles):          # top row: images
        ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        ax.set_title(t, fontsize=9)
        ax.axis("off")
    for ax, im, t in zip(axes[1], imgs, titles):          # bottom row: histograms
        ax.plot(luminance_hist(im).ravel(), color="black", lw=1.2)
        ax.axvline(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).mean(),
                   color="tab:red", ls="--", lw=1.2, label="mean")
        ax.set_title(t, fontsize=9)
        ax.set_xlabel("Intensity")
        ax.set_ylabel("Count")
        ax.legend(fontsize=8)
        ax.set_xlim([0, 255])
    fig.suptitle("FirstI: linear vs. non-linear (gamma) brightness enhancement")
    save_figure(fig, "fig2_brightness.png")

    # --- 1.3 Histogram equalization on Y channel + CLAHE -------------------
    he = equalize_y(first)
    cl = clahe_y(first)
    note(f"\nHistogram equalization (Y channel): mean {first.mean():.1f} -> {he.mean():.1f}")
    note(f"CLAHE (clip=3.0, 8x8 tiles):        mean {first.mean():.1f} -> {cl.mean():.1f}")
    save_image(he, "14_equalized_y.png")
    save_image(cl, "15_clahe.png")

    titles = ["Original", "HE on Y channel (global)", "CLAHE on Y channel (local)"]
    imgs = [first, he, cl]
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 7))
    for ax, im, t in zip(axes[0], imgs, titles):
        ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        ax.set_title(t, fontsize=9)
        ax.axis("off")
    for ax, im, t in zip(axes[1], imgs, titles):
        ax.plot(luminance_hist(im).ravel(), color="black", lw=1.2)
        ax.axvline(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).mean(),
                   color="tab:red", ls="--", lw=1.2, label="mean")
        ax.set_title(t, fontsize=9)
        ax.set_xlabel("Intensity")
        ax.set_ylabel("Count")
        ax.legend(fontsize=8)
        ax.set_xlim([0, 255])
    fig.suptitle("FirstI: histogram equalization (Y channel) and CLAHE")
    save_figure(fig, "fig3_equalization.png")


# ---------------------------------------------------------------------------
# ============================ PART 2: peppers.jpg ==========================
# ---------------------------------------------------------------------------
def part2(sec: np.ndarray) -> None:
    note("\n" + "=" * 60)
    note("PART 2 - peppers.jpg (SecI): noise -> smoothing -> sharpening")
    note("=" * 60)
    note(channel_stats(sec, "SecI (original)"))

    # --- 2.1 Add Gaussian noise -> NoiseI ----------------------------------
    SIGMA = 25.0
    noise_i = add_gaussian_noise(sec, SIGMA)
    note(f"\nGaussian noise added (sigma={SIGMA:.0f}):  "
         f"PSNR(SecI, NoiseI) = {psnr(sec, noise_i):.2f} dB")
    save_image(noise_i, "21_noise.png")

    # --- 2.2 Smoothing filters -> SmoothI ----------------------------------
    mean5 = cv2.blur(noise_i, (5, 5))                          # arithmetic mean
    gauss5 = cv2.GaussianBlur(noise_i, (5, 5), sigmaX=1.2)     # Gaussian (SmoothI)
    median5 = cv2.medianBlur(noise_i, 5)                       # median
    smooth_i = gauss5
    save_image(mean5, "22_smooth_mean.png")
    save_image(smooth_i, "23_smooth_gaussian.png")
    save_image(median5, "24_smooth_median.png")

    psnrs = {"Noisy": psnr(sec, noise_i),
             "Mean 5x5": psnr(sec, mean5),
             "Gaussian 5x5": psnr(sec, smooth_i),
             "Median 5x5": psnr(sec, median5)}
    for k, v in psnrs.items():
        note(f"PSNR(SecI, {k:>11s}) = {v:6.2f} dB")

    fig, axes = plt.subplots(2, 3, figsize=(12.5, 7))
    panels = [(sec, "SecI (original)"),
              (noise_i, f"NoiseI (Gaussian, $\\sigma$={SIGMA:.0f})"),
              (mean5, "Mean filter 5x5"),
              (smooth_i, "SmoothI: Gaussian 5x5, $\\sigma$=1.2"),
              (median5, "Median filter 5x5")]
    for ax, (im, t) in zip(axes.ravel(), panels):
        ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        ax.set_title(t, fontsize=9)
        ax.axis("off")
    ax = axes[1, 2]                                            # last panel: PSNR bars
    bars = ax.bar(psnrs.keys(), psnrs.values(), color="tab:orange")
    ax.bar_label(bars, fmt="%.1f", fontsize=8)
    ax.set_title("PSNR vs. SecI (dB, higher = better)")
    ax.set_ylim([0, 45])
    ax.tick_params(axis="x", labelsize=8)
    fig.suptitle("SecI: Gaussian noise suppression with different smoothing filters")
    save_figure(fig, "fig4_smoothing.png")

    # --- 2.3 Sharpening of SmoothI ------------------------------------------
    K_USM = 1.5
    sharp_usm = unsharp_mask(smooth_i, k=K_USM)
    sharp_lap = laplacian_sharpen(smooth_i)
    save_image(sharp_usm, "25_unsharp.png")
    save_image(sharp_lap, "26_laplacian.png")

    note(f"\nSharpness metric (variance of Laplacian):")
    for name, im in (("SecI", sec), ("NoiseI", noise_i), ("SmoothI", smooth_i),
                     (f"Unsharp k={K_USM}", sharp_usm), ("Laplacian", sharp_lap)):
        note(f"  {name:>14s}: {sharpness_metric(im):9.1f}")

    # center crop so the sharpening effect is easy to see in the figure
    y0, x0 = 80, 80
    crop = lambda im: im[y0:y0 + 96, x0:x0 + 96]
    titles = [f"SmoothI (smoothed)", f"Unsharp masking (k={K_USM})", "Laplacian 4-neighbour"]
    imgs = [smooth_i, sharp_usm, sharp_lap]
    fig, axes = plt.subplots(2, 3, figsize=(12.5, 7))
    for ax, im, t in zip(axes[0], imgs, titles):              # top: full images
        ax.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
        ax.set_title(t, fontsize=9)
        ax.axis("off")
    for ax, im in zip(axes[1], imgs):                         # bottom: zoomed crops
        ax.imshow(cv2.cvtColor(crop(im), cv2.COLOR_BGR2RGB))
        ax.set_title("Zoom (center 96x96)", fontsize=9)
        ax.axis("off")
    fig.suptitle("SmoothI: sharpening with Unsharp masking and Laplacian")
    save_figure(fig, "fig5_sharpening.png")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    note("Experiment 2: Image Enhancement")
    note(f"Results folder: {RESULTS_DIR}")

    first = load_bgr(NIGHT_PATH, "night.png")     # Part 1 input
    sec = load_bgr(PEPPERS_PATH, "peppers.JPG")   # Part 2 input

    part1(first)
    part2(sec)

    note("\nAll statistics above are also written to results/stats_summary.txt")
    (RESULTS_DIR / "stats_summary.txt").write_text("\n".join(STATS) + "\n",
                                                   encoding="utf-8")
    note("\nDone. Figures and images are in the 'results' folder.")


if __name__ == "__main__":
    main()
