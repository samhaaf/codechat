
import sys
import time

class UserInterface:
    def __init__(self):
        pass

    def get_user_input(self, prompt_message="|< "):
        last_input_time = 0
        multiline = False
        user_input = ''
        first_line = True
        still_inputting = True
        while still_inputting:
            try:
                multiline_input = input(prompt_message if first_line else '')
                first_line = False
            except EOFError:
                sys.exit(0)
            if not multiline and multiline_input.startswith('!@#'):
                multiline = True
                multiline_input = multiline_input[3:]
            elif not multiline and multiline_input.endswith('!@#'):
                multiline = True
                multiline_input = multiline_input[:-3]
            elif multiline and multiline_input.endswith('!@#'):
                multiline_input = multiline_input[:-3]
                multiline = False
            still_inputting = multiline
            last_input_time = time.time()
            user_input += ("" if first_line else '\n') + multiline_input
        return user_input

    def print(self, message='', end='\n', flush=True):
        print(message, end=end, flush=flush)

    def print_error(self, message, end='\n', flush=True):
        print(f"|| {message}", end=end, flush=flush)

    def print_warning(self, message, end='\n', flush=True):
        print(f"|! {message}", end=end, flush=flush)

    def print_info(self, message, end='\n', flush=True):
        print(f"|- {message}", end=end, flush=flush)

    def get_confirmation(self, prompt_message):
        while True:
            response = input(f"|< {prompt_message} [y/n]: ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                self.print("Please enter 'y' or 'n'.")
