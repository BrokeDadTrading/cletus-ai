import streamlit as st
from openai import OpenAI
import base64

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Cletus - Broke Dad Trading Co.")
st.write("Sports Card AI Assistant")

question = st.text_input("Ask Cletus")
uploaded_file = st.file_uploader("Upload a card photo", type=["jpg", "jpeg", "png"])

if st.button("Ask Cletus"):
    messages = [
        {
            "role": "system",
            "content": "You are Cletus, an AI assistant for sports cards and Pokemon cards. Analyze cards, estimate value, grading potential, fake risk, and selling advice."
        }
    ]

    if uploaded_file:
        image_bytes = uploaded_file.getvalue()
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