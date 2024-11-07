import subprocess
from ai_toolkit.prompts.prompt import Prompt

class DirectoryTreePrompt(Prompt):
    def __init__(self, path="."):
        super().__init__()
        self.path = path

    @classmethod
    def from_cli(cls):
        path = input("Enter the directory path (leave empty for current directory): ")
        path = path or "."

    def get_gittree_output(self):
        try:
            result = subprocess.run(["gittree", "--min-tokens"], capture_output=True, text=True, cwd=self.path, check=True)
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error occurred when running 'gittree --min-tokens' in directory '{self.path}': {e}")
            return None

    def render(self):
        output = [
            "--FILES--",
            self.get_gittree_output(),
            "--END FILES--",
        ]

        return "\n".join(filter(None, output))  # filter out None values in case of errors
