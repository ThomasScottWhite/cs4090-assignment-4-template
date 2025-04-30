import pytest
import tempfile
import os
import json
import sys
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.modules['streamlit'] = MagicMock()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.tasks import (
    load_tasks,
    save_tasks,
    reset_tasks
)
from src.app import display_task_progress

@pytest.fixture
def temp_task_file():
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
        sample_tasks = [
            {"id": 1, "title": "Task 1", "description": "Desc 1", "priority": "High", "category": "Work", "due_date": "2025-04-20", "completed": False},
            {"id": 2, "title": "Task 2", "description": "Desc 2", "priority": "Medium", "category": "Personal", "due_date": "2025-04-15", "completed": True}
        ]
        temp.write(json.dumps(sample_tasks).encode('utf-8'))
        temp_name = temp.name
    
    yield temp_name
    
    # Clean up the temporary file
    if os.path.exists(temp_name):
        os.unlink(temp_name)

# The first test I wrote was to check if the tasks were empty when the reset function was called
# this ensures that loading tasks after resetting returns an empty list
# and doesnt throw an error
def test_reset_tasks_empty_file(temp_task_file):
    tasks = load_tasks(temp_task_file)
    assert len(tasks) > 0
    
    reset_result = reset_tasks(temp_task_file)
    
    assert reset_result == []
    
    tasks = load_tasks(temp_task_file)
    assert tasks == []


# The second test I wrote was to check if the reset function works as expected
# This is a more in-depth test that checks if the reset function actually clears the file
def test_reset_tasks_file_content(temp_task_file):
    reset_tasks(temp_task_file)
    
    with open(temp_task_file, 'r') as f:
        content = f.read()
        assert content.strip() in ('[]', '[\n]', '[\n  \n]') # The Json Auto Formatter is evil for making this test fail so many times

# The third test I wrote was to check if the reset function creates a file if it doesn't exist
def test_reset_tasks_creates_file_if_missing():
    non_existent_file = os.path.join(tempfile.gettempdir(), 'non_existent_tasks.json')
    
    if os.path.exists(non_existent_file):
        os.unlink(non_existent_file)
    
    reset_tasks(non_existent_file)
    
    assert os.path.exists(non_existent_file)
    tasks = load_tasks(non_existent_file)
    assert tasks == []
    
    os.unlink(non_existent_file)

#  This then starts the progress bar tests, this one shows if the progress bar is displayed
def test_display_task_progress_empty_tasks():
    with patch('src.app.st.info') as mock_info:
        display_task_progress([])
        mock_info.assert_called_once_with("No tasks available. Add tasks to see progress.")

# This test checks if the progress bar is displayed correctly when tasks are present
# It checks if the progress bar is displayed correctly when tasks are present
def test_display_task_progress_metrics():
    tasks = [
        {"id": 1, "title": "Task 1", "completed": False},
        {"id": 2, "title": "Task 2", "completed": True},
        {"id": 3, "title": "Task 3", "completed": False},
        {"id": 4, "title": "Task 4", "completed": False}
    ]
    
    with patch('src.app.st.subheader') as mock_subheader, \
         patch('src.app.st.columns') as mock_columns, \
         patch('src.app.st.progress') as mock_progress:
        
        mock_col = MagicMock()
        mock_columns.return_value = [mock_col, mock_col, mock_col]
        
        display_task_progress(tasks)
        
        mock_subheader.assert_called_once_with("Task Completion Progress")
        
        mock_progress.assert_called_once_with(0.25)
