import pytest
from app import calculate_bnpl_total_from_yodlee

def test_calculate_bnpl_total_with_mixed_transactions(monkeypatch):
    """
    Tests the BNPL calculation with a mix of BNPL and non-BNPL transactions.
    """
    mock_transactions = [
        {"description": "AMAZON", "amount": 50.00},
        {"description": "KLARNA* WIDGET CO", "amount": 25.00},
        {"description": "STARBUCKS", "amount": 5.50},
        {"description": "AFTERPAY* FASHION STORE", "amount": 45.00},
        {"description": "AFFIRM* GADGETS INC", "amount": 150.00},
    ]

    # Mock the yodlee_client.get_transactions method
    monkeypatch.setattr("app.yodlee_client.get_transactions", lambda user_id: mock_transactions)

    # Call the function and assert the result
    assert calculate_bnpl_total_from_yodlee("test_user") == "220.00"

def test_calculate_bnpl_total_with_no_bnpl_transactions(monkeypatch):
    """
    Tests the BNPL calculation with no BNPL transactions.
    """
    mock_transactions = [
        {"description": "AMAZON", "amount": 50.00},
        {"description": "STARBUCKS", "amount": 5.50},
        {"description": "UBER", "amount": 15.75},
    ]

    monkeypatch.setattr("app.yodlee_client.get_transactions", lambda user_id: mock_transactions)

    assert calculate_bnpl_total_from_yodlee("test_user") == "0.00"

def test_calculate_bnpl_total_with_empty_transactions(monkeypatch):
    """
    Tests the BNPL calculation with an empty list of transactions.
    """
    mock_transactions = []

    monkeypatch.setattr("app.yodlee_client.get_transactions", lambda user_id: mock_transactions)

    assert calculate_bnpl_total_from_yodlee("test_user") == "0.00"

def test_calculate_bnpl_total_with_malformed_transactions(monkeypatch):
    """
    Tests the BNPL calculation with transactions that have missing fields.
    """
    mock_transactions = [
        {"description": "KLARNA* WIDGET CO"},  # Missing amount
        {"amount": 45.00},  # Missing description
        {"description": "AFFIRM* GADGETS INC", "amount": 150.00},
    ]

    monkeypatch.setattr("app.yodlee_client.get_transactions", lambda user_id: mock_transactions)

    assert calculate_bnpl_total_from_yodlee("test_user") == "150.00"
