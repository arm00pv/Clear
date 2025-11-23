import os
import csv
import io
from flask import Flask, render_template, redirect, url_for, Response, request
from flask_cors import CORS
from yodlee_client import YodleeClient
from ai_analyzer import SmartAnalyzer

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# --- Mock Yodlee Integration ---
# In a real app, this would be stored in a session or database
ACCOUNT_LINKED = False
# In a real app, these would come from a secure config
YODLEE_API_KEY = "your_api_key"
YODLEE_SECRET = "your_secret"
yodlee_client = YodleeClient(YODLEE_API_KEY, YODLEE_SECRET)
smart_analyzer = SmartAnalyzer()

# Mock Storage for User Budget
USER_BUDGET = {
    "Food & Drink": 150,
    "Transportation": 100,
    "Shopping": 100,
    "Entertainment": 50,
    "Utilities": 100,
    "BNPL": 50,
}
# ---

@app.route('/')
def index():
    """
    Renders the main page with the total BNPL spending.
    """
    bnpl_total = "0.00"
    analysis = {}

    if ACCOUNT_LINKED:
        # In a real app, the user_id would come from the session
        transactions = yodlee_client.get_transactions(user_id="test_user")
        analysis = smart_analyzer.analyze_transactions(transactions, budget_limits=USER_BUDGET)
        bnpl_total = analysis.get("total_bnpl", "0.00")

    return render_template('index.html', bnpl_total=bnpl_total, account_linked=ACCOUNT_LINKED, analysis=analysis, user_budget=USER_BUDGET)

@app.route('/update-budget', methods=['POST'])
def update_budget():
    """
    Updates the user's budget limits.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    for category in USER_BUDGET:
        if category in request.form:
            try:
                USER_BUDGET[category] = float(request.form[category])
            except ValueError:
                pass # Ignore invalid input

    return redirect(url_for('index'))

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

@app.route('/download-report')
def download_report():
    """
    Generates and downloads a CSV report of the transactions.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    transactions = yodlee_client.get_transactions(user_id="test_user")

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(["Date", "Description", "Amount"])

    # Rows
    for tx in transactions:
        writer.writerow([tx.get("date"), tx.get("description"), tx.get("amount")])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=transactions_report.csv"}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
