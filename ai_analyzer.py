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

        # Detect Subscriptions
        subscriptions = self._detect_subscriptions(enriched_transactions)

        # Calculate Health Score
        total_spending = sum(category_breakdown.values())
        health_score = self._calculate_health_score(total_bnpl, total_spending)

        # Project Monthly Spending
        projected_spending = self._calculate_spending_projection(transactions, total_spending)

        # Generate Upcoming Installments (Mock)
        upcoming_installments = self._generate_upcoming_installments(enriched_transactions)

        # Generate Insights
        insights = self._generate_insights(category_breakdown, spending_habits, total_bnpl)

        return {
            "total_bnpl": f"{total_bnpl:.2f}",
            "category_breakdown": category_breakdown,
            "insights": insights,
            "bnpl_providers": bnpl_providers,
            "recent_transactions": enriched_transactions,
            "subscriptions": subscriptions,
            "health_score": health_score,
            "projected_spending": f"{projected_spending:.2f}",
            "upcoming_installments": upcoming_installments
        }

    def _generate_upcoming_installments(self, transactions):
        """
        Generates mock upcoming installments for BNPL transactions.
        Assumes a standard 'Pay in 4' model where 3 future payments remain.
        """
        installments = []
        import datetime

        for tx in transactions:
            if tx["category"] == "BNPL":
                # Create 3 future dates
                try:
                    current_date = tx["date"]
                    if current_date is None:
                        # Fallback for tests or missing dates: use today
                        current_date = datetime.date.today()

                    if isinstance(current_date, str):
                        current_date = datetime.date.fromisoformat(current_date)

                    amount = float(tx["amount"])

                    # Generate 3 payments
                    for i in range(1, 4):
                        due_date = current_date + datetime.timedelta(weeks=2*i)
                        installments.append({
                            "description": f"Installment {i+1} of 4: {tx['description']}",
                            "amount": f"{amount:.2f}",
                            "due_date": due_date.isoformat()
                        })
                except ValueError:
                    continue

        # Sort by date
        installments.sort(key=lambda x: x["due_date"])
        return installments

    def _calculate_spending_projection(self, transactions, total_spending):
        """
        Calculates a projection for total monthly spending based on current average daily spending.
        """
        if not transactions:
            return 0.0

        # Ensure dates are comparable (handle strings if necessary, though yodlee_client uses date objects)
        # The mocked test might pass strings, so let's handle that or rely on the input being correct.
        # In test_subscription_detection, the dates are strings "2023-01-01".
        # In yodlee_client, they are datetime.date objects.
        # We should convert to date objects if they are strings.
        import datetime

        dates = []
        for t in transactions:
            d = t.get("date")
            if isinstance(d, str):
                try:
                    d = datetime.date.fromisoformat(d)
                except ValueError:
                    continue # Skip invalid dates
            if d:
                dates.append(d)

        if not dates:
            return total_spending # Fallback

        min_date = min(dates)
        max_date = max(dates)
        days_diff = (max_date - min_date).days + 1

        if days_diff <= 0:
            days_diff = 1

        daily_average = total_spending / days_diff

        # Simple projection: 30 * average daily spend
        return daily_average * 30

    def _detect_subscriptions(self, transactions):
        """
        Identifies potential recurring subscriptions.
        """
        subs = []
        # In a real app, we'd look for recurring dates/amounts.
        # Here we use known keywords.
        keywords = ["NETFLIX", "SPOTIFY", "HULU", "DISNEY+", "APPLE", "AMAZON PRIME", "YOUTUBE"]

        seen = set()
        for tx in transactions:
            desc = tx["description"].upper()
            if any(k in desc for k in keywords):
                # Avoid duplicates for this simple list
                if desc not in seen:
                    subs.append({
                        "name": tx["description"],
                        "amount": tx["amount"],
                        "date": tx["date"] # Last payment date
                    })
                    seen.add(desc)
        return subs

    def _calculate_health_score(self, total_bnpl, total_spending):
        """
        Calculates a financial health score (0-100).
        """
        if total_spending == 0:
            return 100

        # Base score
        score = 100

        # Deduct based on BNPL ratio
        bnpl_ratio = total_bnpl / total_spending
        if bnpl_ratio > 0.5:
            score -= 40
        elif bnpl_ratio > 0.3:
            score -= 20
        elif bnpl_ratio > 0.1:
            score -= 10

        # Deduct absolute BNPL amount penalties
        if total_bnpl > 200:
            score -= 10
        if total_bnpl > 500:
            score -= 20

        return max(0, score)

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
