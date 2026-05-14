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
    
    cropped_image.save("data/latest_card_crop.png")

    st.success("Cropped high-resolution image saved.")

question = st.text_input("Ask Cletus something")

if st.button("Run Cletus"):

    # Read memory file
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            memory = file.read()
    except:
        memory = ""

    # Send to OpenAI
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": f"""
                You are Cletus AI.

                Here is your long-term memory:
                {memory}

                Use this memory to help the user.
                """
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    answer = response.choices[0].message.content

    # Save conversation into memory
    with open(MEMORY_FILE, "a", encoding="utf-8") as file:
        file.write(f"\nUSER: {question}\n")
        file.write(f"CLETUS: {answer}\n")

    # Show only newest response
    st.write(answer)

   