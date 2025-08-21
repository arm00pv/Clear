import os
from flask import Flask, render_template, redirect, url_for
from yodlee_client import YodleeClient

app = Flask(__name__)

# --- Mock Yodlee Integration ---
# In a real app, this would be stored in a session or database
ACCOUNT_LINKED = False
# In a real app, these would come from a secure config
YODLEE_API_KEY = "your_api_key"
YODLEE_SECRET = "your_secret"
yodlee_client = YodleeClient(YODLEE_API_KEY, YODLEE_SECRET)
# ---

# Define BNPL keywords
BNPL_KEYWORDS = ["KLARNA", "AFTERPAY", "AFFIRM"]

def calculate_bnpl_total_from_yodlee(user_id):
    """
    Fetches transactions from the Yodlee client and calculates the total BNPL spending.
    """
    total = 0.0
    transactions = yodlee_client.get_transactions(user_id)
    for transaction in transactions:
        description = transaction.get("description", "").upper()
        amount = transaction.get("amount", 0.0)
        if any(keyword in description for keyword in BNPL_KEYWORDS):
            total += amount
    return f"{total:.2f}"

@app.route('/')
def index():
    """
    Renders the main page with the total BNPL spending.
    """
    bnpl_total = "0.00"
    if ACCOUNT_LINKED:
        # In a real app, the user_id would come from the session
        bnpl_total = calculate_bnpl_total_from_yodlee(user_id="test_user")

    return render_template('index.html', bnpl_total=bnpl_total, account_linked=ACCOUNT_LINKED)

@app.route('/link-account', methods=['POST'])
def link_account():
    """
    Renders the page to simulate linking a bank account.
    """
    return render_template('link_account.html')

@app.route('/authorize-account', methods=['POST'])
def authorize_account():
    """
    Simulates the successful authorization of a bank account.
    """
    global ACCOUNT_LINKED
    ACCOUNT_LINKED = True
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
