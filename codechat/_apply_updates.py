import re
import os

def check_for_file_updates(response, ui):
    # Use regex to find code blocks with filenames
    pattern = r'```([^\n]*)\n(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)

    updates = []

    for filename, content in matches:
        filename = filename.strip()
        if filename and content:
            updates.append((filename, content))

    if updates:
        ui.print_info("Detected suggested file updates:")
        for i, (filename, _) in enumerate(updates):
            ui.print_info(f"{i+1}. {filename}")

        # Ask user if they want to apply the changes
        for filename, content in updates:
            ui.print_info(f"\nProposed changes to {filename}:\n")
            ui.print(content)
            apply_change = ui.get_confirmation(f"\nDo you want to apply changes to {filename}?")
            if apply_change:
                apply_file_update(filename, content, ui)
            else:
                ui.print_info(f"Skipped updating {filename}.")

def apply_file_update(filename, content, ui):
    try:
        # Ensure the directory exists
        directory = os.path.dirname(filename)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(filename, 'w') as file:
            file.write(content)
        ui.print_info(f"Updated {filename} successfully.")
    except Exception as e:
        ui.print_error(f"Failed to update {filename}: {e}")
