import pytest
import pytest
import tempfile
import os
import json
import sys
from datetime import datetime

from unittest.mock import MagicMock
sys.modules['streamlit'] = MagicMock()

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
    update_task,
    add_new_task_to_list,
)

@pytest.fixture
def sample_tasks():
    return [
        {"id": 1, "title": "Task 1", "description": "Desc 1", "priority": "High", "category": "Work", "due_date": "2025-04-20", "completed": False},
        {"id": 2, "title": "Task 2", "description": "Desc 2", "priority": "Medium", "category": "Personal", "due_date": "2025-04-15", "completed": True},
        {"id": 3, "title": "Task 3", "description": "Desc 3", "priority": "Low", "category": "School", "due_date": "2024-04-20", "completed": False},
    ]

def test_save_and_load_tasks(sample_tasks):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_path = temp_file.name
    save_tasks(sample_tasks, temp_path)
    loaded = load_tasks(temp_path)
    assert loaded == sample_tasks
    os.remove(temp_path)

def test_load_tasks_file_not_found():
    result = load_tasks(file_path="non_existent_file.json")
    assert result == []

def test_load_tasks_invalid_json():
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file.write("{ invalid json") 
        temp_path = temp_file.name
    
    result = load_tasks(file_path=temp_path)
    assert result == []
    
    os.remove(temp_path)

def test_generate_unique_id(sample_tasks):
    uid = generate_unique_id(sample_tasks)
    assert uid == 4

def test_filter_tasks_by_priority(sample_tasks):
    high_priority = filter_tasks_by_priority(sample_tasks, "High")
    assert len(high_priority) == 1
    assert high_priority[0]["priority"] == "High"

def test_filter_tasks_by_category(sample_tasks):
    work_tasks = filter_tasks_by_category(sample_tasks, "Work")
    assert len(work_tasks) == 1
    assert work_tasks[0]["category"] == "Work"

def test_filter_tasks_by_completion(sample_tasks):
    incomplete = filter_tasks_by_completion(sample_tasks, completed=False)
    assert len(incomplete) == 2
    completed = filter_tasks_by_completion(sample_tasks, completed=True)
    assert len(completed) == 1

def test_search_tasks(sample_tasks):
    found = search_tasks(sample_tasks, "Task 1")
    assert len(found) == 1
    assert found[0]["title"] == "Task 1"

def test_get_overdue_tasks(sample_tasks):
    overdue = get_overdue_tasks(sample_tasks)
    assert any(task["due_date"] < "2025-01-01" for task in overdue)

def test_toggle_task_completion(sample_tasks):
    toggle_task_completion(sample_tasks, 1)

    assert sample_tasks[0]["completed"] == True

    toggle_task_completion(sample_tasks, 1)

    assert sample_tasks[0]["completed"] == False

def test_delete_task(sample_tasks):
    sample_tasks = delete_task(sample_tasks, 1)
    assert len(sample_tasks) == 2
    assert sample_tasks[0]["id"] == 2

def test_update_task():
    task = {
        "id": 1,
        "title": "Original Title",
        "description": "Original Description",
        "priority": "Low",
        "category": "Work",
        "due_date": "2025-04-20"
    }
    
    new_fields = {
        "title": "Updated Title",
        "description": "Updated Description",
        "priority": "High",
        "category": "Personal",
        "due_date": datetime.strptime("2025-05-15", "%Y-%m-%d")
    }
    
    update_task(task, new_fields)
    
    assert task["title"] == "Updated Title"
    assert task["description"] == "Updated Description"
    assert task["priority"] == "High"
    assert task["category"] == "Personal"
    assert task["due_date"] == "2025-05-15"

def test_add_new_task_to_list():
    
    tasks = []
    
    title = "Test Task"
    description = "Test Description"
    priority = "Medium"
    category = "School"
    due_date = datetime.strptime("2025-06-10", "%Y-%m-%d")
    
    tasks = add_new_task_to_list(tasks, title, description, priority, category, due_date)

    assert len(tasks) == 1
    assert tasks[0]["title"] == "Test Task"
    assert tasks[0]["description"] == "Test Description"
    assert tasks[0]["priority"] == "Medium"
    assert tasks[0]["category"] == "School"
    assert tasks[0]["due_date"] == "2025-06-10"
    assert tasks[0]["completed"] == False
    assert "id" in tasks[0]
    assert "created_at" in tasks[0]
