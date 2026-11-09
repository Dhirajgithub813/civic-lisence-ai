---
title: CivicLens AI
emoji: 🏙️
colorFrom: blue
colorTo: gray
sdk: gradio
sdk_version: "6.31.0"
app_file: main.py
pinned: false
license: mit
---

# CivicLens AI

AI-powered public infrastructure issue detection.
Upload a photograph of a pothole, overflowing garbage, broken streetlight or
water leakage, and the app produces a structured civic report (detected issue,
severity, safety impact, responsible department, ready-to-send complaint draft)
using Google Gemini Vision (gemini-2.5-flash).

## Setup

- Create a Space with the **Gradio** SDK (this README configures it).
- Add your key as a Space **Secret** named `GEMINI_API_KEY`
  (Space Settings → Variables & secrets).
- Push files: `main.py`, `requirements.txt`, and this `README.md`.

> `sdk_version` must match a version Hugging Face supports — if the build
> complains about `6.31.0`, pick the closest version offered in the Space UI.
