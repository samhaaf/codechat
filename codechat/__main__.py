from core.ai.llms import models
import argparse
import copy
import os
import threading
import time
import sys
import traceback
import re
from .files import get_updated_files_in, get_files_content, display_files
from .art import title_art
# from .prompts import system_prompt, spelling_prompt  # Removed totality_prompt
from .config import config, update_config, ALLOWED_CONFIG_OPTIONS, save_config
from .user_interface import UserInterface
from .apply_diff import apply_cli
import json

def main():
    valid_commands = [
        "/debug",
        "/reset",
        "/deltas",
        "/patch",
        "/errors",
        "/include",
        "/diff",
        "/diffs",
        "/included",
        '/model',
        '/config',
        '/prompt',
        '/prompt-edit',
        '/prompt-list'  # Newly added command
    ]

    ui = UserInterface()  # Initialize the UserInterface

    def new_session(model='4o', history=None):
        ui.print_info(f'New session with model `{model}`..')
        session = models[model]().get_session(history=history)
        return session

    def get_files_prompt(paths):
        if len(paths) > 0:
            return get_files_content(paths, exclusion_rules=exclusion_rules) + '\n'
        return ''

    parser = argparse.ArgumentParser(description='AI Assistant for Coding Assistance')
    parser.add_argument('--model', '-m', type=str, default=config.get('model', '4o'), help='Specify the model to use')
    parser.add_argument('--CHDIR', type=str, help='Path to change the current directory to', default=None)
    parser.add_argument('--set', type=str, help='Path to a config.json file to set configuration')
    parser.add_argument('paths', nargs='*', help='Paths to included_files in the session')
    args = parser.parse_args()

    # Handle --set
    if args.set:
        set_config_path = args.set
        if os.path.isfile(set_config_path):
            try:
                with open(set_config_path, 'r') as f:
                    new_config = json.load(f)
                # Validate and update config
                for key, value in new_config.items():
                    if key in ALLOWED_CONFIG_OPTIONS:
                        expected_type = ALLOWED_CONFIG_OPTIONS[key]
                        if isinstance(value, expected_type):
                            config[key] = value
                        else:
                            ui.print_warning(f"Invalid type for '{key}'. Expected {expected_type.__name__}. Skipping.")
                    else:
                        ui.print_warning(f"Unknown configuration option: '{key}'. Skipping.")
                save_config(config)
                ui.print_info(f"Configuration updated from {set_config_path}")
            except json.JSONDecodeError:
                ui.print_error(f"Error: The file {set_config_path} is not valid JSON.")
            except Exception as e:
                ui.print_error(f"Error updating configuration: {e}")
        else:
            ui.print_error(f"Error: The file {set_config_path} does not exist.")
        # Optionally, exit after setting config
        sys.exit(0)

    # Handle --CHDIR
    if args.CHDIR:
        os.chdir(args.CHDIR)

    model = args.model if args.model else config.get('model', '4o')
    included_files = args.paths
    session = None
    prompt = ""
    user_input = None
    last_response = None
    last_delta_times = {}
    last_input_time = time.time()
    errors = []
    exclusion_rules = copy.copy(config['exclude'])

    # Ensure default prompts exist
    if 'prompts' not in config:
        config['prompts'] = {}
    if 'totality' not in config['prompts']:
        config['prompts']['totality'] = (
            "Be thorough. Don't break existing code. Output all of the files you change in totality. "
            "Don't use any placeholders like '...' or 'your logic goes here'."
        )
        save_config(config)

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

    def handle_api_key():
        """
        Checks for OPENAI_API_KEY in environment variables.
        If not found, prompts the user to input it and optionally saves it to shell profiles.
        """
        if 'OPENAI_API_KEY' in os.environ and os.environ['OPENAI_API_KEY']:
            return  # API Key already set

        # List of potential shell profile files
        shell_profiles = [
            os.path.expanduser("~/.bashrc"),
            os.path.expanduser("~/.bash_profile"),
            os.path.expanduser("~/.zshrc"),
            os.path.expanduser("~/.profile"),
            os.path.expanduser("~/.zprofile")
        ]

        # Check if it's been added recently
        api_key = None
        for profile in shell_profiles:
            if os.path.exists(profile):
                with open(profile) as file:
                    for line in file:
                        match = re.match(r'export OPENAI_API_KEY=(.*)', line)
                        if match:
                            value = match.groups()[0]
                            api_key = value.strip('"').strip("'")
                            os.environ['OPENAI_API_KEY'] = api_key.strip()
                            return

        ui.print_warning("OPENAI_API_KEY not found in environment variables.")

        # Prompt user to enter the API key
        api_key = ui.get_user_input("|< Please enter your OpenAI API Key: ")

        if not api_key.strip():
            ui.print_error("No API Key entered. Exiting application.")
            sys.exit(1)

        # Set the API key in the environment
        os.environ['OPENAI_API_KEY'] = api_key.strip()

        # Ask user if they want to save the API key to their shell profile
        save_key = ui.get_confirmation("Do you want to save it for future sessions?")

        if save_key:
            export_line = f'\nexport OPENAI_API_KEY="{api_key.strip()}"\n'

            for profile in shell_profiles:
                try:
                    # Check if the profile file exists
                    if os.path.exists(profile):
                        # Read the current content to avoid duplicates
                        with open(profile, 'r') as file:
                            content = file.read()
                        if 'OPENAI_API_KEY' not in content:
                            with open(profile, 'a') as file:
                                file.write(export_line)
                            ui.print_info(f"Added OPENAI_API_KEY to {profile}")
                except Exception as e:
                    ui.print_error(f"Failed to update {profile}: {str(e)}")
        else:
            ui.print_warning("API Key not saved to shell profiles.")

    def create_prompt(prompt_name):
        """CLI to create a new prompt."""
        ui.print_info(f"Creating a new prompt: '{prompt_name}'")
        prompt_content = ui.get_user_input("|< Enter the prompt content:")
        config['prompts'][prompt_name] = prompt_content
        save_config(config)
        ui.print_info(f"Prompt '{prompt_name}' has been created.")

    def edit_prompt(prompt_name):
        """CLI to edit an existing prompt or create a new one if it doesn't exist."""
        if prompt_name not in config['prompts']:
            ui.print_warning(f"Prompt '{prompt_name}' does not exist. Initiating creation process.")
            create_prompt(prompt_name)
            return
        ui.print_info(f"Editing prompt: '{prompt_name}'")
        current_content = config['prompts'][prompt_name]
        ui.print_info(f"Current content:\n{current_content}")
        new_content = ui.get_user_input("|< Enter the new prompt content:")
        config['prompts'][prompt_name] = new_content
        save_config(config)
        ui.print_info(f"Prompt '{prompt_name}' has been updated.")

    def list_prompts():
        """List all saved prompts."""
        if not config.get('prompts'):
            ui.print_info("No prompts have been saved yet.")
            return
        ui.print_info("Saved Prompts:")
        for prompt_name, prompt_content in config['prompts'].items():
            ui.print(f"\n/prompt {prompt_name}:    {prompt_content}\n")

    def handle_prompt_command(command_parts):
        """Handle the /prompt command within user input."""
        nonlocal prompt
        if len(command_parts) < 2:
            ui.print_warning("Usage: /prompt <prompt_name>")
            return
        prompt_name = command_parts[1]
        if prompt_name in config['prompts']:
            replacement = config['prompts'][prompt_name]
            # Replace the /prompt <prompt_name> with the actual prompt content
            return ' '.join(command_parts[:0] + [replacement] + command_parts[2:])
        else:
            ui.print_warning(f"Prompt '{prompt_name}' not found. Starting prompt creation.")
            create_prompt(prompt_name)
            return ''

    ui.print(title_art)
    handle_api_key()
    reset()

    try:
        while True:
            user_input = ui.get_user_input()

            if not user_input.strip():
                ui.print_warning('No user input provided.')
                continue

            # Handle /prompt-edit command
            if user_input.strip().startswith('/prompt-edit'):
                parts = user_input.strip().split(' ', 1)
                if len(parts) != 2:
                    ui.print_error("Usage: /prompt-edit <prompt_name>")
                    continue
                prompt_name = parts[1]
                edit_prompt(prompt_name)
                continue  # Continue after editing

            # Process /prompt commands within user input
            user_input = re.sub(
                r'/prompt\s+(\w+)',
                lambda match: config['prompts'].get(
                    match.group(1), f"/prompt {match.group(1)}"
                ),
                user_input
            )

            # If any /prompt was not found and created, remove it from prompt
            if '/prompt' in user_input:
                # Split the input to find missing prompts
                parts = user_input.split()
                for i, part in enumerate(parts):
                    if part == '/prompt' and i + 1 < len(parts):
                        prompt_name = parts[i + 1]
                        if prompt_name in config['prompts']:
                            replacement = config['prompts'][prompt_name]
                            parts[i] = replacement
                            del parts[i + 1]
                            ui.print_info(f'Injected /prompt {prompt_name}')
                        else:
                            ui.print_warning(f"Prompt '{prompt_name}' not found. Starting prompt creation.")
                            create_prompt(prompt_name)
                            del parts[i:i+2]
                user_input = ' '.join(parts)

            # Now, check for commands
            first_word = user_input.strip().split(' ')[0]
            if first_word[0] == '/' and first_word not in valid_commands + ['//']:
                ui.print_warning(f'Unrecognized command: {first_word}')
                continue

            if user_input.strip() == '/reset':
                reset()
                continue

            if user_input.strip().split(' ')[0] == '/model':
                parts = user_input.strip().split(' ', 2)
                if len(parts) == 2:
                    new_model = parts[1]
                    if new_model not in models:
                        ui.print_error(f"Model '{new_model}' is not recognized.")
                        continue
                    try:
                        ui.print_info(f"Model set to '{new_model}'")
                        # Instantiate the new LLM model
                        new_llm_instance = models[new_model]()
                        # Fork the current session with the new model
                        session = session.fork(new_llm_instance)
                        # Update the model variable
                        model = new_model
                    except Exception as e:
                        ui.print_error(str(e))
                else:
                    ui.print_error("Usage: /model <new_model>")
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

            if user_input.strip().split(' ')[0] == '/config':
                parts = user_input.strip().split(' ', 2)
                if len(parts) == 2 and parts[1] == 'help':
                    ui.print_info("Usage: /config <option> <value>")
                    ui.print_info("Available options:")
                    for option in DEFAULT_CONFIG.keys():
                        ui.print_info(f" - {option}")
                elif len(parts) == 3:
                    _, option, value = parts
                    try:
                        # Type casting based on expected type
                        expected_type = ALLOWED_CONFIG_OPTIONS.get(option)
                        if expected_type == int:
                            value = int(value)
                        elif expected_type == float:
                            value = float(value)
                        elif expected_type == bool:
                            value = value.lower() in ['true', '1', 'yes']
                        elif expected_type == str:
                            value = str(value)
                        elif expected_type == dict:
                            value = json.loads(value)
                        else:
                            raise ValueError(f"No type handling implemented for '{option}'.")

                        update_config(option, value)
                        ui.print_info(f"Configuration '{option}' updated to '{value}'.")
                        # Handle any immediate changes, e.g., if model is updated
                        if option == 'model':
                            if value in models:
                                new_llm_instance = models[value]()
                                session = session.fork(new_llm_instance)
                                model = value
                            else:
                                ui.print_error(f"Model '{value}' is not recognized.")
                    except (ValueError, TypeError) as e:
                        ui.print_error(str(e))
                    except Exception as e:
                        ui.print_error(f"Error: {e}")
                else:
                    ui.print_error("Usage: /config <option> <value> or /config help")
                continue

            # Now, handle the new /prompt-list command
            if user_input.strip() == '/prompt-list':
                list_prompts()
                continue

            # Replace /prompt commands in the prompt
            prompt += user_input

            if user_input[-6:].strip() == '/debug':
                ui.print_warning('Debug mode. Printing out prompt:')
                print(prompt)
                continue

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
            while first_chunk == -1 and time.time() - start < 300:
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

            if time.time() - start >= 200 and first_chunk == -1:
                ui.print_warning('Request timed out. Consider reducing input size.')
                continue

            # Print first chunk because we nexted it as our break indicator
            if first_chunk:
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

if __name__ == "__main__":
    main()
