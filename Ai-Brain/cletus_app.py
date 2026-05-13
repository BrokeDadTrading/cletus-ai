import streamlit as st
from openai import OpenAI
import base64
from datetime import datetime
import csv
from PIL import Image
import io
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

os.makedirs("Inventory", exist_ok=True)

TASKS_FILE = "Inventory/tasks.csv"

SCAN_HISTORY_FILE = "Inventory/scan_history.csv"
INVENTORY_FILE = "Inventory/cards_inventory.csv"

st.set_page_config(
    page_title="Cletus AI",
    page_icon="🤖",
    layout="wide"
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "growth_goal" not in st.session_state:
    st.session_state.growth_goal = "Build Broke Dad Trading Co. into a profitable sports card business."

def save_scan(mode, question, answer):
    with open(SCAN_HISTORY_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            mode,
            question,
            answer
        ])

def save_task(task, priority, status, notes):

    with open(TASKS_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            task,
            priority,
            status,
            notes
        ])

def load_tasks():

    tasks = []

    if os.path.exists(TASKS_FILE):

        with open(TASKS_FILE, "r", encoding="utf-8") as file:
            reader = csv.reader(file)

            next(reader, None)

            for row in reader:
                tasks.append(row)

    return tasks


def optimize_image(file):
    image = Image.open(file)
    old_w, old_h = image.size

    max_size = (1024, 1024)
    image.thumbnail(max_size)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=70)

    return buffer.getvalue(), old_w, old_h, image.size[0], image.size[1]

def ask_cletus(mode, question, image_file=None):
    system_prompt = f"""
You are Cletus, the AI growth assistant for Broke Dad Trading Co.

Personality:
- Helpful
- Honest
- Business-minded
- Direct
- Motivational
- Always focused on helping the user grow safely and profitably

Your mission:
Help the user build a profitable sports card and Pokemon card business.

Current user goal:
{st.session_state.growth_goal}

Current mode:
{mode}

Cletus should act like a growing business assistant, not just a chatbot.

When analyzing cards, use this format:

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

When giving business advice, include:
- Immediate next step
- Risk
- Income potential
- What Cletus would do next
"""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in st.session_state.messages[-8:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

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

st.title("🤖 Cletus AI")
st.caption("Broke Dad Trading Co. Sports Card Growth Assistant")

with st.sidebar:
    st.header("Cletus Command Center")

    mode = st.selectbox(
        "Choose Mode",
        [
            "General Chat",
            "Analyze Card",
            "Task Manager",
            "Grade Check",
            "Profit Calculator",
            "Listing Writer",
            "Inventory Assistant",
            "Deal Finder",
            "Manager Review",
            "Business Growth"
        ]
    )

    st.write("### Growth Goal")
    st.session_state.growth_goal = st.text_area(
        "What is Cletus helping you build?",
        value=st.session_state.growth_goal
    )

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    if st.button("Generate Today's Mission"):
        mission_prompt = """
Create a daily mission plan for Broke Dad Trading Co.

Focus on:
- making money
- scanning cards
- grading candidates
- listing cards
- finding deals
- creating content
- growing the business

Return 5 clear tasks with priority levels.
"""

        mission = ask_cletus("Task Manager", mission_prompt)

        st.write("### Today's Cletus Mission")
        st.write(mission)

        save_task("Generated Daily Mission", "High", "Pending", mission)
        save_scan("Task Manager", mission_prompt, mission)

        st.success("Today's mission saved to tasks.")

    st.divider()

st.subheader("What are we working on today?")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📸 Analyze a Card"):
        mode = "Analyze Card"
        st.session_state.messages.append({
            "role": "user",
            "content": "Help me analyze a card photo and decide whether to grade, sell, hold, or pass."
        })

with col2:
    if st.button("💰 Check Profit"):
        mode = "Profit Calculator"
        st.session_state.messages.append({
            "role": "user",
            "content": "Help me calculate profit and ROI on a card deal."
        })

with col3:
    if st.button("🚀 Grow Business"):
        mode = "Business Growth"
        st.session_state.messages.append({
            "role": "user",
            "content": "Give me the next best move to grow Broke Dad Trading Co."
        })

st.divider()

if mode == "Task Manager":

    st.header("📋 Cletus Task Manager")

    task = st.text_input("Task")
    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
    status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
    notes = st.text_area("Notes")

    if st.button("Save Task"):
        save_task(task, priority, status, notes)
        st.success("Task saved.")

    st.divider()
    st.subheader("Current Tasks")

    tasks = load_tasks()

    for row in tasks:
        if len(row) >= 5:
            st.write(f"""
**Task:** {row[1]}  
**Priority:** {row[2]}  
**Status:** {row[3]}  
**Notes:** {row[4]}  
---
""")

elif mode == "Profit Calculator":
    st.header("💰 Profit Calculator")

    sale_price = st.number_input("Sale Price", min_value=0.0, step=1.0)
    purchase_price = st.number_input("Purchase Price", min_value=0.0, step=1.0)
    fees = st.number_input("Platform Fees", min_value=0.0, step=1.0)
    shipping = st.number_input("Shipping Cost", min_value=0.0, step=1.0)

    if st.button("Calculate"):
        profit = sale_price - purchase_price - fees - shipping
        roi = (profit / purchase_price) * 100 if purchase_price > 0 else 0

        result = f"""
Profit: ${profit:.2f}
ROI: {roi:.1f}%

Cletus Recommendation:
{"This looks profitable." if profit > 0 else "This does not look profitable."}
"""

        st.success(result)

        st.session_state.messages.append({"role": "assistant", "content": result})
        save_scan(mode, "Profit calculation", result)

else:
    use_camera = st.toggle("Use Camera", value=False)

    camera_photo = None

    if use_camera:
        camera_photo = st.camera_input("Take a photo of your card")

    uploaded_file = st.file_uploader(
        "Or upload a card photo",
        type=["jpg", "jpeg", "png"]
    )

    image_file = camera_photo if camera_photo else uploaded_file

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    question = st.chat_input("Ask Cletus...")

    if question or image_file:
        user_text = question or "Analyze this card photo."

        st.session_state.messages.append({
            "role": "user",
            "content": user_text
        })

        with st.chat_message("user"):
            st.write(user_text)

        with st.chat_message("assistant"):
            with st.spinner("Cletus is thinking..."):
                answer = ask_cletus(mode, user_text, image_file)
                st.write(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })

        save_scan(mode, user_text, answer)
                if mode == "Analyze Card":

            task_prompt = f"""
Based on this card analysis, create 3 short actionable business tasks.

Analysis:
{answer}

Examples:
- Grade this card
- Research comps
- Create listing
- Monitor player market
- Hold for offseason

Return ONLY short task titles.
"""

            task_response = ask_cletus(
                "Task Manager",
                task_prompt
            )

            st.write("### Auto Generated Tasks")
            st.write(task_response)

            task_lines = task_response.split("\n")

            for task in task_lines:

                cleaned = task.strip("- ").strip()

                if len(cleaned) > 3:

                    save_task(
                        cleaned,
                        "Medium",
                        "Pending",
                        "Auto-generated from card analysis"
                    )

            st.success("Tasks automatically added to Task Manager.")