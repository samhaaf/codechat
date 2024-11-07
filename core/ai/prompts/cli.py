import os
import sys
import pyperclip

from ai_toolkit.prompts.prompt import Prompt
from ai_toolkit.prompts.task import TaskPrompt
from ai_toolkit.prompts.app_task import AppTaskPrompt
from ai_toolkit.prompts.directory_tree import DirectoryTreePrompt
from ai_toolkit.prompts.code.code import CodePrompt
from ai_toolkit.prompts.code.python import PythonPrompt


def display_menu(menu_items):
    os.system('clear')
    print("Welcome to the ChatGPT Prompts CLI")
    print("Please choose an option:")

    for i, item in enumerate(menu_items, start=1):
        print(f"{i}. {item['caption']}")

    print("0. Exit")


def select_code_prompt(file_path, only_comments=False):
    file_extension = os.path.splitext(file_path)[1]

    if file_extension == ".py":
        prompt_class = PythonPrompt
    else:
        prompt_class = CodePrompt

    return prompt_class(file_path, only_comments=only_comments)


def output_prompt_result(prompt):
    print("Print to stdout or copy to clipboard?")
    print("1. Print to stdout")
    print("2. Copy to clipboard")

    choice = input("Enter your choice: ")

    result = prompt.render()

    if choice == "1":
        print(result)
    elif choice == "2":
        pyperclip.copy(result)
        print("Result copied to clipboard.")
    else:
        print("Invalid choice. Defaulting to stdout.")
        print(result)

    input("Press Enter to continue...")


def handle_app_task_prompt():
    app_task_prompt = AppTaskPrompt()
    app_task_prompt.build_prompt()
    output_prompt_result(app_task_prompt)


def handle_code_prompt():
    file_path = input("Enter the file path: ")
    comment_only_input = input("Do you want to run with comment_only? (y/n): ")
    comment_only = True if comment_only_input.lower() == "y" else False
    code_prompt = select_code_prompt(file_path, comment_only)
    output_prompt_result(code_prompt)


def handle_directory_tree_prompt():
    path = input("Enter the directory path (leave empty for current directory): ")
    path = path or "."
    directory_tree_prompt = DirectoryTreePrompt(path)
    output_prompt_result(directory_tree_prompt)


def handle_task_prompt():
    # Instantiate and call the TaskPrompt class
    pass


def main_loop():
    menu_items = [
        {"handler": handle_app_task_prompt, "caption": "App Task"},
        {"handler": handle_code_prompt, "caption": "Code Prompt"},
        {"handler": handle_directory_tree_prompt, "caption": "Directory Tree"},
        {"handler": handle_task_prompt, "caption": "Task Prompt"},
    ]

    while True:
        display_menu(menu_items)

        choice = input("Enter your choice: ")

        if choice == "0":
            sys.exit()
        elif 1 <= int(choice) <= len(menu_items):
            menu_items[int(choice) - 1]["handler"]()
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        sys.exit(1)
