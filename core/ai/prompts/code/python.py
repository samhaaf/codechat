from .code import CodePrompt

class PythonPrompt(CodePrompt):

    def line_is_comment(self, line, _vars):
        stripped_line = line.strip()

        _vars.setdefault("close_comment_on", None)

        if _vars["close_comment_on"] is not None:
            if _vars["close_comment_on"] in stripped_line:
                _vars["close_comment_on"] = None
            return True, _vars

        if stripped_line.startswith("#"):
            return True, _vars

        if stripped_line.startswith('"""'):
            _vars["close_comment_on"] = '"""'
            return True, _vars

        if stripped_line.startswith("'''"):
             _vars["close_comment_on"] = "'''"
             return True, _vars

        return False, _vars
