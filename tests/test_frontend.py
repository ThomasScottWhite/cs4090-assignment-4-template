# This file was a ton of work and im not sure if it was even needed.
# It basically tests the frontend of the app, I wasnt sure if the frontend needed 90% code coverage
# or just the backend.

# Given that this was probably more effort than everything else combined, it probably wasnt needed lol.
import sys
import os

from unittest.mock import MagicMock

import pytest
import json
from datetime import datetime
from unittest.mock import patch, call

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.app import developer_tools, render_task_display, add_new_task
from src.tasks import add_new_task_to_list


@pytest.fixture
def sample_tasks():
    return [
        {"id": 1, "title": "Task 1", "description": "Desc 1", "priority": "High", "category": "Work", "due_date": "2025-04-20", "completed": False},
        {"id": 2, "title": "Task 2", "description": "Desc 2", "priority": "Medium", "category": "Personal", "due_date": "2025-04-15", "completed": True},
        {"id": 3, "title": "Task 3", "description": "Desc 3", "priority": "Low", "category": "School", "due_date": "2024-04-20", "completed": False},
    ]

import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_streamlit():
    with patch('src.app.st', new_callable=MagicMock) as mock_st:
        real_session = {}
        type(mock_st).session_state = property(lambda self: real_session)
        yield mock_st
        mock_st.reset_mock()


def test_developer_tools_buttons(mock_streamlit):
    
    with patch('subprocess.run') as mock_subprocess_run:
        mock_streamlit.button.side_effect = [True, False, False, False, False, False]
        
        developer_tools()
        
        mock_streamlit.header.assert_called_once_with("Developer Tools")
        
        assert mock_streamlit.button.call_count == 6
        mock_streamlit.button.assert_any_call("Run Pytest ")
        mock_streamlit.button.assert_any_call("Run Pytest + Coverage Report")
        mock_streamlit.button.assert_any_call("Run Parameterized Tests")
        mock_streamlit.button.assert_any_call("Run Tests with Mocking")
        mock_streamlit.button.assert_any_call("Generate Full HTML Test Report")
        
        mock_subprocess_run.assert_called_once()
        args, _ = mock_subprocess_run.call_args
        assert args[0] == ["pytest"]

# These tests are for the buttons in the developer tools section
# Pretty much boilerplate they shoud probably be moved into one test
# but I have already spent to much time on this
def test_developer_tools_coverage_button(mock_streamlit):
    
    with patch('subprocess.run') as mock_subprocess_run:
        mock_streamlit.button.side_effect = [False, True, False, False, False, False]
        
        developer_tools()
        
        mock_subprocess_run.assert_called_once()
        args, _ = mock_subprocess_run.call_args
        assert args[0] == ["pytest", "--cov=src", "--cov-report=term-missing"]

def test_developer_tools_param_button(mock_streamlit):
    with patch('subprocess.run') as mock_subprocess_run:
        mock_streamlit.button.side_effect = [False, False, True, False, False, False] 

        developer_tools()

        mock_subprocess_run.assert_called_once_with(["pytest", "-k", "test_param"], capture_output=True, text=True)

def test_developer_tools_mock_button(mock_streamlit):
    with patch('subprocess.run') as mock_subprocess_run:
        mock_streamlit.button.side_effect = [False, False, False, True, False, False]

        developer_tools()

        mock_subprocess_run.assert_called_once_with(["pytest", "-k", "test_mock"], capture_output=True, text=True)

def test_developer_tools_html_button(mock_streamlit):
    with patch('subprocess.run') as mock_subprocess_run:
        mock_streamlit.button.side_effect = [False, False, False, False, True, False]  # 5th button True

        developer_tools()

        mock_subprocess_run.assert_called_once_with(["pytest", "--html=report.html"])

def test_developer_tools_bdd_button(mock_streamlit):
    with patch('subprocess.run') as mock_subprocess_run:
        mock_streamlit.button.side_effect = [False, False, False, False, False, True]

        developer_tools()

        mock_subprocess_run.assert_called_once_with(
            ["pytest", "-k", "test_user_can"], 
            capture_output=True, 
            text=True
        )

# This test if the render_task_display function works
def test_render_task_display_incomplete(mock_streamlit, sample_tasks):
    """Test rendering an incomplete task"""
    
    task = sample_tasks[0]
    
    col1_mock, col2_mock = MagicMock(), MagicMock()
    mock_streamlit.columns.return_value = [col1_mock, col2_mock]
    
    col2_mock.button.return_value = False
    
    render_task_display(task, sample_tasks)
    
    mock_streamlit.columns.assert_called_once_with([4, 1])
    
    col1_mock.markdown.assert_called_once_with(f"**{task['title']}**")
    
    col1_mock.write.assert_called_once_with(task["description"])
    col1_mock.caption.assert_called_once_with(f"Due: {task['due_date']} | Priority: {task['priority']} | Category: {task['category']}")
    
    col2_mock.button.assert_any_call("Complete", key=f"complete_{task['id']}")
    col2_mock.button.assert_any_call("Delete", key=f"delete_{task['id']}")
    col2_mock.button.assert_any_call("Edit", key=f"edit_{task['id']}")

