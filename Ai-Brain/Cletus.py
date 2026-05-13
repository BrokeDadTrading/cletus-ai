from openai import OpenAI
import csv
import os

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

INVENTORY_FILE = "Inventory/cards.csv"

system_prompt = """
You are Cletus, the AI assistant for BrokeDad-Cletus.

You help grow a sports card and Pokemon business.

Your jobs:
- Analyze cards
- Estimate card values
- Help decide grading
- Calculate profit
- Create listing titles
- Recommend buy/sell/hold
- Help manage inventory
"""

def add_card():
    card_name = input("Card name: ")
    category = input("Category Sports/Pokemon: ")
    purchase_price = input("Purchase price: ")
    estimated_value = input("Estimated value: ")
    grade = input("Grade/Raw: ")
    platform = input("Platform bought from: ")
    status = input("Status Hold/Sell/Grade: ")
    notes = input("Notes: ")

    with open(INVENTORY_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            card_name,
            category,
            purchase_price,
            estimated_value,
            grade,
            platform,
            status,
            notes
        ])

    print("\nCletus: Card added to inventory.")

def show_inventory():
    if not os.path.exists(INVENTORY_FILE):
        print("Cletus: No inventory file found.")
        return

    with open(INVENTORY_FILE, "r") as file:
        reader = csv.reader(file)
        for row in reader:
            print(row)

while True:
    question = input("\nYou: ")

    if question.lower() == "add card":
        add_card()

    elif question.lower() == "show inventory":
        show_inventory()

    else:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ]
        )

        print("\nCletus:", response.choices[0].message.content)
