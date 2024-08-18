from  time import strftime, sleep
import pandas as pd
import os


def getTodos(file):
    """ Return file content - todos - taks in a List """
    with open(file, "r") as f:
        todos =  f.readlines()
        return todos


def saveFile(file, todos_arg):
    """ Save / Write the content/todos in the file """
    with open(file, "w") as f:
        f.writelines(todos_arg)


def printToods(file):
    """
    get the contetnt of the file 
    and Print each line enumerated 
    """
    todos = getTodos(file)
    print("Your todos:")
    for index, item in enumerate(todos):
        print(f"{index + 1}. {item.strip("\n")}")
        
        
def currentTime():
    """ return current time:
        - %a : day of the week
        - %d : day of the month
        - %b : month
        - %Y : year
        - %H %M %S : hours, minutes, seconds
    """
    curr = strftime("%d %b %Y %H:%M:%S")
    # sleep(1)
    return(curr)



###### EXEL Functions

# Function to initialize or load data from Excel
def initialize_excel_files(file, archive):
    if not os.path.exists(file):
        with pd.ExcelWriter(file, engine='openpyxl') as writer:
            pd.DataFrame(columns=["To-Do Tasks"]).to_excel(writer, sheet_name='To-Do Tasks', index=False)
            pd.DataFrame(columns=["Completed Tasks"]).to_excel(writer, sheet_name='Completed Tasks', index=False)

    if not os.path.exists(archive):
        with pd.ExcelWriter(archive, engine='openpyxl') as writer:
            pd.DataFrame(columns=["Archived Tasks"]).to_excel(writer, sheet_name=today_str, index=False)


# Load existing tasks from Excel
def load_excel_data(file):
    with pd.ExcelFile(file) as xls:
        todos_df = pd.read_excel(xls, sheet_name='To-Do Tasks')
        doneTodos_df = pd.read_excel(xls, sheet_name='Completed Tasks')
    return todos_df['To-Do Tasks'].tolist(), doneTodos_df['Completed Tasks'].tolist()





        
if __name__ == "__main___":
    pass

