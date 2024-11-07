import os

from .code.code import CodePrompt
from .prompt import Prompt

class AppTaskPrompt(Prompt):

    def set_project_root(self):
        self.project_root = input("Enter the project root (default to .): ")
        if not self.project_root:
            self.project_root = "."

    def print_current_directory_options(self, path):
        entries = os.listdir(path)
        numbered_entries = []
        for idx, entry in enumerate(entries):
            if os.path.isdir(os.path.join(path, entry)):
                entry += "/"
            numbered_entries.append(f"{idx + 1}. {entry}")
        return "\n".join(numbered_entries)

    def select_files(self):
        while True:
            print(self.print_current_directory_options(self.project_root))

            file_selection = input("Enter file selection (number, dir name or . for all files, or press Enter to finish): ")

            if not file_selection:
                break
            elif file_selection == ".":
                self.project_root = "."
            else:
                self.project_root = os.path.join(self.project_root, file_selection)

    def ask_configuration_options(self):
        self.comments_only = input("Comments only (default True): ")
        self.start_line = input("Start line (default None): ")
        self.end_line = input("End line (default None): ")

        if self.comments_only.lower() not in ["false", "no", "0"]:
            self.comments_only = True
        else:
            self.comments_only = False

        if not self.start_line:
            self.start_line = None
        else:
            self.start_line = int(self.start_line)

        if not self.end_line:
            self.end_line = None
        else:
            self.end_line = int(self.end_line)

    def add_tasks(self):
        while True:
            task = ""
            print("Define the tasks that need to be performed (press Enter twice to finish):")
            while True:
                line = input()
                if not line:
                    break
                task += line + "\n"
            self.add_component(task)

            add_more_tasks = input("Add another task? (default no): ")
            if add_more_tasks.lower() not in ["yes", "y"]:
                break

    def build_prompt(self):
        self.set_project_root()

        while True:
            self.select_files()
            self.ask_configuration_options()

            code_prompt = CodePrompt(file_path=self.project_root,
                                     only_comments=self.comments_only,
                                     line_start=self.start_line,
                                     line_end=self.end_line)
            self.add_component(code_prompt)

            self.add_tasks()

            add_more_files = input("Add more files? (y/n): ")
            if add_more_files.lower() not in ["yes", "y"]:
                break
