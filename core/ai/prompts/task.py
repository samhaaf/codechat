from .prompt import Prompt

class TaskPrompt(Prompt):
    def __init__(self, task_name):
        super().__init__()
        self.task_name = task_name

    def render(self):
        return f"-- TASK {self.task_name} --\n{super().render()}\n-- END TASK --"
