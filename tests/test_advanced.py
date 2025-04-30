import pytest
import pytest
import tempfile
import os
import json
import sys
from datetime import datetime

from unittest.mock import MagicMock, patch
mock_streamlit = MagicMock()
mock_streamlit.columns.return_value = [MagicMock(), MagicMock()]
sys.modules['streamlit'] = mock_streamlit

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.app import toggle_task_completion, delete_task, filter_tasks
from src.tasks import (
    load_tasks,
    save_tasks,
    generate_unique_id,
    filter_tasks_by_priority,
    filter_tasks_by_category,
    filter_tasks_by_completion,
    search_tasks,
    get_overdue_tasks,
)

@pytest.fixture
def sample_tasks():
    return [
        {"id": 1, "title": "Task 1", "description": "Desc 1", "priority": "High", "category": "Work", "due_date": "2025-04-20", "completed": False},
        {"id": 2, "title": "Task 2", "description": "Desc 2", "priority": "Medium", "category": "Personal", "due_date": "2025-04-15", "completed": True},
        {"id": 3, "title": "Task 3", "description": "Desc 3", "priority": "Low", "category": "School", "due_date": "2024-04-20", "completed": False},
    ]

# This uses the mock streamlit to test if the task completion toggle works
def test_mock_filter_tasks_category_filtering(sample_tasks):
    with patch('src.app.st.selectbox', side_effect=["Work", "All"]), patch('src.app.st.checkbox', return_value=True):
        filtered = filter_tasks(sample_tasks)
        assert len(filtered) == 1
        assert filtered[0]["category"] == "Work"

def test_mock_filter_tasks_priority_filtering(sample_tasks):
    with patch('src.app.st.selectbox', side_effect=["All", "High"]), patch('src.app.st.checkbox', return_value=True):
        filtered = filter_tasks(sample_tasks)
        assert len(filtered) == 1
        assert filtered[0]["priority"] == "High"

def test_mock_filter_tasks_show_completed(sample_tasks):
    with patch('streamlit.selectbox', side_effect=["All", "All"]), patch('streamlit.checkbox', return_value=False):
        filtered = filter_tasks(sample_tasks)
        assert all(not task["completed"] for task in filtered)


# Uses parametrize to test different task categories
@pytest.mark.parametrize("priority", ["High", "Medium", "Low"])
def test_param_filter_tasks_by_priority(sample_tasks, priority):
    filtered = filter_tasks_by_priority(sample_tasks, priority)
    for task in filtered:
        assert task["priority"] == priority

@pytest.mark.parametrize("category", ["Work", "Personal", "School"])
def test_param_filter_tasks_by_category(sample_tasks, category):
    filtered = filter_tasks_by_category(sample_tasks, category)
    for task in filtered:
        assert task["category"] == category

@pytest.mark.parametrize("completed,expected_count", [(True, 1), (False, 2)])
def test_param_filter_tasks_by_completion(sample_tasks, completed, expected_count):
    filtered = filter_tasks_by_completion(sample_tasks, completed=completed)
    assert len(filtered) == expected_count


@pytest.mark.parametrize("query,expected_title", [
    ("Task 1", "Task 1"),
    ("Task 2", "Task 2"),
    ("Desc 1", "Task 1"),
])
def test_param_search_tasks(sample_tasks, query, expected_title):
    results = search_tasks(sample_tasks, query)
    assert any(expected_title in task["title"] or expected_title in task["description"] for task in results)
