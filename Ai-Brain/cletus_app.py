import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("Cletus - Broke Dad Trading Co.")
st.write("Sports Card AI Assistant")

question = st.text_input("Talk to Cletus")

if st.button("Ask Cletus"):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are Cletus, an AI sports card assistant."
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    answer = response.choices[0].message.content

    st.write("### Cletus Says:")
    st.write(answer)