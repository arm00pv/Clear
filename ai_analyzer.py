import random

class SmartAnalyzer:
    """
    A simulated AI-powered analyzer for financial transactions.
    It uses pattern recognition and heuristic rules to categorize spending and generate insights,
    mimicking the behavior of an intelligent financial assistant.
    """

    CATEGORIES = {
        "Food & Drink": ["STARBUCKS", "MCDONALDS", "UBER EATS", "DOORDASH", "RESTAURANT", "CAFE"],
        "Transportation": ["UBER", "LYFT", "GAS", "SHELL", "EXXON", "TRAIN", "BUS"],
        "Shopping": ["AMAZON", "TARGET", "WALMART", "BEST BUY", "CLOTHING", "FASHION"],
        "BNPL": ["KLARNA", "AFTERPAY", "AFFIRM", "SEZZLE", "PAYPAL PAY IN 4"],
        "Entertainment": ["NETFLIX", "SPOTIFY", "CINEMA", "MOVIE", "HULU"],
        "Utilities": ["ELECTRIC", "WATER", "GAS", "INTERNET", "PHONE"],
    }

    def analyze_transactions(self, transactions):
        """
        Analyzes a list of transactions to produce a comprehensive financial report.

        Args:
            transactions (list): A list of transaction dictionaries.

        Returns:
            dict: A dictionary containing:
                - total_bnpl (str): Total amount spent on BNPL services.
                - category_breakdown (dict): Total spending per category.
                - insights (list): A list of AI-generated insights/tips.
                - bnpl_providers (dict): Breakdown of spending by BNPL provider.
                - recent_transactions (list): The list of transactions, potentially enriched.
        """
        total_bnpl = 0.0
        category_breakdown = {cat: 0.0 for cat in self.CATEGORIES}
        category_breakdown["Uncategorized"] = 0.0
        bnpl_providers = {}

        spending_habits = []
        enriched_transactions = []

        for transaction in transactions:
            description = transaction.get("description", "").upper()
            amount = transaction.get("amount", 0.0)

            categorized = False
            tx_category = "Uncategorized"

            # Check for BNPL specifically first
            bnpl_match = False
            for keyword in self.CATEGORIES["BNPL"]:
                if keyword in description:
                    total_bnpl += amount
                    category_breakdown["BNPL"] += amount
                    categorized = True
                    bnpl_match = True
                    tx_category = "BNPL"

                    # Track provider
                    provider_name = keyword.title()
                    if provider_name not in bnpl_providers:
                        bnpl_providers[provider_name] = 0.0
                    bnpl_providers[provider_name] += amount
                    break

            # Check other categories
            found_category = False
            for category, keywords in self.CATEGORIES.items():
                if category == "BNPL": continue # Already handled

                if any(keyword in description for keyword in keywords):
                    category_breakdown[category] += amount
                    found_category = True
                    if not bnpl_match:
                        tx_category = category

                    # Track specific habits
                    if category == "Food & Drink" and amount < 20:
                        spending_habits.append("Coffee/Snack")

            if not found_category and not categorized:
                category_breakdown["Uncategorized"] += amount

            # Enriched transaction object
            enriched_transactions.append({
                "date": transaction.get("date"),
                "description": transaction.get("description"),
                "amount": f"{amount:.2f}",
                "category": tx_category
            })

        # Generate Insights
        insights = self._generate_insights(category_breakdown, spending_habits, total_bnpl)

        return {
            "total_bnpl": f"{total_bnpl:.2f}",
            "category_breakdown": category_breakdown,
            "insights": insights,
            "bnpl_providers": bnpl_providers,
            "recent_transactions": enriched_transactions
        }

    def _generate_insights(self, breakdown, habits, total_bnpl):
        """
        Generates "AI" insights based on the analysis.
        """
        insights = []

        # BNPL Insights
        if total_bnpl > 100:
            insights.append("⚠️ High BNPL usage detected. Consider paying off existing installments before adding new ones.")
        elif total_bnpl > 0:
            insights.append("ℹ️ You have active Buy Now Pay Later commitments. Keep track of your due dates.")
        else:
            insights.append("✅ Great job! No BNPL debt detected.")

        # Category Insights
        if breakdown["Food & Drink"] > 150:
            insights.append("💡 AI Tip: You're spending a lot on dining out. Cooking at home could save you money.")

        if breakdown["Shopping"] > 200:
             insights.append("🛒 It looks like you've been doing a lot of shopping recently. Make sure to stick to your budget.")

        # Pattern recognition mock
        coffee_count = habits.count("Coffee/Snack")
        if coffee_count > 3:
             insights.append(f"☕ You've bought coffee/snacks {coffee_count} times recently. A loyalty card might save you money!")

        # Random "Smart" tip if few insights
        if len(insights) < 2:
            tips = [
                "💰 Rule of thumb: Save at least 20% of your income.",
                "📉 Review your subscriptions monthly to cancel unused services.",
                "🛡️ Build an emergency fund covering 3-6 months of expenses."
            ]
            insights.append(random.choice(tips))

        return insights
