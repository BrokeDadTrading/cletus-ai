import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from PIL import Image
from streamlit_cropper import st_cropper



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

if photo_option == "Upload Photo":
    image_file = st.file_uploader(
        "Upload a high-resolution card photo",
        type=["jpg", "jpeg", "png"]
    )

if photo_option == "Take Photo":
    image_file = st.camera_input("Take a card photo")

if image_file:
    image = Image.open(image_file)

    st.write("Crop the card below:")

    cropped_image = st_cropper(
        image,
        realtime_update=True,
        box_color="#00FF00",
        aspect_ratio=None
    )

    st.image(cropped_image, caption="Cropped Card Image", use_container_width=True)

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

   