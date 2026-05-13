import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import csv
from PIL import Image
import io

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SCAN_HISTORY_FILE = "Inventory/scan_history.csv"

def save_scan(question, answer):
    with open(SCAN_HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            question,
            answer
        ])

st.title("Cletus - Broke Dad Trading Co.")
st.write("Sports Card AI Assistant")

question = st.text_input("Ask Cletus")

use_camera = st.toggle("Use Camera")

camera_photo = None

if use_camera:
    camera_photo = st.camera_input("Take a photo of your card")

uploaded_file = st.file_uploader(
    "Or upload a card photo",
    type=["jpg", "jpeg", "png"]
)

if st.button("Ask Cletus"):

    messages = [
        {
            "role": "system",
            "content": """
You are Cletus, an AI assistant for sports cards and Pokemon cards.

When a user uploads or takes a card photo, respond in this exact format:

CARD ANALYSIS
1. Card Identification:
2. Sport/Category:
3. Player/Pokemon:
4. Year/Set:
5. Raw Value Estimate:
6. Graded Value Estimate:
7. Condition Notes:
8. Centering Notes:
9. Fake/Reprint Risk:
10. Best Action: Buy / Sell Raw / Grade / Hold / Pass
11. Suggested Max Buy Price:
12. Suggested Listing Title:
13. Final Recommendation:

Be honest if you cannot fully identify the card from the image.
"""
        }
    ]

    if camera_photo or uploaded_file:
        if camera_photo:
            image = Image.open(camera_photo)
        else:
            image = Image.open(uploaded_file)

        width, height = image.size
        st.info(f"Original image resolution: {width} x {height} pixels")

        max_size = (1024, 1024)
        image.thumbnail(max_size)

        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=70)
        image_bytes = buffer.getvalue()

        new_width, new_height = image.size
        st.info(f"Optimized image resolution: {new_width} x {new_height} pixels")

        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": question or "Analyze this card photo."},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        })
    else:
        messages.append({
            "role": "user",
            "content": question
        })

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    answer = response.choices[0].message.content

    st.write("### Cletus Says:")
    st.write(answer)

    save_scan(question, answer)
    st.success("Scan saved to Cletus history.")