import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import csv
from PIL import Image
import io
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

SCAN_HISTORY_FILE = "Inventory/scan_history.csv"
INVENTORY_FILE = "Inventory/cards_inventory.csv"

os.makedirs("Inventory", exist_ok=True)

def save_scan(mode, question, answer):
    with open(SCAN_HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            mode,
            question,
            answer
        ])

def save_inventory(card_name, category, purchase_price, estimated_value, action, notes):
    file_exists = os.path.exists(INVENTORY_FILE)

    with open(INVENTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "Date",
                "Card Name",
                "Category",
                "Purchase Price",
                "Estimated Value",
                "Best Action",
                "Notes"
            ])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            card_name,
            category,
            purchase_price,
            estimated_value,
            action,
            notes
        ])

def optimize_image(file):
    image = Image.open(file)
    width, height = image.size

    max_size = (1024, 1024)
    image.thumbnail(max_size)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=70)

    return buffer.getvalue(), width, height, image.size[0], image.size[1]

def ask_cletus(mode, question, image_file=None):
    system_prompt = f"""
You are Cletus, an AI business assistant for Broke Dad Trading Co.

You specialize in:
- Sports cards
- Pokemon cards
- Grading decisions
- Buy/sell/hold recommendations
- Profit calculations
- Listing titles
- Inventory advice
- Business growth

Current mode: {mode}

If analyzing a card photo, respond in this format:

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

If you are not sure, say what is unclear and what photo/detail is needed.
"""

    messages = [{"role": "system", "content": system_prompt}]

    if image_file:
        image_bytes, old_w, old_h, new_w, new_h = optimize_image(image_file)

        st.info(f"Original image: {old_w} x {old_h}")
        st.info(f"Optimized image: {new_w} x {new_h}")

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
        messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )

    return response.choices[0].message.content

st.set_page_config(
    page_title="Cletus AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Cletus AI")
st.subheader("Broke Dad Trading Co. Sports Card Assistant")

mode = st.sidebar.selectbox(
    "Choose Cletus Mode",
    [
        "Analyze Card",
        "Grade Check",
        "Profit Calculator",
        "Listing Writer",
        "Inventory Assistant",
        "Deal Finder",
        "Business Coach"
    ]
)

st.sidebar.write("### Cletus Tools")
st.sidebar.write("📸 Card Scanner")
st.sidebar.write("💰 Profit Calculator")
st.sidebar.write("📝 Listing Writer")
st.sidebar.write("📦 Inventory Helper")
st.sidebar.write("🔎 Deal Finder")

if mode == "Profit Calculator":
    st.header("💰 Profit Calculator")

    sale_price = st.number_input("Sale Price", min_value=0.0, step=1.0)
    purchase_price = st.number_input("Purchase Price", min_value=0.0, step=1.0)
    fees = st.number_input("Platform Fees", min_value=0.0, step=1.0)
    shipping = st.number_input("Shipping Cost", min_value=0.0, step=1.0)

    if st.button("Calculate Profit"):
        profit = sale_price - purchase_price - fees - shipping

        if purchase_price > 0:
            roi = (profit / purchase_price) * 100
        else:
            roi = 0

        st.success(f"Profit: ${profit:.2f}")
        st.success(f"ROI: {roi:.1f}%")

        if profit > 0:
            st.write("Cletus says: This deal is profitable.")
        else:
            st.write("Cletus says: This deal is not profitable.")

elif mode == "Inventory Assistant":
    st.header("📦 Inventory Assistant")

    card_name = st.text_input("Card Name")
    category = st.selectbox("Category", ["Sports", "Pokemon", "Other"])
    purchase_price = st.number_input("Purchase Price", min_value=0.0, step=1.0)
    estimated_value = st.number_input("Estimated Value", min_value=0.0, step=1.0)
    action = st.selectbox("Best Action", ["Hold", "Sell Raw", "Grade", "Pass"])
    notes = st.text_area("Notes")

    if st.button("Save To Inventory"):
        save_inventory(card_name, category, purchase_price, estimated_value, action, notes)
        st.success("Card saved to inventory.")

elif mode == "Listing Writer":
    st.header("📝 Listing Writer")

    card_info = st.text_area("Enter card details")
    platform = st.selectbox("Platform", ["eBay", "Whatnot", "Fanatics Live", "Facebook", "Instagram"])

    if st.button("Create Listing"):
        prompt = f"""
Create a strong listing for this card.

Platform: {platform}
Card Details: {card_info}

Return:
1. SEO title
2. Short description
3. Long description
4. Hashtags
5. Suggested starting price strategy
"""

        answer = ask_cletus(mode, prompt)
        st.write("### Cletus Says:")
        st.write(answer)
        save_scan(mode, prompt, answer)

else:
    st.header(f"Mode: {mode}")

    question = st.text_input("Ask Cletus")

    use_camera = st.toggle("Use Camera")

    camera_photo = None

    if use_camera:
        camera_photo = st.camera_input("Take a photo of your card")

    uploaded_file = st.file_uploader(
        "Or upload a card photo",
        type=["jpg", "jpeg", "png"]
    )

    image_file = camera_photo if camera_photo else uploaded_file

    if st.button("Ask Cletus"):
        answer = ask_cletus(mode, question, image_file)

        st.write("### Cletus Says:")
        st.write(answer)

        save_scan(mode, question, answer)
        st.success("Saved to Cletus history.")