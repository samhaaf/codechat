import os
import shutil
import sys
from datetime import datetime

this_dir = os.dirname(__file__)


def init(path='./'):
    deltas_path = os.path.join(path, 'deltas')
    if not os.path.exists(deltas_path):
        os.makedirs(deltas_path)
        date_str = datetime.now().strftime('%Y-%m-%d')
        new_dir = os.path.join(deltas_path, date_str)
        os.makedirs(new_dir)
        shutil.copytree(os.path.join(this_dir, 'init_template'), new_dir)
    else:
        print("Folder already exists.")
        exit(0)


def help_cli():
    """
    This function provides a command line interface for the user to interact with the database.
    It provides options for initializing the database and defining the database in terms of the database schemas.
    """
    print("1. init")
    print("2. JSON Schema")
    user_input = input("Please enter the number of your choice: ")
    if user_input == '1':
        print("This will create a db folder.")
    elif user_input == '2':
        print("Define the database in terms of the database schemas in the ai_toolkit/utils/database/json_schema folder.")
    else:
        print("Accepted arguments are '1' for 'db init' to initialize the database, '2' for 'db JSON Schema' to define the database, and '3' for 'db help' to open the help cli.")

def cli():
    if len(sys.argv) < 2:
        print("Please provide a command. Use 'cli help' for a list of commands.")
        return
    command = sys.argv[1]
    if command == 'init':
        path = sys.argv[2] if len(sys.argv) > 2 else './'
        init(path)
    elif command == 'help':
        help_cli()
    else:
        print(f"Unknown command '{command}'. Use 'cli help' for a list of commands.")
