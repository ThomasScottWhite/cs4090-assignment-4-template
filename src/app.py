import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os
# This makes sure that app.py and the tests.py are able to import app.py and task.py properly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.tasks import (
    load_tasks, save_tasks, filter_tasks_by_priority, filter_tasks_by_category, 
    update_task, add_new_task_to_list, filter_tasks_by_completion, 
    toggle_task_completion, delete_task, reset_tasks
)
import subprocess

def start_editing_task(task_id):
    st.session_state[f"editing_{task_id}"] = True

def stop_editing_task(task_id):
    st.session_state[f"editing_{task_id}"] = False

def is_editing(task_id):
    return st.session_state.get(f"editing_{task_id}", False)


def add_new_task(tasks):
    st.sidebar.header("Add New Task")

    with st.sidebar.form(key="new_task_form"):
        task_title      = st.text_input("Task Title")
        task_description = st.text_area("Description")
        task_priority    = st.selectbox("Priority", ["Low", "Medium", "High"])
        task_category    = st.selectbox("Category", ["Work", "Personal", "School", "Other"])
        task_due_date    = st.date_input("Due Date")
        submit_button    = st.form_submit_button("Add Task")

    if submit_button and task_title:
        add_new_task_to_list(
            tasks, task_title, task_description,
            task_priority, task_category, task_due_date
        )
        st.sidebar.success("Task added successfully!")


def filter_tasks(tasks):
    col1, col2 = st.columns(2)
    with col1:
        filter_category = st.selectbox(
            "Filter by Category",
            ["All"] + list(set(task["category"] for task in tasks))
        )
    with col2:
        filter_priority = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"])

    show_completed = st.checkbox("Show Completed Tasks")

    filtered = tasks.copy()
    if filter_category != "All":
        filtered = filter_tasks_by_category(filtered, filter_category)
    if filter_priority != "All":
        filtered = filter_tasks_by_priority(filtered, filter_priority)
    if not show_completed:
        filtered = filter_tasks_by_completion(filtered, completed=False)
    
    return filtered

def render_task_display(task, tasks):
    col1, col2 = st.columns([4, 1])
    with col1:
        if task["completed"]:
            col1.markdown(f"~~**{task['title']}**~~")
        else:
            col1.markdown(f"**{task['title']}**")
        col1.write(task["description"])
        col1.caption(f"Due: {task['due_date']} | Priority: {task['priority']} | Category: {task['category']}")

        if datetime.strptime(task["due_date"], "%Y-%m-%d") < datetime.now():
            col1.warning("This task is overdue!")
    with col2:
        if col2.button("Complete" if not task["completed"] else "Undo", key=f"complete_{task['id']}"):
            toggle_task_completion(tasks, task["id"])
            st.rerun()
        if col2.button("Delete", key=f"delete_{task['id']}"):
            delete_task(tasks, task["id"])
            st.rerun()
        if col2.button("Edit", key=f"edit_{task['id']}"):
            start_editing_task(task["id"])


def render_edit_task_form(task, tasks):
    with st.expander("Edit Task", expanded=True):
        new_title = st.text_input("Edit Title", value=task["title"], key=f"title_{task['id']}")
        new_description = st.text_area("Edit Description", value=task["description"], key=f"desc_{task['id']}")
        new_priority = st.selectbox("Edit Priority", ["Low", "Medium", "High"], index=["Low", "Medium", "High"].index(task["priority"]), key=f"priority_{task['id']}")
        new_category = st.selectbox("Edit Category", ["Work", "Personal", "School", "Other"], index=["Work", "Personal", "School", "Other"].index(task["category"]), key=f"category_{task['id']}")
        new_due_date = st.date_input("Edit Due Date", value=datetime.strptime(task["due_date"], "%Y-%m-%d"), key=f"duedate_{task['id']}")

        if st.button("Save Changes", key=f"save_{task['id']}"):
            new_fields = {
                "title": new_title,
                "description": new_description,
                "priority": new_priority,
                "category": new_category,
                "due_date": new_due_date,
            }
            update_task(task, new_fields)
            save_tasks(tasks)
            stop_editing_task(task["id"])
            st.success("Task updated successfully!")
            st.rerun()

        if st.button("Cancel", key=f"cancel_{task['id']}"):
            stop_editing_task(task["id"])
            st.rerun()

def display_task(task, tasks):
    if is_editing(task["id"]):
        render_edit_task_form(task, tasks)
    else:
        render_task_display(task, tasks)

def developer_tools():
    st.header("Developer Tools")

    if st.button("Run Pytest "):
        with st.spinner("Running tests..."):
            result = subprocess.run(["pytest"], capture_output=True, text=True)
            st.text(result.stdout)

    if st.button("Run Pytest + Coverage Report"):
        with st.spinner("Running tests with coverage..."):
            result = subprocess.run(["pytest", "--cov=src", "--cov-report=term-missing"], capture_output=True, text=True)
            st.text(result.stdout)

    if st.button("Run Parameterized Tests"):
        with st.spinner("Running parameterized tests..."):
            result = subprocess.run(["pytest", "-k", "test_param"], capture_output=True, text=True)
            st.text(result.stdout)

    if st.button("Run Tests with Mocking"):
        with st.spinner("Running tests using mocks..."):
            result = subprocess.run(["pytest", "-k", "test_mock"], capture_output=True, text=True)
            st.text(result.stdout)

    if st.button("Generate Full HTML Test Report"):
        with st.spinner("Generating HTML report..."):
            subprocess.run(["pytest", "--html=report.html"])
            st.success("HTML report generated as report.html! 📄")
    if st.button("Run BDD Tests"):
        with st.spinner("Running BDD tests..."):
            result = subprocess.run(["pytest", "-k", "test_user_can"], capture_output=True, text=True)
            st.text(result.stdout)


def reset_all_tasks():
    st.header("Reset Tasks")
    
    with st.expander("Reset All Tasks"):
        st.warning("This will delete all tasks permanently!")
        if st.button("Reset All Tasks", key="reset_tasks_btn"):
            reset_tasks()
            st.success("All tasks have been deleted!")
            st.rerun()

def display_task_progress(tasks):
    """
    Display a progress bar showing the percentage of completed tasks.
    
    Args:
        tasks (list): List of all task dictionaries
    """
    if not tasks:
        st.info("No tasks available. Add tasks to see progress.")
        return
        
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.get("completed", False))
    
    completion_percentage = (completed_tasks / total_tasks) * 100
    
    st.subheader("Task Completion Progress")
    
    # Display progress metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Completed", f"{completed_tasks}/{total_tasks}")
    with col2:
        st.metric("Remaining", f"{total_tasks - completed_tasks}/{total_tasks}")
    with col3:
        st.metric("Completion Rate", f"{completion_percentage:.1f}%")
    
    # Display progress bar
    st.progress(completed_tasks / total_tasks)

def main():
    st.title("To-Do Application")

    tasks = load_tasks()

    add_new_task(tasks)

    # display_task_progress(tasks)

    st.header("Your Tasks")
    filtered_tasks = filter_tasks(tasks)

    for task in filtered_tasks:
        display_task(task, tasks)
        
    reset_all_tasks()

    developer_tools()

if __name__ == "__main__":
    main()