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

    def analyze_transactions(self, transactions, budget_limits=None):
        """
        Analyzes a list of transactions to produce a comprehensive financial report.

        Args:
            transactions (list): A list of transaction dictionaries.
            budget_limits (dict, optional): Custom budget limits per category.

        Returns:
            dict: A dictionary containing:
                - total_bnpl (str): Total amount spent on BNPL services.
                - category_breakdown (dict): Total spending per category.
                - insights (list): A list of AI-generated insights/tips.
                - bnpl_providers (dict): Breakdown of spending by BNPL provider.
                - recent_transactions (list): The list of transactions, potentially enriched.
                - payoff_plan (dict): Debt payoff calculations and recommendations.
                - calendar_events (list): Merged list of upcoming installments and payments.
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

        # Detect Anomalies
        anomalies = self._detect_anomalies(enriched_transactions, total_spending)

        # Calculate Savings Potential (Round-ups)
        savings_potential = self._calculate_savings_potential(enriched_transactions)

        # Analyze Budget (Comparison)
        budget_analysis = self._analyze_budget(category_breakdown, budget_limits)

        # Generate Payoff Plan
        bnpl_limit = 50 # Default
        if budget_limits and "BNPL" in budget_limits:
            bnpl_limit = budget_limits["BNPL"]
        payoff_plan = self._generate_payoff_plan(total_bnpl, bnpl_limit)

        # Generate Calendar Events
        calendar_events = self._get_calendar_events(upcoming_installments, subscriptions)

        # Generate Peer Comparison
        peer_comparison = self._generate_peer_comparison(category_breakdown)

        # Generate Achievements
        achievements = self._generate_achievements(health_score, total_bnpl, budget_analysis)

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
            "upcoming_installments": upcoming_installments,
            "anomalies": anomalies,
            "savings_potential": f"{savings_potential:.2f}",
            "budget_analysis": budget_analysis,
            "achievements": achievements,
            "peer_comparison": peer_comparison,
            "payoff_plan": payoff_plan,
            "calendar_events": calendar_events
        }

    def _generate_payoff_plan(self, total_debt, monthly_budget):
        """
        Calculates a simple debt payoff plan.
        """
        if total_debt <= 0:
            return {"months": 0, "recommendation": "You are debt free!"}

        if monthly_budget <= 0:
            return {"months": "∞", "recommendation": "Please allocate a budget for BNPL payments to clear debt."}

        import math
        # Ensure total_debt and monthly_budget are floats
        total_debt = float(total_debt)
        monthly_budget = float(monthly_budget)

        months = math.ceil(total_debt / monthly_budget)

        return {
            "months": months,
            "recommendation": f"Paying ${monthly_budget:.2f}/month will clear your debt in {months} months."
        }

    def _get_calendar_events(self, installments, subscriptions):
        """
        Merges and sorts upcoming financial events.
        """
        events = []

        # Add Installments
        for inst in installments:
            events.append({
                "date": inst["due_date"],
                "title": inst["description"].split(":")[0], # Short title
                "amount": inst["amount"],
                "type": "installment"
            })

        # Add Subscriptions (Future projections - simplify to 'next month same day')
        # Note: Subscriptions currently have 'last paid date'. We project next date.
        import datetime
        today = datetime.date.today()

        for sub in subscriptions:
            # Project next payment
            # Simplified: just assume it's monthly and due day matches
            try:
                last_date_str = sub["date"]
                if isinstance(last_date_str, str):
                    last_date = datetime.date.fromisoformat(last_date_str)
                else:
                    last_date = last_date_str

                # If last date is in past, project to next occurence relative to today
                # For this mock, let's just say it's due on the same day next month
                # Handle edge case of day > 28
                day = min(last_date.day, 28)
                next_date = today.replace(day=day)
                if next_date < today:
                    # Move to next month
                    if next_date.month == 12:
                        next_date = next_date.replace(year=next_date.year+1, month=1)
                    else:
                        next_date = next_date.replace(month=next_date.month+1)

                events.append({
                    "date": next_date.isoformat(),
                    "title": sub["name"],
                    "amount": sub["amount"],
                    "type": "subscription"
                })
            except Exception:
                continue

        # Sort by date
        events.sort(key=lambda x: x["date"])
        return events

    def _generate_achievements(self, health_score, total_bnpl, budget_analysis):
        """
        Generates gamified achievements based on financial health.
        """
        achievements = []

        # Health Score Achievements
        if health_score >= 80:
            achievements.append({
                "icon": "🏆",
                "title": "Financial Guru",
                "description": "Achieved a Health Score of 80+"
            })
        elif health_score >= 60:
             achievements.append({
                "icon": "⭐",
                "title": "On the Right Track",
                "description": "Achieved a Health Score of 60+"
            })

        # BNPL Achievements
        if total_bnpl == 0:
            achievements.append({
                "icon": "🛡️",
                "title": "Debt Free",
                "description": "No BNPL usage detected!"
            })
        elif total_bnpl < 100:
             achievements.append({
                "icon": "⚖️",
                "title": "Balanced Spender",
                "description": "Kept BNPL spending under $100"
            })

        # Budget Achievements
        # Check if all budgets are 'good'
        all_good = all(item["status"] == "good" for item in budget_analysis)
        if all_good:
             achievements.append({
                "icon": "🎯",
                "title": "Budget Master",
                "description": "Stayed within budget for all categories"
            })

        return achievements

    def _detect_anomalies(self, transactions, total_spending):
        """
        Detects unusually high transactions (e.g. > 20% of total spending or > $150).
        """
        anomalies = []
        if not transactions:
            return anomalies

        threshold = max(150, total_spending * 0.2)

        for tx in transactions:
            try:
                amount = float(tx["amount"])
                if amount > threshold:
                    anomalies.append(tx)
            except ValueError:
                continue
        return anomalies

    def _calculate_savings_potential(self, transactions):
        """
        Calculates potential savings if rounding up each transaction to the nearest dollar.
        """
        import math
        savings = 0.0
        for tx in transactions:
            try:
                amount = float(tx["amount"])
                ceiling = math.ceil(amount)
                diff = ceiling - amount
                if diff > 0:
                    savings += diff
            except ValueError:
                continue
        return savings

    def _analyze_budget(self, breakdown, custom_limits=None):
        """
        Compares actual spending against a budget.
        """
        # Default Budget
        limits = {
            "Food & Drink": 150,
            "Transportation": 100,
            "Shopping": 100,
            "Entertainment": 50,
            "Utilities": 100,
            "BNPL": 50,
            "Uncategorized": 50
        }

        # Override with custom limits if provided
        if custom_limits:
            limits.update(custom_limits)

        analysis = []
        for category, amount in breakdown.items():
            limit = limits.get(category, 100)
            percent = (amount / limit) * 100 if limit > 0 else 100
            status = "good"
            if percent > 100:
                status = "danger"
            elif percent > 80:
                status = "warning"

            analysis.append({
                "category": category,
                "amount": amount,
                "limit": limit,
                "percent": min(percent, 100), # Cap for bar width
                "status": status
            })
        return analysis

    def _generate_peer_comparison(self, breakdown):
        """
        Generates insights comparing user spending to 'Peer' data.
        """
        # Mock Peer Data (Average spending per category)
        peer_averages = {
            "Food & Drink": 200,
            "Shopping": 150,
            "Transportation": 120,
            "Entertainment": 60,
            "BNPL": 80
        }

        comparison = []
        for cat, avg in peer_averages.items():
            user_spend = breakdown.get(cat, 0)
            # Fix division by zero if avg is 0 (though unlikely with mock data)
            if user_spend > 0 and avg > 0:
                diff_percent = ((user_spend - avg) / avg) * 100
                if diff_percent > 20:
                    comparison.append(f"You spend {int(diff_percent)}% more on {cat} than average.")
                elif diff_percent < -20:
                    comparison.append(f"You spend {abs(int(diff_percent))}% less on {cat} than average. Great job!")

        return comparison

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
