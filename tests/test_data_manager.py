import pytest
import os
import json
from data_manager import DataManager

def test_data_manager_persistence(tmp_path):
    """
    Tests saving and loading data using DataManager.
    """
    # Use a temp file
    d = tmp_path / "test_user_data.json"
    DataManager.DATA_FILE = str(d)

    dm = DataManager()

    # Check default budget
    budget = dm.get_budget()
    assert budget["Food & Drink"] == 150

    # Update budget
    new_budget = budget.copy()
    new_budget["Food & Drink"] = 200
    dm.update_budget(new_budget)

    # Reload
    dm2 = DataManager()
    assert dm2.get_budget()["Food & Drink"] == 200

    # Add Goal
    dm.add_goal({"name": "Test Goal", "target": 1000, "current": 0})
    goals = dm.get_goals()
    assert len(goals) == 1
    assert goals[0]["name"] == "Test Goal"

    # Update Goal
    goal_id = goals[0]["id"]
    dm.update_goal(goal_id, 100)
    goals = dm.get_goals()
    assert goals[0]["current"] == 100
