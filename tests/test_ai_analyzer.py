import pytest
from ai_analyzer import SmartAnalyzer

def test_smart_analyzer_bnpl_calculation():
    """
    Tests the SmartAnalyzer BNPL calculation.
    """
    analyzer = SmartAnalyzer()
    mock_transactions = [
        {"description": "AMAZON", "amount": 50.00},
        {"description": "KLARNA* WIDGET CO", "amount": 25.00},
        {"description": "STARBUCKS", "amount": 5.50},
        {"description": "AFTERPAY* FASHION STORE", "amount": 45.00},
        {"description": "AFFIRM* GADGETS INC", "amount": 150.00},
    ]

    analysis = analyzer.analyze_transactions(mock_transactions)
    assert analysis["total_bnpl"] == "220.00"
    assert analysis["category_breakdown"]["BNPL"] == 220.00
    assert analysis["category_breakdown"]["Food & Drink"] == 5.50
    # "AFTERPAY* FASHION STORE" matches "FASHION" in Shopping, so 50 (Amazon) + 45 (Afterpay) = 95
    assert analysis["category_breakdown"]["Shopping"] == 95.00

def test_smart_analyzer_insights():
    """
    Tests that insights are generated.
    """
    analyzer = SmartAnalyzer()
    mock_transactions = [
        {"description": "AFFIRM* GADGETS INC", "amount": 150.00}, # > 100
        {"description": "STARBUCKS", "amount": 5.00},
        {"description": "STARBUCKS", "amount": 5.00},
        {"description": "STARBUCKS", "amount": 5.00},
        {"description": "STARBUCKS", "amount": 5.00}, # > 3 coffee
    ]

    analysis = analyzer.analyze_transactions(mock_transactions)
    insights = analysis["insights"]

    assert any("High BNPL usage detected" in i for i in insights)
    assert any("loyalty card" in i for i in insights)
