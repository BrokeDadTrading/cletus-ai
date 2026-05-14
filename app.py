import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from PIL import Image
from streamlit_cropper import st_cropper
from PIL import Image


MEMORY_FILE = "data/memory.txt"

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Cletus", layout="wide")

st.title("🤖 Cletus AI")
st.subheader("BroKe Dad Trading Co.")
st.divider()
st.header("📸 Card Photo Grader")

photo_option = st.radio(
    "Choose photo method",
    ["Upload Photo", "Take Photo"]
)

image_file = None

from PIL import Image

st.subheader("📸 High-Resolution Card Photo")

photo = st.file_uploader(
    "Upload or take a high-resolution card photo",
    type=["jpg", "jpeg", "png"],
    help="On your phone, tap Upload, then choose Camera for best quality, zoom, and focus."
)

image = None

if photo:
    image = Image.open(photo)
    st.image(image, caption="Original high-resolution image", use_container_width=True)

    st.success("Photo loaded in full resolution.")


    st.success("Cropped high-resolution image saved.")

question = st.text_input("Ask Cletus something")

if st.button("Run Cletus"):
    if image is None:
        st.warning("Please upload a card photo first.")
    else:
        st.write("Cletus is evaluating your card photo...")

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Evaluate this trading card photo. Look at centering, corners, edges, surface, print quality, and give an estimated grade range. Be clear and practical."
                        },
                        {
                            "type": "input_image",
                            "image_url": image
                        }
                    ]
                }
            ]
        )

        st.write(response.output_text)