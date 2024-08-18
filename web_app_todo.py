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

# Function to save archived tasks to Excel
def save_archived_to_excel():
    df_archive = pd.DataFrame(todos, columns=["Archived Tasks"])
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    with pd.ExcelWriter(archiveExcelFile, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
        df_archive.to_excel(writer, sheet_name=today_str, index=False)

# Function to handle checkbox changes
def handle_checkbox_change(item, index):
    if st.session_state.get(f"{item}_{index}", False):
        todos.remove(item)
        save_todos_to_excel()
        save_archived_to_excel()

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

# Display tasks to be archived
st.write("Tasks to be archived:")

# List the current tasks with checkboxes
for i, item in enumerate(todos):
    st.checkbox(item, key=f"{item}_{i}", on_change=handle_checkbox_change, args=(item, i))

# Separator
st.markdown("---")

# Calculate counts
total_count = len(todos)

# Display progress bar
st.write(f"## Task Archive Progress: {total_count}/{total_count} tasks available to be archived")
st.progress(1.0)  # Always 100% since all tasks are in the list

# Motivational message
if total_count > 0:
    st.write("### Keep going! You have tasks ready to be archived. Stay focused and complete your tasks!")
else:
    st.write("### Great job! All tasks are archived. Add new tasks to get started!")

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