def test_render_task_display_completed(mock_streamlit, sample_tasks):    
    task = sample_tasks[1]
    
    col1_mock, col2_mock = MagicMock(), MagicMock()
    mock_streamlit.columns.return_value = [col1_mock, col2_mock]
    
    col2_mock.button.return_value = False
    
    render_task_display(task, sample_tasks)
    
    col1_mock.markdown.assert_called_once_with(f"~~**{task['title']}**~~")
    
    col2_mock.button.assert_any_call("Undo", key=f"complete_{task['id']}")


from unittest.mock import MagicMock, patch
from datetime import datetime
from src.app import add_new_task  # or your relative import

@patch('src.app.add_new_task_to_list')
def test_add_new_task(mock_add_new_task_to_list, mock_streamlit, sample_tasks):    
    sidebar_form_mock = MagicMock()
    mock_streamlit.sidebar.form.return_value.__enter__.return_value = sidebar_form_mock

    sidebar_form_mock.text_input.return_value = "New Task"
    sidebar_form_mock.text_area.return_value = "New Description"
    sidebar_form_mock.selectbox.side_effect = ["High", "Work"]
    sidebar_form_mock.date_input.return_value = datetime(2025, 5, 1)
    sidebar_form_mock.form_submit_button.return_value = True

    add_new_task(sample_tasks)

    mock_streamlit.sidebar.success.assert_called_once_with("Task added successfully!")

def test_reset_all_tasks(mock_streamlit):
    from src.app import reset_all_tasks
    
    expander_mock = MagicMock()
    mock_streamlit.expander.return_value.__enter__.return_value = expander_mock
    expander_mock.button.return_value = True  # Simulate clicking reset

    with patch('src.app.reset_tasks') as mock_reset_tasks:
        reset_all_tasks()
        
        mock_streamlit.header.assert_called_once_with("Reset Tasks")
        mock_streamlit.expander.assert_called_once_with("Reset All Tasks")
        mock_streamlit.warning.assert_called_once()
        mock_reset_tasks.assert_called_once()
        mock_streamlit.success.assert_called_once_with("All tasks have been deleted!")

def test_filter_tasks_by_category_priority(mock_streamlit, sample_tasks):
    from src.app import filter_tasks
    
    mock_streamlit.columns.return_value = [MagicMock(), MagicMock()]
    mock_streamlit.selectbox.side_effect = ["Work", "High"]
    mock_streamlit.checkbox.return_value = True
    
    filtered = filter_tasks(sample_tasks)

    assert len(filtered) == 1
    assert filtered[0]["category"] == "Work"
    assert filtered[0]["priority"] == "High"

def test_render_edit_task_form_save(mock_streamlit, sample_tasks):
    from src.app import render_edit_task_form
    
    task = sample_tasks[0]
    
    expander_mock = MagicMock()
    mock_streamlit.expander.return_value.__enter__.return_value = expander_mock
    
    expander_mock.text_input.return_value = "Updated Title"
    expander_mock.text_area.return_value = "Updated Description"
    expander_mock.selectbox.side_effect = ["High", "Work"]
    expander_mock.date_input.return_value = datetime(2025, 6, 1)
    expander_mock.button.side_effect = [True, False]

    with patch('src.app.update_task') as mock_update_task, patch('src.app.save_tasks') as mock_save_tasks:
        render_edit_task_form(task, sample_tasks)
        
        mock_update_task.assert_called_once()
        mock_save_tasks.assert_called_once()
        mock_streamlit.success.assert_called_once_with("Task updated successfully!")

def test_editing_task_session_state(mock_streamlit):
    from src.app import start_editing_task, stop_editing_task, is_editing

    task_id = 123
    start_editing_task(task_id)
    assert is_editing(task_id) == True

    stop_editing_task(task_id)
    assert is_editing(task_id) == False

# This just tests if the main funciton works, it was needed for 90% code coverage
def test_main_runs(mock_streamlit):
    from src.app import main

    mock_streamlit.title.return_value = None
    mock_streamlit.header.return_value = None
    mock_streamlit.columns.return_value = [MagicMock(), MagicMock()]
    mock_streamlit.checkbox.return_value = True
    mock_streamlit.selectbox.side_effect = ["All", "All"]
    mock_streamlit.spinner.return_value.__enter__.return_value = None
    mock_streamlit.expander.return_value.__enter__.return_value = MagicMock()
    mock_streamlit.button.return_value = False 

    with patch('src.app.load_tasks', return_value=[]), \
         patch('src.app.add_new_task'), \
         patch('src.app.display_task_progress'), \
         patch('src.app.filter_tasks', return_value=[]), \
         patch('src.app.display_task'), \
         patch('src.app.reset_all_tasks'), \
         patch('src.app.developer_tools'):
        main()

