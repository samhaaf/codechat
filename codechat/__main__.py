from core.ai.llms import models
import argparse
import copy
import os
import threading
import time
import sys
import traceback
from .files import get_updated_files_in, get_files_content, display_files, DEFAULT_EXCLUSION_RULES
# from .diffs import diff_cli
from .art import title_art
from .prompts import system_prompt, totality_prompt, spelling_prompt
from .config import config
from .user_interface import UserInterface
from .apply_diff import apply_cli
# from .apply_updates import check_for_file_updates  # Import the new function

def main():
    valid_commands = [
        "/reset",
        "/deltas",
        "/patch",
        "/errors",
        "/include",
        "/totality",
        "/spelling",
        "/diff",
        "/diffs",
        "/included",
        '/model'
    ]

    ui = UserInterface()  # Initialize the UserInterface

    def new_session(model='o1-mini', history=None):
        ui.print_info(f'New session with model `{model}`..')
        session = models[model]().get_session(history=history)
        return session

    def get_files_prompt(paths):
        if len(paths) > 0:
            return get_files_content(paths, exclusion_rules=exclusion_rules) + "\n\n"
        return ''

    parser = argparse.ArgumentParser(description='AI Assistant for Coding Assistance')
    parser.add_argument('--model', '-m', type=str, default='4o')
    parser.add_argument('--CHDIR', type=str, help='Path to change the current directory to', default=None)
    parser.add_argument('paths', nargs='*', help='Paths to included_files in the session')
    args = parser.parse_args()

    if args.CHDIR:
        os.chdir(args.CHDIR)

    model = args.model
    included_files = args.paths
    session = None
    prompt = ""
    user_input = None
    last_response = None
    last_delta_times = {}
    last_input_time = time.time()
    errors = []
    exclusion_rules = copy.copy(DEFAULT_EXCLUSION_RULES)

    def reset(_model=None):
        nonlocal session, prompt, last_delta_times, included_files, model
        model = _model or model
        session = new_session(model)
        prompt = get_files_prompt(included_files)
        last_delta_times = {file: time.time() for file in included_files}
        display_files(included_files, exclusion_rules=exclusion_rules)

    def attach_deltas():
        nonlocal prompt, last_delta_times, included_files
        updated_files = get_updated_files_in(included_files, last_delta_times)
        if updated_files:
            prompt += "These files have been updated:\n\n"
            prompt += get_files_prompt(updated_files)
            # TODO: attach file diffs instead of whole files
            last_delta_times.update({file: time.time() for file in updated_files})
        else:
            ui.print_warning('No file updates detected..')

    def update_included_files():
        nonlocal prompt, last_delta_times, included_files
        new_include = [_ for _ in user_input.strip().split(' ')[1:] if _]
        prompt += "Adding these files to the scope:\n\n"
        prompt += get_files_prompt(new_include) + '\n\n'
        last_delta_times.update({file: time.time() for file in new_include})
        included_files += new_include

    def display_errors():
        nonlocal errors
        if errors:
            for error in errors:
                ui.print_error(error)
        else:
            ui.print_info('|: No errors to display')
        errors = []

    ui.print(title_art)
    reset()

    try:
        while True:
            user_input = ui.get_user_input()

            if not user_input.strip():
                ui.print_warning('No user input provided.')
                continue

            first_word = user_input.strip().split(' ')[0]
            if first_word[0] == '/' and first_word not in valid_commands + ['//']:
                ui.print_warning(f'Unrecognized command: {first_word}')
                continue

            if user_input.strip() == '/reset':
                reset()
                continue

            if user_input.strip().split(' ')[0] == '/model':
                reset(user_input.strip().split(' ')[1])
                continue

            if user_input.strip() == '/apply':
                apply_cli(ui, session)
                continue

            if user_input.strip() == '/deltas':
                attach_deltas()
                continue

            if user_input.strip() == '/errors':
                display_errors()
                continue

            if user_input.strip() == '/included':
                display_files(included_files, exclusion_rules=exclusion_rules)
                continue

            if user_input.strip().split(' ')[0] == '/include':
                update_included_files()
                display_files(included_files, exclusion_rules=exclusion_rules)
                continue

            if '/totality' in user_input:
                ui.print_info('Replacing /totality with the totality_prompt')
                user_input = user_input.replace('/totality', totality_prompt)

            if '/spelling' in user_input:
                ui.print_info('Replacing /spelling with the spelling_prompt')
                user_input = user_input.replace('/spelling', spelling_prompt + "\n")

            prompt += user_input + "\n\n"

            # ui.print_info('Awaiting response', end='')

            # Get result and print waiting dots
            stream = None
            first_chunk = -1
            def _do():
                nonlocal stream, first_chunk
                try:
                    stream = session.call(prompt)
                    first_chunk = next(stream)
                except Exception:
                    print(traceback.format_exc())
                    first_chunk = None 
                    raise
            thread = threading.Thread(target=_do)
            thread.start()

            # Print timer
            start = time.time()
            while first_chunk == -1:
                ui.print_info(
                    f"Awaiting response.. ({round(time.time() - start, 1)}s)",
                    end='\r', flush=True
                )
                # Pause for 0.1 seconds
                time.sleep(0.1)

            # Print again because we ended the last one on '\r'
            ui.print_info(
                f"Awaiting response.. ({round(time.time() - start, 1)}s)\n\n",
            )

            # Print first chunk because we nexted it as our break indicator
            ui.print(first_chunk, end='', flush=True)

            # Iterate response
            last_response = ""
            for chunk in stream:
                if chunk is None:
                    break
                last_response += chunk
                ui.print(chunk, end='', flush=True)
            ui.print('\n\n')

            # After receiving LLM's response, check for file updates
            # check_for_file_updates(last_response, ui)

            prompt = ""
    except KeyboardInterrupt:
        sys.exit(0)
