"""
Build "Experiment 2 Report.docx" — a lab report in the SAME format as the
template "Experiment 2 .docx", but filled with the actual experiment2.py
implementation and the measured results of this run.

The template is opened as the base document (so page setup, styles such as
Heading 1 / ds-markdown-paragraph, and fonts are inherited), its body is
cleared, and the new content is rebuilt task by task.
"""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

BASE = Path(__file__).resolve().parent
TEMPLATE = BASE / "Experiment 2 .docx"
OUT = BASE / "Experiment 2 Report.docx"
RESULTS = BASE / "results"

TNR = "Times New Roman"
SIMSUN = "宋体"
COURIER = "Courier New"

doc = Document(str(TEMPLATE))

# --- helpers ----------------------------------------------------------------
def add_text(p, text, name=TNR, size=12, bold=None, eastasia=SIMSUN):
    """Add a run with explicit font (incl. East Asian font) and size."""
    r = p.add_run(text)
    r.font.name = name
    r.font.size = Pt(size)
    if bold is not None:
        r.font.bold = bold
    rf = r._element.get_or_add_rPr().get_or_add_rFonts()
    rf.set(qn("w:eastAsia"), eastasia)
    return r


def para(text="", name=TNR, size=12, bold=None, align=None, style=None):
    p = doc.add_paragraph(style=style)
    if align is not None:
        p.alignment = align
    if text:
        add_text(p, text, name=name, size=size, bold=bold)
    return p


def heading(text, size=14, align=None):
    p = doc.add_paragraph(style="Heading 1")
    if align is not None:
        p.alignment = align
    r = add_text(p, text, name=TNR, size=size)
    r.font.color.rgb = RGBColor(0, 0, 0)  # keep headings black
    return p


def subheading(text, size=14):
    return para(text, bold=True, size=size)


def step_heading(text):
    return para(text, bold=True, size=12)


def bullet(text):
    return para(text)


def code_block(lines):
    """Code lines in Courier New 12pt, preceded by a ' python' fence label."""
    para(" python")
    for line in lines:
        para(line, name=COURIER, size=12)


def picture(path, width_in, caption=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(width_in))
    if caption:
        para(caption)


def add_table(rows, header_bold=True):
    """Bordered table (same look as the template's tables)."""
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = doc.styles["Normal Table"]
    tblPr = t._element.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), "auto")
        borders.append(el)
    tblPr.append(borders)
    for i, row in enumerate(rows):
        for j, text in enumerate(row):
            cell = t.cell(i, j)
            cell.text = ""
            p = cell.paragraphs[0]
            add_text(p, text, size=12, bold=(header_bold and i == 0))
    return t


# --- clear the template body (keep the final sectPr = page setup) ----------
body = doc.element.body
for child in list(body):
    if child.tag != qn("w:sectPr"):
        body.remove(child)

