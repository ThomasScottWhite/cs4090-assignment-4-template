import pytest
from src.tasks import (
    add_new_task_to_list,
    toggle_task_completion,
    delete_task,
    filter_tasks_by_category,
    filter_tasks_by_priority,
)

@pytest.fixture
def sample_tasks():
    return [
        {"id": 1, "title": "Task 1", "description": "Desc", "priority": "High", "category": "Work", "due_date": "2025-04-20", "completed": False},
        {"id": 2, "title": "Task 2", "description": "Desc", "priority": "Low", "category": "Personal", "due_date": "2025-05-01", "completed": False},
    ]

from datetime import date

# Given an empty task list, when a user adds a task, it appears in the list. 
def test_user_can_add_task():
    tasks = []
    add_new_task_to_list(
        tasks,
        "New Task",
        "New Desc",
        "Medium",
        "School",
        date(2025, 6, 1)  
    )
    assert any(task["title"] == "New Task" for task in tasks)

# Given an incomplete task, when user marks complete, task is completed
def test_user_can_complete_task(sample_tasks):
    toggle_task_completion(sample_tasks, 1)
    assert sample_tasks[0]["completed"] is True

# Given a task list, when a user deletes a task, it is removed from the list
def test_user_can_delete_task(sample_tasks):
    initial_len = len(sample_tasks)
    delete_task(sample_tasks, 1)
    assert len(sample_tasks) == initial_len - 1
    assert not any(task["id"] == 1 for task in sample_tasks)

# Given tasks with different categories, when filtering by category, only matching tasks are shown
def test_user_can_filter_by_category(sample_tasks):
    filtered = filter_tasks_by_category(sample_tasks, "Work")
    assert all(task["category"] == "Work" for task in filtered)
    assert len(filtered) == 1

# Given tasks with different priorities, when filtering by priority, only matching tasks are shown.
def test_user_can_filter_by_priority(sample_tasks):
    filtered = filter_tasks_by_priority(sample_tasks, "Low")
    assert all(task["priority"] == "Low" for task in filtered)
    assert len(filtered) == 1
