import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from PIL import Image
import base64
from io import BytesIO

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Cletus", layout="wide")

st.title("🤖 Cletus AI")
st.subheader("BroKe Dad Trading Co.")
st.divider()

st.header("📸 High-Resolution Card Photo Grader")

photo = st.file_uploader(
    "Upload or take a high-resolution card photo",
    type=["jpg", "jpeg", "png"],
    help="On your phone, tap Upload, then choose Camera for best quality, zoom, and focus."
)

image = None
image_base64 = None

if photo:
    image = Image.open(photo).convert("RGB")
    st.image(image, caption="Original high-resolution image", use_container_width=True)
    st.success("Photo loaded in full resolution.")

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

question = st.text_input("Ask Cletus something", placeholder="Example: Grade this card and tell me what defects you see.")

if st.button("Run Cletus"):
    if image_base64 is None:
        st.warning("Please upload a card photo first.")
    else:
        st.write("Cletus is evaluating your card photo...")

        prompt = question if question else (
            "Evaluate this trading card photo. Look at centering, corners, edges, "
            "surface, print quality, whitening, scratches, and give an estimated grade range. "
            "Be clear and practical."
        )

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "high"
                        }
                    ]
                }
            ]
        )

        st.subheader("Cletus Evaluation")
        st.write(response.output_text)