# ============================================================================
# Header (same as the template, date updated)
# ============================================================================
para()
para("台州学院", size=42, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
para("人工智能学院实验报告", size=22, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
para(); para(); para()
para("班级 23计算机   学号 2362720051     姓名  陈光明", size=14)
para("同组                                                        ", size=14)
para(); para()
para("实验课程：     数字图像处理", size=14)
p = para("实验项目：    ", size=14)
add_text(p, "Digital Image Processing", size=14, bold=True)
para(); para(); para(); para()
para("实验日期：   2026   年   11   月   18   日", size=14,
     align=WD_ALIGN_PARAGRAPH.CENTER)
para(); para(); para()

heading("Experiment 2: Image Enhancement", size=15, align=WD_ALIGN_PARAGRAPH.CENTER)

# ============================================================================
# Experiment Objectives
# ============================================================================
heading("Experiment Objectives")
p = para(style="ds-markdown-paragraph")
add_text(p, "Further familiarize with OpenCV-based image processing functions.")
p = para(style="ds-markdown-paragraph")
add_text(p, "Master various image enhancement methods.")

# ============================================================================
# Experiment Content
# ============================================================================
heading("Experiment Content")
picture(BASE / "night.png", 2.5)
para("Figure 2-1 (a)")
para("Read the image shown in Figure 2-1 (a), night.png, denoted as FirstI. "
     "Using OpenCV image processing functions, perform the following transformations:")
bullet("Statistically compute and display the R, G, B channel histograms and the luminance histogram of FirstI;")
bullet("Perform linear and nonlinear transformations on FirstI to enhance brightness;")
bullet("Perform histogram equalization on FirstI;")
bullet("Complete the items listed in the experiment requirements.")
picture(BASE / "peppers.JPG", 2.5)
para("Figure 2-1 (b)")
para("Read the image shown in Figure 2-1 (b), peppers.jpg, denoted as SecI. "
     "Using OpenCV image processing functions, perform the following transformations:")
bullet("Add Gaussian noise to SecI to obtain NoiseI;")
bullet("Design a smoothing filter for NoiseI to suppress noise, obtaining SmoothI;")
bullet("Design a sharpening filter for SmoothI to enhance clarity;")
bullet("Complete the items listed in the experiment requirements.")

# ============================================================================
# Experiment Steps and Results
# ============================================================================
heading("Experiment Steps and Results")
p = para(style="ds-markdown-paragraph")
add_text(p, "Record the main operational steps, key code snippets, and include "
            "result screenshots. Explain which layout method you chose and the "
            "reasoning behind your choice.")
p = para(style="ds-markdown-paragraph")
add_text(p, "Briefly describe any difficulties encountered during this experiment "
            "and how you resolved them.")

subheading("Overview")
para("This experiment focuses on two core image processing tasks using OpenCV: "
     "enhancement of low-brightness night images (night.png) and noise suppression "
     "+ sharpening of color images (peppers.jpg). The whole experiment is "
     "implemented as ONE integrated script, experiment2.py: it runs every task in "
     "sequence, saves all figures and intermediate images into a results/ folder, "
     "and prints the quantitative measurements (channel statistics, PSNR, "
     "sharpness metric) quoted in the analysis below.")
para("Layout choice: every comparison figure uses a side-by-side grid in which "
     "the top row shows the processed images and the bottom row shows their "
     "luminance histograms (or zoomed crops for the sharpening task). This layout "
     "was chosen because the experiment is about gray-value statistics: the image "
     "shows the perceptual effect while the aligned histogram shows the numeric "
     "redistribution, so the two can be correlated at a glance. All figures are "
     "rendered headless (matplotlib Agg backend) and written to results/.")

para()
subheading("Pre-Experiment Preparation")
step_heading(" 1. Environment Setup")
para("Install required libraries (run in command prompt/terminal):")
code_block(["pip install opencv-python matplotlib numpy"])
para("Verify the environment: Open Python IDE (e.g., PyCharm, VS Code) and run "
     "the following test code to confirm no errors:")
code_block([
    "import cv2",
    "import matplotlib.pyplot as plt",
    'print("OpenCV version:", cv2.__version__)      # should output version >= 4.0',
    'print("Matplotlib version:", plt.__version__)  # should output version >= 3.0',
])
step_heading(" 2. Image Preparation")
para("Place night.png and peppers.JPG in the same folder as experiment2.py. "
     "The script uses pathlib and exits with a clear error message if a file is "
     "missing, so no silent failures can occur. The results/ folder is created "
     "automatically on the first run.")

para()
# ============================================================================
# Part 1
# ============================================================================
subheading("Part 1: Process night.png (Denoted as FirstI)")

subheading("Task 1: Compute and Display R/G/B Channel Histograms + Luminance Histogram")
step_heading("Step 1: Code Execution")
para("This is the first section of experiment2.py (the whole experiment runs as "
     "one script; each task below shows the relevant section):")
code_block([
    "# experiment2.py -- Task 1: histograms + statistics",
    "import cv2, numpy as np",
    "import matplotlib.pyplot as plt",
    "",
    "def load_bgr(path, name):            # robust loading (file-not-found check)",
    "    if not path.exists():",
    "        sys.exit(f\"[ERROR] Could not find {name} at {path}.\")",
    "    img = cv2.imread(str(path), cv2.IMREAD_COLOR)",
    "    if img is None:",
    "        sys.exit(f\"[ERROR] OpenCV could not decode {name}.\")",
    "    return img",
    "",
    "def luminance_hist(img):             # 256-bin luminance (gray) histogram",
    "    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)",
    "    return cv2.calcHist([gray], [0], None, [256], [0, 256])",
    "",
    "b, g, r = cv2.split(first)          # first = night.png (BGR order)",
    "gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)",
    "hists = {\"R\": cv2.calcHist([r], [0], None, [256], [0, 256]),",
    "         \"G\": cv2.calcHist([g], [0], None, [256], [0, 256]),",
    "         \"B\": cv2.calcHist([b], [0], None, [256], [0, 256]),",
    "         \"Luminance\": cv2.calcHist([gray], [0], None, [256], [0, 256])}",
    "",
    "fig, axes = plt.subplots(2, 2, figsize=(10, 7))   # 2x2 side-by-side layout",
    "for ax, (name, hist) in zip(axes.ravel(), hists.items()):",
    "    ax.plot(hist.ravel(), color=colors[name], lw=1.2)",
    "    ax.axvline(hist.argmax(), color=\"gray\", ls=\":\", lw=1)",
    "    ax.set_title(f\"{name} channel histogram\")",
    "    ax.set_xlim([0, 255])",
    "fig.savefig(\"results/fig1_histograms.png\", dpi=150, bbox_inches=\"tight\")",
])
step_heading("Step 2: Run the Code")
para("Run experiment2.py in the IDE. The statistics are computed with numpy "
     "(mean / std / min / max / median per channel) and printed:")
code_block([
    "B: mean=  27.61  std=  26.16  min=  3  max=255  median=   20.0",
    "G: mean=  25.70  std=  24.86  min=  2  max=254  median=   20.0",
    "R: mean=  28.87  std=  20.95  min=  7  max=253  median=   25.0",
    "Luminance: mean=  26.84  std=  23.67  min=  4  max=250",
])
para("Saved output: results/fig1_histograms.png.")
picture(RESULTS / "fig1_histograms.png", 5.5)
step_heading("Step 3: Result Analysis")
add_table([
    ["Visual Content", "Key Observations"],
    ["Original Image", "Dark overall (night scene), with only a few bright areas "
     "(e.g., distant lights)."],
    ["Histograms", "All 4 histograms (R/G/B/luminance) are concentrated in the "
     "low pixel range 0-100; the measured means are R=28.87, G=25.70, B=27.61 and "
     "luminance=26.84. This confirms the image is underexposed, matching the "
     "night scene characteristics."],
])
para()

subheading("Task 2: Linear & Nonlinear Transformation for Brightness Enhancement")
step_heading("Step 1: Code Execution")
code_block([
    "# experiment2.py -- Task 2: linear & nonlinear brightness enhancement",
    "def linear_transform(img, alpha, beta):",
    "    \"\"\"Point operation: out = alpha * in + beta (clipped to [0, 255]).\"\"\"",
    "    return np.clip(alpha * img.astype(np.float32) + beta, 0, 255).astype(np.uint8)",
    "",
    "def gamma_correct(img, gamma):",
    "    \"\"\"Power-law transform via LUT: out = 255 * (in/255) ** (1/gamma).\"\"\"",
    "    table = (np.arange(256, dtype=np.float32) / 255.0) ** (1.0 / gamma) * 255.0",
    "    table = np.clip(table, 0, 255).astype(np.uint8)",
    "    return cv2.LUT(img, table)",
    "",
    "ALPHA, BETA = 2.2, 25    # gain 2.2 + offset 25 (mean 27 -> ~82)",
    "GAMMA = 2.2              # gamma > 1 brightens the dark image",
    "",
    "lin = linear_transform(first, ALPHA, BETA)",
    "gam = gamma_correct(first, GAMMA)",
    "",
    "fig, axes = plt.subplots(2, 3, figsize=(12.5, 7))",
    "# top row: original / linear / gamma images;",
    "# bottom row: the matching luminance histograms with the mean marked",
])
step_heading("Step 2: Run the Code")
para("After execution, the following statistics are printed and a comparison "
     "figure plus two standalone images are saved:")
code_block([
    "Linear transform  (alpha=2.2, beta=25): mean 27.4 -> 82.5",
    "Gamma transform   (gamma=2.2):          mean 27.4 -> 87.5",
])
para("Saved output: results/fig2_brightness.png, results/12_linear.png, "
     "results/13_gamma.png.")
picture(RESULTS / "fig2_brightness.png", 5.7)
step_heading("Step 3: Result Analysis")
add_table([
    ["Enhancement Method", "Visual Effect", "Advantages/Disadvantages"],
    ["Linear (α=2.2, β=25)", "All pixels are scaled by 2.2 and shifted by +25; "
     "the scene becomes clearly visible, but the already-bright lamps saturate "
     "at 255 (slightly overexposed).", "Advantage: one multiply + one add per "
     "pixel, very fast; Disadvantage: hard clipping of bright pixels."],
    ["Nonlinear (γ=2.2)", "Dark tones are lifted much more than bright ones "
     "(the curve is steepest near 0), so shadow details such as building edges "
     "and tree branches become clear while the lights stay intact.",
     "Advantage: natural brightness without clipping; Disadvantage: needs a LUT "
     "(slightly more computation than the linear transform)."],
])
para()

subheading("Task 3: Histogram Equalization for FirstI")
step_heading("Step 1: Code Execution")
code_block([
    "# experiment2.py -- Task 3: histogram equalization on the Y channel",
    "def equalize_y(img):",
    "    \"\"\"HE applied ONLY to Y in YCrCb to avoid hue shifts.\"\"\"",
    "    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)",
    "    y, cr, cb = cv2.split(ycrcb)",
    "    y_eq = cv2.equalizeHist(y)",
    "    return cv2.cvtColor(cv2.merge([y_eq, cr, cb]), cv2.COLOR_YCrCb2BGR)",
    "",
    "def clahe_y(img, clip_limit=3.0, tile=(8, 8)):",
    "    \"\"\"CLAHE on Y: contrast-limited + local (per-tile) equalization.\"\"\"",
    "    ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)",
    "    y, cr, cb = cv2.split(ycrcb)",
    "    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile)",
    "    y_cl = clahe.apply(y)",
    "    return cv2.cvtColor(cv2.merge([y_cl, cr, cb]), cv2.COLOR_YCrCb2BGR)",
    "",
    "he = equalize_y(first)     # global equalization",
    "cl = clahe_y(first)        # improved local method (CLAHE)",
])
step_heading("Step 2: Run the Code")
code_block([
    "Histogram equalization (Y channel): mean 27.4 -> 132.0",
    "CLAHE (clip=3.0, 8x8 tiles):        mean 27.4 ->  50.3",
])
para("Saved output: results/fig3_equalization.png, results/14_equalized_y.png, "
     "results/15_clahe.png.")
picture(RESULTS / "fig3_equalization.png", 5.7)
step_heading("Step 3: Result Analysis")
bullet("Key effect: HE stretches the originally concentrated low-brightness "
       "histogram across the whole 0-255 range. Dark details (window frames, "
       "road edges) become clearly visible; the equalized histogram shows the "
       "typical comb-shaped gaps of global equalization.")
bullet("Color preservation: because only the Y channel is equalized (Cr/Cb are "
       "untouched), the measured mean hue shift between the original and the "
       "result is only ~1.9 degrees, i.e., no color distortion occurs.")
bullet("CLAHE: contrast is amplified locally per 8x8 tile and limited by "
       "clipLimit=3.0, so the bright sky is not over-amplified and the result "
       "looks more balanced than global HE.")

para()
# ============================================================================
# Part 2
# ============================================================================
subheading("Part 2: Process peppers.jpg (Denoted as SecI)")

subheading("Task 1: Add Gaussian Noise to Obtain NoiseI")
step_heading("Step 1: Code Execution")
code_block([
    "# experiment2.py -- Part 2 Task 1: add Gaussian noise",
    "def add_gaussian_noise(img, sigma=25.0, seed=42):",
    "    \"\"\"Zero-mean Gaussian noise with standard deviation sigma.\"\"\"",
    "    rng = np.random.default_rng(seed)     # fixed seed -> reproducible",
    "    noise = rng.normal(0.0, sigma, img.shape)",
    "    return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)",
    "",
    "def psnr(ref, img):                       # quality measure in dB",
    "    mse = np.mean((ref.astype(np.float64) - img.astype(np.float64)) ** 2)",
    "    return 20.0 * np.log10(255.0 / np.sqrt(mse))",
    "",
    "SIGMA = 25.0",
    "noise_i = add_gaussian_noise(sec, SIGMA)  # sec = peppers.jpg",
    "print(f\"PSNR(SecI, NoiseI) = {psnr(sec, noise_i):.2f} dB\")",
])
step_heading("Step 2: Run the Code")
code_block([
    "Gaussian noise added (sigma=25):  PSNR(SecI, NoiseI) = 20.48 dB",
])
para("Saved output: results/21_noise.png, results/fig4a_noise.png.")
picture(RESULTS / "fig4a_noise.png", 5.7)
step_heading("Step 3: Result Analysis")
bullet("NoiseI characteristics: fine random grain covers the whole image. The "
       "overall shape and color of the peppers are retained, but small details "
       "(e.g., pepper skin texture) are masked by the noise.")
bullet("Quantitative check: the measured PSNR of 20.48 dB matches the "
       "theoretical value for σ=25 noise, 20*log10(255/25) = 20.2 dB, which "
       "confirms the noise model is implemented correctly.")

para()
subheading("Task 2: Design Smoothing Filter to Obtain SmoothI")
step_heading("Step 1: Code Execution")
code_block([
    "# experiment2.py -- Part 2 Task 2: smoothing filters (compared by PSNR)",
    "mean5    = cv2.blur(noise_i, (5, 5))                       # arithmetic mean",
    "smooth_i = cv2.GaussianBlur(noise_i, (5, 5), sigmaX=1.2)   # SmoothI",
    "median5  = cv2.medianBlur(noise_i, 5)                      # median",
    "",
    "for name, im in ((\"Mean 5x5\", mean5), (\"Gaussian 5x5\", smooth_i),",
    "                 (\"Median 5x5\", median5)):",
    "    print(f\"PSNR(SecI, {name}) = {psnr(sec, im):.2f} dB\")",
])
step_heading("Step 2: Run the Code")
code_block([
    "PSNR(SecI,       Noisy) =  20.48 dB",
    "PSNR(SecI,    Mean 5x5) =  23.69 dB",
    "PSNR(SecI, Gaussian 5x5) =  25.08 dB",
    "PSNR(SecI,  Median 5x5) =  25.99 dB",
])
para("Saved output: results/22_smooth_mean.png, results/23_smooth_gaussian.png, "
     "results/24_smooth_median.png, results/fig4b_smoothing.png.")
picture(RESULTS / "fig4b_smoothing.png", 5.5)
step_heading("Step 3: Result Analysis")
bullet("SmoothI effect: the Gaussian filter (chosen as SmoothI because it is "
       "the optimal filter for Gaussian-distributed noise) removes the visible "
       "grain; PSNR rises from 20.48 dB to 25.08 dB.")
bullet("Comparison: the arithmetic mean filter (23.69 dB) blurs edges the "
       "most; the median filter (25.99 dB) preserves edges best here because "
       "peppers contains strong color boundaries.")
bullet("Trade-off: smoothing slightly blurs the edges - this is restored by "
       "the sharpening filter in the next task.")

para()
subheading("Task 3: Design Sharpening Filter to Enhance Clarity")
step_heading("Step 1: Code Execution")
code_block([
    "# experiment2.py -- Part 2 Task 3: sharpening (two methods)",
    "def unsharp_mask(img, k=1.5, kernel=(5, 5), sigma=1.5):",
    "    \"\"\"Unsharp masking: sharp = img + k * (img - blur(img)).\"\"\"",
    "    blur = cv2.GaussianBlur(img, kernel, sigma)",
    "    return cv2.addWeighted(img, 1.0 + k, blur, -k, 0)",
    "",
    "LAPLACIAN_KERNEL_4 = np.array([[0, -1, 0],",
    "                               [-1, 5, -1],",
    "                               [0, -1, 0]], np.float32)",
    "",
    "def laplacian_sharpen(img, kernel=LAPLACIAN_KERNEL_4):",
    "    \"\"\"Composite kernel f + Laplacian(f) applied with cv2.filter2D.\"\"\"",
    "    return cv2.filter2D(img, -1, kernel)",
    "",
    "def sharpness_metric(img):              # variance of the Laplacian",
    "    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)",
    "    return float(cv2.Laplacian(gray, cv2.CV_64F).var())",
    "",
    "sharp_usm = unsharp_mask(smooth_i, k=1.5)   # k = detail amount",
    "sharp_lap = laplacian_sharpen(smooth_i)",
])
step_heading("Step 2: Run the Code")
code_block([
    "Sharpness metric (variance of Laplacian):",
    "            SecI:    1751.0",
    "          NoiseI:    6788.9",
    "         SmoothI:      63.7",
    "   Unsharp k=1.5:     218.8",
    "       Laplacian:     330.2",
])
para("Saved output: results/fig5_sharpening.png, results/25_unsharp.png, "
     "results/26_laplacian.png.")
picture(RESULTS / "fig5_sharpening.png", 5.7)
step_heading("Step 3: Result Analysis")
bullet("Sharpened effect: both methods restore the edge clarity lost during "
       "smoothing; the zoomed crops in the bottom row of the figure show "
       "crisper pepper outlines and stem edges.")
bullet("Unsharp masking (k=1.5): the parameter k controls how much "
       "high-frequency detail is added back - a moderate value avoids halos "
       "around edges.")
bullet("Laplacian (4-neighbour composite kernel): a pure second-derivative "
       "sharpening; here its effect is slightly stronger than USM (330.2 vs "
       "218.8).")
bullet("Note on the metric: NoiseI scores 6788.9 because noise is itself "
       "high-frequency energy. This is exactly why sharpening is applied AFTER "
       "smoothing - sharpening NoiseI directly would amplify the grain.")

para()
# ============================================================================
# Experiment Summary
# ============================================================================
subheading("Experiment Summary")
step_heading("Key Results & Files")
para("After running experiment2.py, all output files are written to the "
     "results/ folder (organized by task):")
add_table([
    ["Task", "Output Files", "Purpose"],
    ["1 (Histograms)", "results/fig1_histograms.png",
     "R/G/B + luminance histograms and statistics of night.png"],
    ["2 (Brightness)", "results/fig2_brightness.png, results/12_linear.png, results/13_gamma.png",
     "Linear (α=2.2, β=25) and gamma (γ=2.2) enhancement"],
    ["3 (Equalization)", "results/fig3_equalization.png, results/14_equalized_y.png, results/15_clahe.png",
     "HE on the Y channel and CLAHE results"],
    ["4 (Add Noise)", "results/fig4a_noise.png, results/21_noise.png",
     "Noisy version of peppers.jpg (σ=25, PSNR 20.48 dB)"],
    ["5 (Smoothing)", "results/fig4b_smoothing.png, results/22_smooth_mean.png, results/23_smooth_gaussian.png, results/24_smooth_median.png",
     "Noise-suppressed images with PSNR comparison"],
    ["6 (Sharpening)", "results/fig5_sharpening.png, results/25_unsharp.png, results/26_laplacian.png",
     "Sharpened images (Unsharp masking and Laplacian)"],
    ["- (Statistics)", "results/stats_summary.txt",
     "All measured numbers (means, PSNR, sharpness metric)"],
])
para()
step_heading("Difficulties Encountered & Solutions")
add_table([
    ["Difficulty", "Solution"],
    ["\"File not found\" error", "Use pathlib with an explicit existence check "
     "and a clear error message; keep the images in the same folder as the script."],
    ["Color distortion in histogram equalization",
     "Do not equalize the BGR channels directly; convert to YCrCb, equalize "
     "only the Y channel, then convert back (measured hue shift only ~1.9°)."],
    ["Overexposure / clipping in linear enhancement",
     "The bright lamps saturate at 255 with the linear transform; use gamma "
     "correction (γ=2.2) instead, which lifts shadows more than highlights."],
    ["Blurred edges after smoothing",
     "Restore details with unsharp masking (k=1.5) or the Laplacian composite "
     "kernel, applied after smoothing."],
    ["Sharpening amplifies noise",
     "Never sharpen NoiseI directly (its Laplacian-variance metric is 6788.9 "
     "vs 1751.0 for the clean image); always smooth first, then sharpen."],
    ["Figure windows pop up / block the script",
     "Use the matplotlib Agg backend and savefig() so all figures are written "
     "to results/ automatically without opening windows."],
])
para()
step_heading("Experiment Objectives Achieved")
bullet("Familiarized with OpenCV functions: cv2.imread, cv2.cvtColor, "
       "cv2.calcHist, cv2.LUT, cv2.equalizeHist, cv2.createCLAHE, cv2.blur, "
       "cv2.GaussianBlur, cv2.medianBlur, cv2.addWeighted, cv2.filter2D, "
       "cv2.Laplacian, etc.")
bullet("Mastered brightness enhancement: linear (α=2.2, β=25, mean 27.4 → 82.5) "
       "vs nonlinear gamma correction (γ=2.2, mean 27.4 → 87.5).")
bullet("Mastered contrast improvement: histogram equalization on the Y channel "
       "(mean 27.4 → 132.0) and the improved CLAHE method (mean 27.4 → 50.3).")
bullet("Mastered noise suppression + sharpening: Gaussian smoothing raised PSNR "
       "from 20.48 dB to 25.08 dB; sharpening raised the Laplacian-variance "
       "metric from 63.7 to 218.8 (USM) / 330.2 (Laplacian).")

doc.save(str(OUT))
print(f"Saved: {OUT}")
