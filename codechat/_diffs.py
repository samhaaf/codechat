import subprocess
import re
import os
import platform
import shutil
import traceback
from .files import file_to_string


def move_to_trash(file_path):
    """
    Move the specified file to the trash bin.

    :param file_path: Path to the file to be moved to trash.
    """
    system = platform.system()

    if system == 'Linux':
        trash_path = os.path.expanduser('~/.local/share/Trash/files/')
        if not os.path.exists(trash_path):
            os.makedirs(trash_path)
        shutil.move(file_path, trash_path)
    elif system == 'Darwin':  # macOS
        osascript_command = f'tell application "Finder" to delete POSIX file "{file_path}"'
        subprocess.run(['osascript', '-e', osascript_command])
    else:
        print("Unsupported system for trash operation.")


# def apply_patches(diff_string):
#     """
#     Apply a diff string to a file using the patch utility and print a summary of operations.
#
#     :param diff_string: The diff string to apply.
#     """
#     errors = []
#
#     # Find positions of individual diffs in the diff_string
#     diff_delimiters = [match.start() for match in re.finditer(r'^--- .+\s+^\+\+\+ .+\s', diff_string, re.MULTILINE)]
#     individual_diffs = [diff_string[start:end] for start, end in zip(diff_delimiters, diff_delimiters[1:] + [None])]
#
#     for diff in individual_diffs:
#         # Extract source and target files
#         file_pair = re.search(r'^--- (.+?)\s+^\+\+\+ (.+?)\s', diff, re.MULTILINE)
#         if not file_pair:
#             print("Failed to extract file paths from diff string.")
#             continue
#
#         source_file, target_file = file_pair.groups()
#
#         # Handle new file creation
#         if source_file == '/dev/null':
#             with open(target_file, 'w') as new_file:
#                 new_file_contents = re.sub(r'^\+','', diff, flags=re.MULTILINE)
#                 new_file.write(new_file_contents)
#             print(f"|- New file created: {target_file}")
#
#         # Handle file deletion
#         elif target_file == '/dev/null':
#             move_to_trash(source_file)
#             print(f"|- File moved to trash: {source_file}")
#
#         # Apply the diff using the patch command
#         try:
#             process = subprocess.run(['patch', '-p1'], input=diff, text=True, check=True)
#             print(f"|- Patch applied to {target_file}")
#
#         except subprocess.CalledProcessError as e:
#             print(f"|- Failed to apply patch to {file}. type /error to print errors.")
#             errors.append(traceback.format_exc())
#
#         # Handle file rename
#         if source_file != target_file and source_file != '/dev/null' and target_file != '/dev/null':
#             print(f"|- Renamed {source_file} to {target_file}")
#
#     return errors

# [Example diff string and function call]


def extract_backtick_sections(raw):
    """
    Extract sections enclosed in triple backticks from the given string.

    :param raw: The input string containing triple backtick sections.
    :return: A list of tuples, where each tuple contains the rest of the line
             after the opening backticks and the content within the backticks.
    """
    pattern = r'```([^\n]*)\n(.*?)```'
    matches = re.findall(pattern, raw, re.DOTALL)
    return matches



custom_diff_prompt = """
[[TASK]]
We have just discussed file modifications
You are going to output diffs to apply the changes that we just discussed.

You are going to follow these steps exactly:
    1. Output a bulletted list of names of each of the files that need a patch.
        - You will always print out the complete file path.
    2. Iterate over each of the file names and print out a bulletted list of changes.
    3. Iterate over each file and output 1 or more diffs. For each diff:
        a. Print out <<START DIFF>>
        b. Print out the diff in the Custom Diff Format, described below.
        c. Print out <<END DIFF>>

[[GLOSSARY]]
Custom Diff Format:
    Like Unified Diff Format:
        1.  Lines that are added must begin with a +
        2.  Lines that are dropped must begin with a -
    Unlike Unified Diff Format:
    	1.	File Modification Times Omitted: the Custom Diff Format does not include timestamps of file modifications.
    	2.	Description Inside @@: Inside the @@ markers, a brief description of the change is provided instead of line numbers.
    	3.	Contextual Lines: Include a few lines of context around the changes, as much as necessary to make the changes clear and understandable.

[[EXAMPLE OUTPUT]]
1. Files that need a patch:
    - /config/logging.conf
    - /config/database.yml
    - /path/to/file3.py

2. Changes to these files:
    - /config/logging.conf
        - Modify log level from info to debug
        - Enable file logging
    - /config/database.yml
        - Update database host address
        - Change maximum pool size
    - /config/roles.ini
        - Add new admin role

3. Diffs for these files:

<<START DIFF>>
--- /config/logging.conf
+++ /config/logging.conf
@@ Modify log level from info to debug @@
 # Configuration of log levels
 # Increasing verbosity for troubleshooting

-log_level=info
+log_level=debug
 # Please review the levels accordingly

@@ Enable file logging @@
 # File logging setup
 # Activating logging to file for better issue tracking

-file_logging=disabled
+file_logging=enabled
 # Log files location: /var/log/app
<<END DIFF>>

<<START DIFF>>
--- /config/database.yml
+++ /config/database.yml
@@ Update database host address @@
 # Database connection settings
 # Host changed due to server migration

-host=db.example.com
+host=newdb.example.com
 # Port remains unchanged
@@ Change maximum pool size @@
 # Pool settings
 # Adjusting maximum pool size for performance optimization

-max_pool_size=10
+max_pool_size=20
 # Monitor performance post-change
<<END DIFF>>

<<START DIFF>>
--- /config/roles.ini
+++ /config/roles.ini
@@ Add new admin role @@
 # User roles configuration
 # Adding new role for better access control

+[admin]
+access_level=high
+permissions=modify, delete, create
 # Ensure proper role assignments
<<END DIFF>>
"""

