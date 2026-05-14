import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from PIL import Image
import base64
from io import BytesIO
import cv2
import numpy as np
from streamlit_mic_recorder import mic_recorder

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Cletus AI", page_icon="🤖", layout="wide")

st.markdown("""
<style>
.block-container { padding-top: 2rem; }
.card-box {
    background: #1c1f2a;
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #33384a;
    margin-bottom: 18px;
}
.big-title { font-size: 42px; font-weight: 800; }
.sub-text { color: #b8bcc8; font-size: 18px; }
</style>
""", unsafe_allow_html=True)

CHAT_MEMORY_FILE = "cletus_chat_memory.txt"


def load_chat_memory():
    if os.path.exists(CHAT_MEMORY_FILE):
        with open(CHAT_MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def save_chat_memory(user_msg, cletus_msg):
    with open(CHAT_MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\nUser: {user_msg}\nCletus: {cletus_msg}\n")


def image_to_base64(pil_image):
    buffer = BytesIO()
    pil_image.convert("RGB").save(buffer, format="JPEG", quality=95)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def auto_detect_card(pil_image):
    image = np.array(pil_image.convert("RGB"))
    original = image.copy()

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 60, 180)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    card_contour = None

    for contour in contours[:10]:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.03 * peri, True)
        area = cv2.contourArea(approx)

        if len(approx) == 4 and area > image.shape[0] * image.shape[1] * 0.15:
            card_contour = approx
            break

    if card_contour is None:
        return None, None, "Card edges not detected. Use a plain dark background and keep the full card visible."

    pts = card_contour.reshape(4, 2).astype("float32")
    rect = order_points(pts)

    width_a = np.linalg.norm(rect[2] - rect[3])
    width_b = np.linalg.norm(rect[1] - rect[0])
    height_a = np.linalg.norm(rect[1] - rect[2])
    height_b = np.linalg.norm(rect[0] - rect[3])

    max_width = int(max(width_a, width_b))
    max_height = int(max(height_a, height_b))

    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(original, matrix, (max_width, max_height))

    detected = original.copy()
    cv2.drawContours(detected, [card_contour], -1, (0, 255, 0), 8)

    return Image.fromarray(warped), Image.fromarray(detected), "Card detected and straightened."


def estimate_centering(cropped_image):
    img = np.array(cropped_image.convert("RGB"))
    h, w, _ = img.shape

    left_sample = img[:, :max(5, int(w * 0.08))]
    right_sample = img[:, int(w * 0.92):]
    top_sample = img[:max(5, int(h * 0.08)), :]
    bottom_sample = img[int(h * 0.92):, :]

    left_brightness = np.mean(left_sample)
    right_brightness = np.mean(right_sample)
    top_brightness = np.mean(top_sample)
    bottom_brightness = np.mean(bottom_sample)

    lr_diff = abs(left_brightness - right_brightness)
    tb_diff = abs(top_brightness - bottom_brightness)

    if lr_diff < 8:
        lr = "Looks fairly balanced left-to-right."
    elif left_brightness > right_brightness:
        lr = "Left border may appear wider/lighter than right."
    else:
        lr = "Right border may appear wider/lighter than left."

    if tb_diff < 8:
        tb = "Looks fairly balanced top-to-bottom."
    elif top_brightness > bottom_brightness:
        tb = "Top border may appear wider/lighter than bottom."
    else:
        tb = "Bottom border may appear wider/lighter than top."

    return lr, tb


st.markdown('<div class="big-title">🤖 Cletus AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">BroKe Dad Trading Co. — AI Card Grading Assistant</div>', unsafe_allow_html=True)
st.divider()

# ---------------- TALK/TEXT WITH CLETUS FIRST ----------------

st.header("💬 Talk/Text With Cletus")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("Or talk to Cletus")

audio = mic_recorder(
    start_prompt="🎙️ Start Recording",
    stop_prompt="⏹️ Stop Recording",
    just_once=True,
    use_container_width=True
)

user_message = st.chat_input("Ask Cletus anything...")

