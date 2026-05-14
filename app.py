import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from PIL import Image
import base64
from io import BytesIO

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="Cletus AI",
    page_icon="🤖",
    layout="wide"
)

st.markdown("""
<style>
.main {
    background-color: #0f1117;
}
.block-container {
    padding-top: 2rem;
}
.card-box {
    background: #1c1f2a;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #33384a;
    margin-bottom: 18px;
}
.big-title {
    font-size: 42px;
    font-weight: 800;
}
.sub-text {
    color: #b8bcc8;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

def image_to_base64(uploaded_file):
    image = Image.open(uploaded_file).convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return image, encoded

st.markdown('<div class="big-title">🤖 Cletus AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">BroKe Dad Trading Co. — AI Card Grading Assistant</div>', unsafe_allow_html=True)
st.divider()

left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("📸 Upload Card Photos")

    front_photo = st.file_uploader(
        "Front of card",
        type=["jpg", "jpeg", "png"],
        help="Use your phone camera through Upload for best quality."
    )

    back_photo = st.file_uploader(
        "Back of card optional but recommended",
        type=["jpg", "jpeg", "png"]
    )

    corner_photo = st.file_uploader(
        "Corner/edge closeup optional",
        type=["jpg", "jpeg", "png"]
    )

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("✅ Photo Tips")
    st.write("""
    For best grading results:
    - Use bright, even lighting
    - Avoid glare
    - Fill most of the photo with the card
    - Take one straight front photo
    - Take one straight back photo
    - Add a closeup if corners or edges are questionable
    """)
    st.markdown("</div>", unsafe_allow_html=True)

images_for_ai = []

if front_photo:
    front_image, front_base64 = image_to_base64(front_photo)
    st.subheader("Front Preview")
    st.image(front_image, use_container_width=True)
    images_for_ai.append(front_base64)

if back_photo:
    back_image, back_base64 = image_to_base64(back_photo)
    st.subheader("Back Preview")
    st.image(back_image, use_container_width=True)
    images_for_ai.append(back_base64)

if corner_photo:
    corner_image, corner_base64 = image_to_base64(corner_photo)
    st.subheader("Closeup Preview")
    st.image(corner_image, use_container_width=True)
    images_for_ai.append(corner_base64)

st.divider()

question = st.text_input(
    "Ask Cletus",
    placeholder="Example: Grade this card and tell me if it is worth sending to PSA."
)

grade_style = st.selectbox(
    "Choose grading style",
    ["PSA-style", "BGS-style", "CGC-style", "General collector opinion"]
)

if st.button("🔍 Run Cletus Grading Review", use_container_width=True):
    if not images_for_ai:
        st.warning("Please upload at least the front of the card first.")
    else:
        with st.spinner("Cletus is inspecting centering, corners, edges, and surface..."):

            prompt = question if question else f"""
You are Cletus AI, a practical trading card grading assistant.

Use a {grade_style} evaluation style.

Analyze the uploaded card photos and give:
1. Estimated grade range
2. Centering opinion
3. Corner condition
4. Edge condition
5. Surface/print quality
6. Back condition if back photo is included
7. Biggest grading risks
8. Whether it is worth sending to PSA/BGS/CGC
9. What better photos are needed if the image is not good enough

Be honest. Do not guarantee a grade.
"""

            content = [{"type": "input_text", "text": prompt}]

            for img in images_for_ai:
                content.append({
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{img}",
                    "detail": "high"
                })

            response = client.responses.create(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

            st.subheader("🧾 Cletus Evaluation")
            st.write(response.output_text)