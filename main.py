import gradio as gr
from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("API Key missing! Check your .env file.")

client = genai.Client(api_key=api_key)


def detect_issue(image):

    if image is None:
        return "Please upload an image."

    prompt = """
    You are an AI civic infrastructure assistant.

    Examine the uploaded photograph.

    Identify whether it contains:
    - Pothole or damaged road
    - Overflowing garbage
    - Broken streetlight
    - Water leakage
    - Damaged public infrastructure
    - No identifiable civic issue

    Provide:

    1. Detected issue
    2. Visual evidence
    3. Estimated severity: Low, Medium or High
    4. Potential public safety impact
    5. Suggested municipal department
    6. A formal complaint draft

    Do not claim that a problem exists if it is not
    visible in the image.

    State that severity is an AI estimate and needs
    human verification.
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, image]
    )

    return response.text


with gr.Blocks(title="CivicLens AI") as demo:

    gr.Markdown("# 🏙️ CivicLens AI")
    gr.Markdown(
        "AI-powered public infrastructure issue detection"
    )

    image = gr.Image(
        type="pil",
        label="Upload a civic issue photograph"
    )

    button = gr.Button("Detect Public Issue")

    output = gr.Markdown()

    button.click(
        fn=detect_issue,
        inputs=image,
        outputs=output
    )


demo.launch()