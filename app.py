import os
import csv
import io
from flask import Flask, render_template, redirect, url_for, Response, request, jsonify
from flask_cors import CORS
from yodlee_client import YodleeClient
from ai_analyzer import SmartAnalyzer
from data_manager import DataManager

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
data_manager = DataManager()
# ---

@app.route('/')
def index():
    """
    Renders the main page with the total BNPL spending.
    """
    bnpl_total = "0.00"
    analysis = {}
    user_budget = data_manager.get_budget()
    user_goals = data_manager.get_goals()
    user_xp = data_manager.get_xp()

    if ACCOUNT_LINKED:
        import datetime
        today = datetime.date.today().isoformat()

        # Check challenges
        challenges_data = data_manager.get_challenges_data()
        if challenges_data["date"] != today:
            new_challenges = smart_analyzer.generate_daily_challenges()
            data_manager.set_challenges(today, new_challenges)
            active_challenges = new_challenges
        else:
            active_challenges = challenges_data["active"]

        # In a real app, the user_id would come from the session
        yodlee_transactions = yodlee_client.get_transactions(user_id="test_user")
        manual_transactions = data_manager.get_transactions()
        manual_bills = data_manager.get_bills()

        # Merge transactions
        all_transactions = yodlee_transactions + manual_transactions

        # Sort by date (descending for display, or ascending for analysis?)
        # Let's sort descending so recent are top
        # Need to handle date types (string vs object)
        def parse_date(tx):
            d = tx.get("date")
            if isinstance(d, str):
                try:
                    return datetime.date.fromisoformat(d)
                except ValueError:
                    return datetime.date.min
            return d or datetime.date.min

        all_transactions.sort(key=parse_date, reverse=True)

        # Pass current_xp to analysis if you want to use it for display or logic
        analysis = smart_analyzer.analyze_transactions(all_transactions, budget_limits=user_budget, manual_bills=manual_bills, current_xp=user_xp, active_challenges=active_challenges)
        bnpl_total = analysis.get("total_bnpl", "0.00")

    return render_template('index.html',
                           bnpl_total=bnpl_total,
                           account_linked=ACCOUNT_LINKED,
                           analysis=analysis,
                           user_budget=user_budget,
                           user_goals=user_goals)

@app.route('/add-goal', methods=['POST'])
def add_goal():
    """
    Adds a new savings goal.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    name = request.form.get('name')
    try:
        target = float(request.form.get('target', 0))
    except ValueError:
        target = 0

    if name and target > 0:
        data_manager.add_goal({
            'name': name,
            'target': target,
            'current': 0.0
        })
        data_manager.add_xp(20) # Award XP

    return redirect(url_for('index'))

@app.route('/contribute-goal/<int:goal_id>', methods=['POST'])
def contribute_goal(goal_id):
    """
    Simulates adding funds to a goal.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    try:
        amount = float(request.form.get('amount', 0))
        data_manager.update_goal(goal_id, amount)
    except ValueError:
        pass

    return redirect(url_for('index'))

@app.route('/update-budget', methods=['POST'])
def update_budget():
    """
    Updates the user's budget limits.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    current_budget = data_manager.get_budget()
    for category in current_budget:
        if category in request.form:
            try:
                current_budget[category] = float(request.form[category])
            except ValueError:
                pass # Ignore invalid input

    data_manager.update_budget(current_budget)
    data_manager.add_xp(5) # Award XP

    return redirect(url_for('index'))

@app.route('/auto-budget', methods=['POST'])
def auto_budget():
    """
    Automatically sets the budget based on AI recommendations.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    # Fetch all transactions to analyze
    yodlee_transactions = yodlee_client.get_transactions(user_id="test_user")
    manual_transactions = data_manager.get_transactions()
    all_transactions = yodlee_transactions + manual_transactions

    recommended = smart_analyzer.calculate_recommended_budget(all_transactions)

    data_manager.update_budget(recommended)
    data_manager.add_xp(25) # Award XP for using AI tools

    return redirect(url_for('index'))

@app.route('/add-transaction', methods=['POST'])
def add_transaction():
    """
    Adds a manual transaction.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    date = request.form.get('date')
    description = request.form.get('description')
    amount = request.form.get('amount')
    category = request.form.get('category')

    if date and description and amount and category:
        try:
            amount = float(amount)
            # Add transaction
            data_manager.add_transaction({
                "date": date,
                "description": description,
                "amount": amount,
                "category": category # Optional: If we want to override auto-cat
            })
            data_manager.add_xp(10) # Award XP
        except ValueError:
            pass

    return redirect(url_for('index'))

@app.route('/add-bill', methods=['POST'])
def add_bill():
    """
    Adds a recurring bill.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    name = request.form.get('name')
    amount = request.form.get('amount')
    due_date = request.form.get('due_date')

    if name and amount and due_date:
        try:
            amount = float(amount)
            data_manager.add_bill({
                "name": name,
                "amount": amount,
                "due_date": due_date
            })
            data_manager.add_xp(15) # Award XP
        except ValueError:
            pass

    return redirect(url_for('index'))

@app.route('/delete-bill/<int:bill_id>', methods=['POST'])
def delete_bill(bill_id):
    """
    Deletes a recurring bill.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    data_manager.delete_bill(bill_id)
    return redirect(url_for('index'))

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handles chat queries from the AI Assistant.
    """
    if not ACCOUNT_LINKED:
        return jsonify({"response": "Please link your account first."})

    data = request.get_json()
    query = data.get("query", "")

    user_budget = data_manager.get_budget()

    # Analyze data fresh to answer questions
    transactions = yodlee_client.get_transactions(user_id="test_user")
    analysis = smart_analyzer.analyze_transactions(transactions, budget_limits=user_budget)

    response = smart_analyzer.get_chat_response(query, analysis)

    return jsonify({"response": response})

@app.route('/claim-challenge/<challenge_id>', methods=['POST'])
def claim_challenge(challenge_id):
    """
    Claims reward for a completed challenge.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    data_manager.mark_challenge_complete(challenge_id)
    # Get challenge reward (simplification: assume 50 XP if not easily retrievable without lookup)
    # Ideally we look up the challenge details.
    # For now, let's just award a flat XP amount or try to find it.
    challenges = data_manager.get_challenges_data().get("active", [])
    reward = 0
    for ch in challenges:
        if ch.get("uid") == challenge_id and ch.get("completed"):
            reward = ch.get("reward", 50)
            break

    if reward > 0:
        data_manager.add_xp(reward)

    return redirect(url_for('index'))

@app.route('/backup-data')
def backup_data():
    """
    Exports all user data as a JSON file.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    data = data_manager.get_all_data()
    return Response(
        json.dumps(data, indent=4),
        mimetype="application/json",
        headers={"Content-disposition": "attachment; filename=bnpl_tracker_backup.json"}
    )

@app.route('/restore-data', methods=['POST'])
def restore_data():
    """
    Restores user data from a JSON file.
    """
    if not ACCOUNT_LINKED:
        return redirect(url_for('index'))

    if 'backup_file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['backup_file']
    if file.filename == '':
        return redirect(url_for('index'))

    if file:
        try:
            content = file.read()
            data = json.loads(content)
            data_manager.replace_all_data(data)
        except Exception:
            pass # Handle error gracefully

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