unified_diff_prompt = """
[[TASK]]
You are going to produce a diff in the Unified Diff Format.
You will be given 2 items, a custom diff description, and the file with line numbers.

[[GLOSSARY]]
Unified Diff Format
    - Key Concerns:
    	1.	”+” (plus sign): Indicates a line that has been added to a file. Lines prefixed with a “+” are new or modified lines in the new version of the file.
        2.	”-” (minus sign): Signifies a line that has been removed from the file. Lines prefixed with a “-” are those that were present in the old version but have been deleted in the new version.

[[EXAMPLE INPUT]]

```/config/logging.conf
1	# Configuration of log levels
2	# Increasing verbosity for troubleshooting
3
4	log_level=info
5	# Please review the levels accordingly
6
7	# File logging setup
8	# Activating logging to file for better issue tracking
9
10	file_logging=disabled
11	# Log files location: /var/log/app
```

```diff
@@ Modify log level from info to debug @@
 # Configuration of log levels
 # Increasing verbosity for troubleshooting

-log_level=info
+log_level=debug
 # Please review the levels accordingly

@@ Enable file logging @@
 # File logging setup
 # Activating logging to file for better issue tracking

-file_logging=disabled
+file_logging=enabled
 # Log files location: /var/log/app
```

[[EXAMPLE OUTPUT]]
Here is a diff for this file in Unified Diff Format:

<<START DIFF>
--- original
+++ modified
@@ -4,1 +4,1 @@
-log_level=info
+log_level=DEBUG
@@ -10,1 +10,1 @@
-file_logging=disabled
+file_logging=enabled
<END DIFF>
"""

def generate_delete_diff(file):
    return f"""
--- {file}
+++ /dev/null
"""

def extract_diffs(extract_response):
    """
    Extract diff strings from the extract_response.

    :param extract_response: The response string containing diffs enclosed in <<START DIFF>> and <<END DIFF>>.
    :return: A list of diff strings.
    """
    pattern = r'<<START DIFF>>(.*?)<<END DIFF>>'
    matches = re.findall(pattern, extract_response, re.DOTALL)
    return matches


def apply_cli(session):
    print('|- Entering /apply mode..')

    # Fork session for delta extraction
    custom_session = session.fork(constraints=[custom_diff_prompt])
    custom_prompt = "Generate the diffs based on the recent conversation history."

    # Extract diffs
    custom_response = ""
    for chunk in custom_session.call(custom_prompt):
        content = chunk['choices'][0]['delta']['content']
        if content is None:
            break
        custom_response += content
        print(content, end='', flush=True)

    custom_diffs = extract_diffs(custom_response)

    # Convert custom diffs to unified diffs
    unified_diffs = []
    for c, custom_diff in enumerate(custom_diffs):
        print(f"\n|- [{c}] Generating diff in Unified Diff Format")
        # unified_diff = build_unified_diff(custom_diff)
        # unified_diffs.append(unified_diff)
        # print(unified_diff)

        # Extract source and target files
        file_pair = re.search(r'^--- (.+?)\s+^\+\+\+ (.+?)\s', custom_diff, re.MULTILINE)
        if not file_pair:
            print("Failed to extract file paths from custom diff string.")
            continue

        source_file, target_file = file_pair.groups()

        if target_file == '/dev/null':
            unified_diffs.append(generate_delete_diff(source_file))

        else:
            unified_session = session.fork(constraints=[unified_diff_prompt])
            unified_prompt = file_to_string(source_file, line_numbers=True) + '\n\n' + custom_diff

            # Extract diffs
            unified_response = ""
            for chunk in unified_session.call(unified_prompt):
                content = chunk['choices'][0]['delta']['content']
                if content is None:
                    break
                unified_response += content
                print(content, end='', flush=True)

            formatted_diffs = [
                diff.replace(
                    '--- original', f'--- {source_file}'
                ).replace(
                    '+++ modified', f'--- {target_file}'
                ) for diff in extract_diffs(unified_response)
            ]
            unified_diffs.extend(formatted_diffs)

    while True:
        user_input = input("\n|> ")

        if user_input.startswith('/apply'):
            args = user_input.split(' ')[1:]
            if not args:
                for diff in unified_diffs:
                    apply_patch(diff)
                    return
            else:
                for arg in args:
                    apply_patch(diffs[int(arg)])
                    continue

        # elif user_input.startswith('/drop'):
        #     args = user_input.split()[1:]
        #     if not args:
        #         diffs = []
        #     else:
        #         for arg in sorted(args, reverse=True):
        #             del diffs[int(arg)]

        elif user_input == '/cancel':
            print('|- Exiting diff mode..')
            return

        else:
            for chunk in custom_session.call(user_input):
                content = chunk['choices'][0]['delta']['content']
                if content is None:
                    break
                delta_response += content
                print(content, end='', flush=True)


def apply_patch(diff_string):
    """
    Apply a diff string to a file using the patch utility and print a summary of operations.

    :param diff_string: The diff string to apply.
    """
    errors = []

    # Apply the diff using the patch command
    try:
        process = subprocess.run(['patch', '-p1'], input=diff_string, text=True, check=True)
        print(f"\n|- Patch applied successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\n|- Failed to apply patch:")
        print(diff_string)
        trace = traceback.format_exc()
        errors.append(trace)
        print(trace)

    return errors
