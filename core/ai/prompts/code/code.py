import os
from ..prompt import Prompt

class CodePrompt(Prompt):
    def __init__(self, file_path, only_comments=False, line_start=None, line_end=None):
        super().__init__()
        self.file_path = file_path
        self.only_comments = only_comments
        self.line_start = line_start
        self.line_end = line_end

    def read_file(self):
        with open(self.file_path, "r") as file:
            return file.readlines()

    def line_is_comment(self, line, _vars):
        return False, _vars

    def process_lines(self, lines):
        file_type = os.path.splitext(self.file_path)[1][1:]
        processed_lines = []
        _vars = {}

        was_comment = False
        was_dotdotdot = False
        for idx, line in enumerate(lines):
            if self.line_start is not None and idx + 1 < self.line_start:
                continue
            if self.line_end is not None and idx + 1 > self.line_end:
                break

            is_comment, _vars = self.line_is_comment(line, _vars)

            if self.only_comments:
                if is_comment:
                    processed_lines.append(line)
                    was_dotdotdot = False
                    was_comment = True
                else:
                    if was_comment and not was_dotdotdot:
                        processed_lines.append('...')
                        was_dotdotdot = True
                    was_comment = False

            else:
                processed_lines.append(line)

        return processed_lines

    def render(self):
        lines = self.read_file()
        processed_lines = self.process_lines(lines)

        output = [
            "-- FILE --",
            f"file_name: {os.path.basename(self.file_path)}",
            f"file_type: {os.path.splitext(self.file_path)[1][1:]}",
            f"start_line: {self.line_start or 1}",
            f"end_line: {self.line_end or len(lines)}",
            f"only_comments: {self.only_comments}",
            "```",
            "".join(processed_lines),
            "```",
            "-- END FILE --",
        ]

        return "\n".join(output)
