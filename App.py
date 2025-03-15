from flask import Flask, render_template, request, jsonify
import requests
import random
import re

app = Flask(__name__)

def validate_card(number):
    number = re.sub(r'\D', '', number)
    sum = 0
    alt = False
    for i in range(len(number) - 1, -1, -1):
        n = int(number[i])
        if alt:
            n *= 2
            if n > 9:
                n -= 9
        sum += n
        alt = not alt
    return sum % 10 == 0

def get_bin_data(bin):
    url = f"https://lookup.binlist.net/{bin}"
    headers = {"Accept-Version": "3"}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Error fetching BIN data:", e)
    return None

def compute_fraud_risk(is_valid, bin_data):
    if not is_valid:
        return random.randint(80, 100)
    if bin_data and "type" in bin_data:
        return random.randint(20, 50) if bin_data["type"].lower() == "debit" else random.randint(0, 30)
    return random.randint(30, 60)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    
    if request.method == "POST":
        cards = request.form.get("cards", "").strip().split("\n")
        cards = [c.strip() for c in cards if c.strip()]
        cards = cards[:100]

        for card_input in cards:
            card_number = re.sub(r'\D', '', card_input)
            if not card_number:
                continue

            is_valid = validate_card(card_number)
            bin_data = get_bin_data(card_number[:6]) if len(card_number) >= 6 else None

            results.append({
                "input": card_input,
                "number": card_number,
                "valid": is_valid,
                "bank": bin_data["bank"]["name"] if bin_data and "bank" in bin_data else "N/A",
                "country": bin_data["country"]["name"] if bin_data and "country" in bin_data else "N/A",
                "scheme": bin_data["scheme"] if bin_data and "scheme" in bin_data else "N/A",
                "type": bin_data["type"] if bin_data and "type" in bin_data else "N/A",
                "risk": compute_fraud_risk(is_valid, bin_data)
            })

    return render_template("index.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
