import json
import os

class DataManager:
    """
    Handles persistence of user data (budgets, goals) to a local JSON file.
    """
    DATA_FILE = "data/user_data.json"

    DEFAULT_BUDGET = {
        "Food & Drink": 150,
        "Transportation": 100,
        "Shopping": 100,
        "Entertainment": 50,
        "Utilities": 100,
        "BNPL": 50,
    }

    def __init__(self):
        self._ensure_data_file()

    def _ensure_data_file(self):
        """
        Creates the data file with default values if it doesn't exist.
        """
        if not os.path.exists(self.DATA_FILE):
            default_data = {
                "budget": self.DEFAULT_BUDGET,
                "goals": [],
                "transactions": [],
                "recurring_bills": [],
                "xp": 0
            }
            self._save_data(default_data)

    def _load_data(self):
        """
        Loads data from the JSON file.
        """
        try:
            with open(self.DATA_FILE, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"budget": self.DEFAULT_BUDGET, "goals": [], "transactions": [], "recurring_bills": [], "xp": 0}

    def _save_data(self, data):
        """
        Saves data to the JSON file.
        """
        with open(self.DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    def get_budget(self):
        data = self._load_data()
        # Merge with default to ensure all keys exist if schema changes
        budget = self.DEFAULT_BUDGET.copy()
        budget.update(data.get("budget", {}))
        return budget

    def update_budget(self, new_budget):
        data = self._load_data()
        data["budget"] = new_budget
        self._save_data(data)

    def get_goals(self):
        data = self._load_data()
        return data.get("goals", [])

    def add_goal(self, goal):
        data = self._load_data()
        goals = data.get("goals", [])
        goal['id'] = len(goals) + 1 # Simple auto-increment
        goals.append(goal)
        data["goals"] = goals
        self._save_data(data)

    def update_goal(self, goal_id, amount_added):
        data = self._load_data()
        goals = data.get("goals", [])
        for goal in goals:
            if goal['id'] == goal_id:
                goal['current'] += amount_added
                break
        data["goals"] = goals
        self._save_data(data)

    def get_transactions(self):
        data = self._load_data()
        return data.get("transactions", [])

    def add_transaction(self, transaction):
        data = self._load_data()
        transactions = data.get("transactions", [])
        transactions.append(transaction)
        data["transactions"] = transactions
        self._save_data(data)

    def get_bills(self):
        data = self._load_data()
        return data.get("recurring_bills", [])

    def add_bill(self, bill):
        data = self._load_data()
        bills = data.get("recurring_bills", [])
        bill['id'] = len(bills) + 1
        bills.append(bill)
        data["recurring_bills"] = bills
        self._save_data(data)

    def delete_bill(self, bill_id):
        data = self._load_data()
        bills = data.get("recurring_bills", [])
        bills = [b for b in bills if b['id'] != bill_id]
        data["recurring_bills"] = bills
        self._save_data(data)

    def get_xp(self):
        data = self._load_data()
        return data.get("xp", 0)

    def add_xp(self, points):
        data = self._load_data()
        current = data.get("xp", 0)
        data["xp"] = current + points
        self._save_data(data)

    def get_all_data(self):
        return self._load_data()

    def replace_all_data(self, new_data):
        # Validate schema basics
        if isinstance(new_data, dict):
            self._save_data(new_data)
