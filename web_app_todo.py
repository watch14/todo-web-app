import streamlit as st
import pandas as pd
import os
import datetime

# File paths for the to-do lists and archives
todosExcelFile = "files/todos_summary.xlsx"
archiveExcelFile = "files/archived_tasks.xlsx"

# Initialize files if necessary
def initialize_excel_files(todos_file, archive_file):
    if not os.path.exists(todos_file):
        df_empty = pd.DataFrame(columns=["To-Do Tasks"])
        df_empty.to_excel(todos_file, index=False, sheet_name='To-Do Tasks')
    if not os.path.exists(archive_file):
        df_empty = pd.DataFrame(columns=["Archived Tasks"])
        df_empty.to_excel(archive_file, index=False)

initialize_excel_files(todosExcelFile, archiveExcelFile)

# Load data
def load_todos():
    if os.path.exists(todosExcelFile):
        return pd.read_excel(todosExcelFile, sheet_name='To-Do Tasks')['To-Do Tasks'].tolist()
    return []

todos = load_todos()

# Save to-do list to Excel
def save_todos_to_excel():
    df_todos = pd.DataFrame(todos, columns=["To-Do Tasks"])
    with pd.ExcelWriter(todosExcelFile, mode='w', engine='openpyxl') as writer:
        df_todos.to_excel(writer, sheet_name='To-Do Tasks', index=False)

# Save checked tasks to archive
def save_task_to_archive(task):
    today_str = datetime.date.today().strftime('%Y-%m-%d')

    if os.path.exists(archiveExcelFile):
        with pd.ExcelFile(archiveExcelFile) as xls:
            if today_str in xls.sheet_names:
                df_archive = pd.read_excel(xls, sheet_name=today_str)
                new_task_df = pd.DataFrame([task], columns=["Archived Tasks"])
                df_archive = pd.concat([df_archive, new_task_df], ignore_index=True)
            else:
                df_archive = pd.DataFrame([task], columns=["Archived Tasks"])
    else:
        df_archive = pd.DataFrame([task], columns=["Archived Tasks"])

    with pd.ExcelWriter(archiveExcelFile, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
        df_archive.to_excel(writer, sheet_name=today_str, index=False)

# Handle checkbox changes
def handle_checkbox_change(item, index):
    if st.session_state.get(f"{item}_{index}", False):
        save_task_to_archive(item)
        todos.remove(item)
        save_todos_to_excel()

# Add a new task
def addTodo():
    todo = st.session_state.get("newTodo", "").strip()
    if todo:
        todos.append(todo.title())
        save_todos_to_excel()
        st.session_state["newTodo"] = ""

# Calculate today's archived tasks and progress
def get_today_archived_tasks():
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    if os.path.exists(archiveExcelFile):
        with pd.ExcelFile(archiveExcelFile) as xls:
            if today_str in xls.sheet_names:
                return pd.read_excel(xls, sheet_name=today_str)
    return pd.DataFrame(columns=["Archived Tasks"])

# App header
st.set_page_config(page_title="Daily To-Do App", page_icon=":memo:")

st.title("📝 My Daily To-Do App")
st.write("### Improve your productivity each day!")

# Input for adding new tasks
st.text_input(
    label="Add a New Task:",
    placeholder="Enter a task...",
    key="newTodo",
    on_change=addTodo,
    help="Type a task and press Enter to add it to your list."
)

# Display tasks to be done
st.write("### Tasks to Be Done")

# List the current tasks with checkboxes
for i, item in enumerate(todos):
    st.checkbox(item, key=f"{item}_{i}", on_change=handle_checkbox_change, args=(item, i))

# Separator
st.markdown("---")

# Calculate progress
total_tasks = len(todos) + len(get_today_archived_tasks())
completed_tasks_today = len(get_today_archived_tasks())
completion_percentage = (completed_tasks_today / total_tasks) if total_tasks > 0 else 0

# Display progress bar
st.write(f"## Task Completion Progress: {completed_tasks_today}/{total_tasks} tasks completed")
st.progress(completion_percentage)

# Show archived tasks using an expander
st.markdown("---")
with st.expander("📂 View Archived Tasks", expanded=False):
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
        df_archive = get_today_archived_tasks() if selected_date_str == datetime.date.today().strftime('%Y-%m-%d') else pd.read_excel(archiveExcelFile, sheet_name=selected_date_str)
        
        if not df_archive.empty:
            st.write(f"Archived Tasks for {selected_date_str}:")
            for task in df_archive['Archived Tasks']:
                st.checkbox(task, value=True, key=f"archive_{task}", disabled=True)
        else:
            st.write(f"No archived tasks found for {selected_date_str}.")
    else:
        st.write("Not enough data to show the slider. Only one date available.")
