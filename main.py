import os

import gradio as gr
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key missing! Check your .env file.")

client = genai.Client(api_key=api_key)

APP_NAME = "CivicLens AI"
TAGLINE = "AI-powered public infrastructure issue detection"

SYSTEM_PROMPT = """
You are CivicLens AI, a professional civic infrastructure reporting assistant
used by municipal teams and field inspectors.

Examine the uploaded photograph and identify whether it contains:
- Pothole or damaged road
- Overflowing garbage
- Broken streetlight
- Water leakage
- Damaged public infrastructure
- No identifiable civic issue

Provide your report in this exact structure:

## 1. Detected Issue
(one-line conclusion)

## 2. Visual Evidence
(bullet list of what is visible in the photo)

## 3. Estimated Severity
(One of: 🟢 Low, 🟡 Medium, 🔴 High — with a one-line justification)

## 4. Public Safety Impact
(short paragraph)

## 5. Suggested Municipal Department
(the responsible department, e.g. Roads, Sanitation, Lighting, Water)

## 6. Formal Complaint Draft
(a ready-to-send formal complaint text the citizen can submit)

Rules:
- Do not claim a problem exists if it is not visible in the image.
- State clearly that severity is an AI estimate and requires human verification.
- Keep the tone formal, factual and concise.
"""

EXAMPLE_IMAGE = "IMG-20261108-WA0019.jpg"

# ---------------------------------------------------------------- CSS ------
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --civic-bg: #0d1117;
    --civic-surface: #161b22;
    --civic-border: #29303c;
    --civic-primary: #2563eb;
    --civic-accent: #38bdf8;
    --civic-text: #e6edf3;
    --civic-muted: #8b949e;
}

.gradio-container,
body {
    background: var(--civic-bg) !important;
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    color: var(--civic-text) !important;
}

/* ---------- Header banner ---------- */
.civic-header {
    background: linear-gradient(135deg, #0f2027 0%, #1e3a5f 45%, #2563eb 130%);
    border: 1px solid var(--civic-border);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
}

.civic-logo {
    font-size: 42px;
    line-height: 1;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,.4));
}

.civic-title {
    font-size: 30px;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -.5px;
}

.civic-subtitle {
    margin: 4px 0 0 0;
    color: #c7d7ef;
    font-size: 15px;
    font-weight: 500;
}

.civic-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    padding: 3px 10px;
    border-radius: 999px;
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #7dd3fc;
    font-size: 11.5px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .6px;
}

/* ---------- Cards / panels ---------- */
.civic-panel {
    background: var(--civic-surface) !important;
    border: 1px solid var(--civic-border) !important;
    border-radius: 14px !important;
    padding: 18px !important;
}

.civic-label {
    font-size: 12px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: var(--civic-muted) !important;
    margin-bottom: 10px;
}

/* ---------- Image upload ---------- */
#civic-upload .wrap,
#civic-upload .container {
    background: #10151d !important;
    border: 1.5px dashed #3b4559 !important;
    border-radius: 12px !important;
    color: var(--civic-muted);
}

/* ---------- Buttons ---------- */
button#detect-btn {
    background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    padding: 12px 0 !important;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35);
    transition: transform .12s ease, box-shadow .12s ease;
}

button#detect-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.5);
}

button#detect-btn:active {
    transform: translateY(0);
}

button#clear-btn {
    border-radius: 10px !important;
    font-weight: 600 !important;
    background: transparent !important;
    border: 1px solid var(--civic-border) !important;
    color: var(--civic-muted) !important;
}

button#clear-btn:hover {
    color: #fff !important;
    border-color: #46536b !important;
}

/* ---------- Report panel ---------- */
#civic-report {
    min-height: 220px;
}

#civic-report .prose,
#civic-report .markdown {
    color: var(--civic-text) !important;
}

#civic-report h3 {
    color: #7dd3fc !important;
    border-bottom: 1px solid var(--civic-border);
    padding-bottom: 4px;
}

/* ---------- Footer ---------- */
.civic-footer {
    margin-top: 22px;
    padding: 14px 20px;
    background: var(--civic-surface);
    border: 1px solid var(--civic-border);
    border-radius: 12px;
    color: var(--civic-muted);
    font-size: 12.5px;
    text-align: center;
}

.civic-footer code {
    color: var(--civic-accent);
}
"""

# ------------------------------------------------------------- Helpers -----


def detect_issue(image):
    """Run the civic infrastructure analysis on the uploaded image."""
    if image is None:
        raise gr.Error("Please upload a photograph first.")

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[SYSTEM_PROMPT, image],
        )
    except Exception as exc:  # keep the failure user-friendly
        raise gr.Error(f"Analysis failed: {exc}") from exc

    report = (response.text or "").strip()
    if not report:
        raise gr.Error("The model returned an empty response. Please try again.")

    return report


with gr.Blocks(
    title=f"{APP_NAME} — Civic Issue Detection",
    theme=gr.themes.Base(
        primary_hue="blue",
        neutral_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "Segoe UI", "sans-serif"],
    ),
    css=CUSTOM_CSS,
) as demo:

    # ------------------------------------------------ Header ------------
    with gr.Row(elem_classes=["civic-header"]):
        with gr.Column(scale=1, min_width=60):
            gr.Markdown("<div class='civic-logo'>🏙️</div>")
        with gr.Column(scale=16):
            gr.Markdown(
                f"<h1 class='civic-title'>{APP_NAME}</h1>"
                f"<p class='civic-subtitle'>{TAGLINE}</p>"
                "<span class='civic-badge'>⚡ Gemini Vision Assistant</span>",
                elem_id="header-text",
            )

    # ------------------------------------------------ Main row ----------
    with gr.Row(equal_height=True):

        # ---- Left: input ----
        with gr.Column(scale=5):
            gr.Markdown("<div class='civic-label'>📷  Photograph Input</div>")
            upload = gr.Image(
                type="pil",
                sources=["upload", "webcam", "clipboard"],
                label="Upload a civic issue photograph",
                elem_id="civic-upload",
                height=380,
                interactive=True,
                
            )

            with gr.Row():
                detect_btn = gr.Button(
                    "🔍  Detect Public Issue",
                    variant="primary",
                    elem_id="detect-btn",
                    scale=3,
                )
                clear_btn = gr.ClearButton(
                    [upload],
                    value="🗑  Clear",
                    elem_id="clear-btn",
                    scale=1,
                )

        # ---- Right: report ----
        with gr.Column(scale=6):
            gr.Markdown("<div class='civic-label'>🧾  Analysis Report</div>")
            report = gr.Markdown(
                value=(
                    "**No analysis yet.**\n\n"
                    "Upload a photograph of a civic issue and press "
                    "*Detect Public Issue* — the AI will identify the problem, "
                    "assess estimated severity, and draft a formal complaint "
                    "you can submit to the municipality."
                ),
                elem_id="civic-report",
            )

    # ------------------------------------------------ Footer ------------
    gr.Markdown(
        "<div class='civic-footer'>"
        f"<b>{APP_NAME}</b> &nbsp;|&nbsp; severity levels are AI estimates "
        "and require human verification before official action. &nbsp;|&nbsp; "
        "Powered by <code>gemini-2.5-flash</code>"
        "</div>",
        elem_id="footer",
    )

    # ------------------------------------------------ Events ------------
    detect_btn.click(
        fn=detect_issue,
        inputs=upload,
        outputs=report,
        api_name="detect_issue",
    )

demo.launch()
