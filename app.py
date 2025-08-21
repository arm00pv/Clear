import csv
import os
from flask import Flask, render_template

app = Flask(__name__)

# Define BNPL keywords
BNPL_KEYWORDS = ["KLARNA", "AFTERPAY", "AFFIRM"]

def get_bnpl_total():
    """
    Reads transactions from a CSV file, identifies BNPL transactions,
    and calculates the total spending.
    """
    total = 0.0
    # Correctly locate the CSV file in the 'data' directory
    csv_file_path = os.path.join(os.path.dirname(__file__), 'data', 'transactions.csv')

    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                description = row.get("Description", "").upper()
                amount_str = row.get("Amount")
                if amount_str:
                    try:
                        amount = float(amount_str)
                        if any(keyword in description for keyword in BNPL_KEYWORDS):
                            total += amount
                    except (ValueError, TypeError):
                        # Handle cases where Amount is not a valid number
                        pass
    except FileNotFoundError:
        # Handle case where the CSV file does not exist
        return 0.0

    return f"{total:.2f}"

@app.route('/')
def index():
    """
    Renders the main page with the total BNPL spending.
    """
    bnpl_total = get_bnpl_total()
    return render_template('index.html', bnpl_total=bnpl_total)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
