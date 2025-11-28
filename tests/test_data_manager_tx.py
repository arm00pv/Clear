import pytest
from data_manager import DataManager

def test_data_manager_transactions(tmp_path):
    """
    Tests persisting transactions.
    """
    d = tmp_path / "test_tx_data.json"
    DataManager.DATA_FILE = str(d)

    dm = DataManager()

    # Empty initially
    assert len(dm.get_transactions()) == 0

    # Add
    tx = {"date": "2025-01-01", "description": "Test", "amount": 10.0}
    dm.add_transaction(tx)

    # Verify
    txs = dm.get_transactions()
    assert len(txs) == 1
    assert txs[0]["description"] == "Test"

    # Reload
    dm2 = DataManager()
    txs2 = dm2.get_transactions()
    assert len(txs2) == 1