if audio:
    audio_bytes = audio["bytes"]

    with open("voice_input.wav", "wb") as f:
        f.write(audio_bytes)

    with open("voice_input.wav", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-mini-transcribe",
            file=audio_file
        )

    user_message = transcript.text
    st.success(f"You said: {user_message}")

if user_message:
    saved_memory = load_chat_memory()

    st.session_state.chat_history.append({"role": "user", "content": user_message})

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=f"""
You are Cletus AI, a helpful trading card assistant for BroKe Dad Trading Co.

Use this saved memory when helpful:
{saved_memory}

User message:
{user_message}

Answer naturally like a helpful assistant.
"""
    )

    cletus_reply = response.output_text

    st.session_state.chat_history.append({"role": "assistant", "content": cletus_reply})
    save_chat_memory(user_message, cletus_reply)

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

st.divider()

# ---------------- CARD GRADING SECTION ----------------

st.header("📸 Card Grading Tools")

left, right = st.columns([1, 1])

with left:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("📸 Upload Card Photos")

    front_photo = st.file_uploader("Front of card", type=["jpg", "jpeg", "png"])
    back_photo = st.file_uploader("Back of card optional", type=["jpg", "jpeg", "png"])
    closeup_photo = st.file_uploader("Corner/edge closeup optional", type=["jpg", "jpeg", "png"])

    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    st.subheader("✅ Best Photo Setup")
    st.write("""
    - Use your phone camera through Upload
    - Use bright even lighting
    - Put the card on a dark plain background
    - Keep the full card visible
    - Avoid glare
    - Take front, back, and corner closeups
    """)
    st.markdown("</div>", unsafe_allow_html=True)

images_for_ai = []

if front_photo:
    front_original = Image.open(front_photo).convert("RGB")
    front_cropped, detected_preview, detect_msg = auto_detect_card(front_original)

    st.subheader("Front Original")
    st.image(front_original, use_container_width=True)

    if front_cropped:
        st.success(detect_msg)
        st.subheader("Detected Card Edge")
        st.image(detected_preview, use_container_width=True)

        st.subheader("Auto-Cropped / Straightened Card")
        st.image(front_cropped, use_container_width=True)

        lr, tb = estimate_centering(front_cropped)
        st.info(f"Centering estimate: {lr} {tb}")

        images_for_ai.append(image_to_base64(front_original))
        images_for_ai.append(image_to_base64(front_cropped))
    else:
        st.warning(detect_msg)
        images_for_ai.append(image_to_base64(front_original))

if back_photo:
    back_image = Image.open(back_photo).convert("RGB")
    back_cropped, back_detected, back_msg = auto_detect_card(back_image)

    st.subheader("Back Original")
    st.image(back_image, use_container_width=True)

    if back_cropped:
        st.success("Back detected and straightened.")
        st.image(back_cropped, caption="Back Auto-Cropped", use_container_width=True)
        images_for_ai.append(image_to_base64(back_cropped))
    else:
        st.warning(back_msg)
        images_for_ai.append(image_to_base64(back_image))

if closeup_photo:
    closeup_image = Image.open(closeup_photo).convert("RGB")
    st.subheader("Corner / Edge Closeup")
    st.image(closeup_image, use_container_width=True)
    images_for_ai.append(image_to_base64(closeup_image))

st.divider()

grading_question = st.text_input(
    "Ask Cletus about this card",
    placeholder="Example: Is this card worth sending to PSA?"
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

            prompt = grading_question if grading_question else f"""
You are Cletus AI, a practical trading card grading assistant.

Use a {grade_style} evaluation style.

Analyze the uploaded card photos. If an auto-cropped image is included, use it to judge centering and edges, but also compare against the original photo.

Give:
1. Estimated grade range
2. Centering opinion
3. Corner condition
4. Edge condition
5. Surface/print quality
6. Back condition if included
7. Biggest grading risks
8. Whether it is worth sending to PSA/BGS/CGC
9. What better photos are needed if the images are not good enough

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
                input=[{"role": "user", "content": content}]
            )

            st.subheader("🧾 Cletus Evaluation")
            st.write(response.output_text)