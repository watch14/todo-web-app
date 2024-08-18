import streamlit as st
import pandas as pd
import os
from functions import initialize_excel_files
import datetime

# File paths for the to-do lists and archives
todosExcelFile = "files/todos_summary.xlsx"
archiveExcelFile = "files/archived_tasks.xlsx"

# Initialize files if necessary
initialize_excel_files(todosExcelFile, archiveExcelFile)

# Load data
def load_todos():
    if os.path.exists(todosExcelFile):
        return pd.read_excel(todosExcelFile, sheet_name='To-Do Tasks')['To-Do Tasks'].tolist()
    return []

todos = load_todos()

# Function to save to-do lists to Excel
def save_todos_to_excel():
    df_todos = pd.DataFrame(todos, columns=["To-Do Tasks"])
    with pd.ExcelWriter(todosExcelFile, mode='w', engine='openpyxl') as writer:
        df_todos.to_excel(writer, sheet_name='To-Do Tasks', index=False)

# Function to save a task to the archive
def save_task_to_archive(task):
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    if os.path.exists(archiveExcelFile):
        with pd.ExcelFile(archiveExcelFile) as xls:
            if today_str in xls.sheet_names:
                # Load existing archive data
                df_archive = pd.read_excel(xls, sheet_name=today_str)
                new_task_df = pd.DataFrame([task], columns=["Archived Tasks"])
                df_archive = pd.concat([df_archive, new_task_df], ignore_index=True)
            else:
                # Create new archive data
                df_archive = pd.DataFrame([task], columns=["Archived Tasks"])
    else:
        # Create new archive file
        df_archive = pd.DataFrame([task], columns=["Archived Tasks"])

    # Save updated archive data
    with pd.ExcelWriter(archiveExcelFile, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df_archive.to_excel(writer, sheet_name=today_str, index=False)

# Function to handle checkbox changes
def handle_checkbox_change(item, index):
    if st.session_state.get(f"{item}_{index}", False):
        # Save the checked task to the archive
        save_task_to_archive(item)
        # Remove the checked task from the to-do list
        todos.remove(item)
        # Save updated to-do list to Excel
        save_todos_to_excel()

# Function to add a new task
def addTodo():
    todo = st.session_state.get("newTodo", "").strip()
    if todo:
        todos.append(todo.title())
        save_todos_to_excel()
        st.session_state["newTodo"] = ""

# App header
st.write("""
         # My Daily To-Do App
         ###### Improve your productivity each day!
         """)

# Input for adding new tasks
st.text_input(label="Add Task:", placeholder="Add Task:", key="newTodo", on_change=addTodo)

# Display tasks to be done
st.write("Tasks to be done:")

# List the current tasks with checkboxes
for i, item in enumerate(todos):
    st.checkbox(item, key=f"{item}_{i}", on_change=handle_checkbox_change, args=(item, i))

# Separator
st.markdown("---")

# Calculate counts
total_count = len(todos)  # Total tasks is just the length of todos
completed_count = len([item for item in todos if st.session_state.get(f"{item}_{i}", False)])  # Adjust as needed
completion_percentage = (completed_count / total_count) if total_count > 0 else 0

# Display progress bar
st.write(f"## Task Completion Progress: {completed_count}/{total_count} tasks completed")
st.progress(completion_percentage)

# Motivational message
if completed_count > 0:
    if completion_percentage > 0.75:
        st.write("### Fantastic job! You've completed a significant portion of your tasks. You're doing great!")
    elif completion_percentage > 0.50:
        st.write("### Well done! You've completed more than half of your tasks. Keep pushing forward!")
    elif completion_percentage > 0.25:
        st.write("### Good work! You've made solid progress. Keep working to reach your goal!")
    else:
        st.write("### Keep going! You've made a good start. Stay focused and continue making progress!")
else:
    st.write("### Get started! Add some tasks and start working towards your goals!")

# Show archived tasks using a slider
st.markdown("---")
st.write("### View Archived Tasks")

def load_archive_dates():
    if os.path.exists(archiveExcelFile):
        with pd.ExcelFile(archiveExcelFile) as xls:
            return [datetime.datetime.strptime(sheet_name, '%Y-%m-%d').date() for sheet_name in xls.sheet_names]
    return []

archive_dates = load_archive_dates()

if len(archive_dates) > 1:
    min_date = min(archive_dates)
    max_date = max(archive_dates)
    
    selected_date = st.slider(
        "Select Date for Archived Tasks:",
        min_value=min_date,
        max_value=max_date,
        value=max_date,
        format="YYYY-MM-DD"
    )

    selected_date_str = selected_date.strftime('%Y-%m-%d')
    with pd.ExcelFile(archiveExcelFile) as xls:
        if selected_date_str in xls.sheet_names:
            df_archive = pd.read_excel(xls, sheet_name=selected_date_str)
            st.write(f"Archived Tasks for {selected_date_str}:")
            for task in df_archive['Archived Tasks']:
                st.write(f"- {task}")
        else:
            st.write(f"No archived tasks found for {selected_date_str}.")
else:
    st.write("Not enough data to show the slider. Only one date available.")
