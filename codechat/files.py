import os
from core.utils.files import crawl_files
from .config import config


def find_nearest_parent_timestamp(path, timestamps):
    """Find the timestamp of the nearest parent directory in the timestamps dictionary."""
    while path != os.path.dirname(path):  # Check until the root directory is reached
        if path in timestamps:
            return timestamps[path]
        path = os.path.dirname(path)
    return timestamps.get(path, 0)  # Default to 0 if no parent timestamp is found


def has_file_been_updated_since(file_path, timestamp):
    """Check if the file has been modified since the timestamp in the timestamps dict."""
    if not os.path.isfile(file_path):
        return False
    file_mod_time = os.path.getmtime(file_path)
    return file_mod_time > timestamp


def get_updated_files_in(paths, timestamps, default_timestamp=0, exclusion_files=['.gitignore', '.gptignore'], exclusion_rules=set(config['exclude'])):
    """Get a list of files in the given paths that have been updated since their respective timestamps."""
    updated_items = []

    for path in paths:
        path_timestamp = timestamps.get(path, default_timestamp)
        if os.path.isdir(path):
            files = crawl_files(path, exclusion_files=exclusion_files, exclusion_rules=exclusion_rules)
            for file_path in files:
                file_timestamp = timestamps.get(file_path, path_timestamp)  # Use file's timestamp or default to path's timestamp
                if has_file_been_updated_since(file_path, file_timestamp):
                    updated_items.append(file_path)
        elif os.path.isfile(path):
            file_timestamp = timestamps.get(path, default_timestamp)
            if has_file_been_updated_since(path, file_timestamp):
                updated_items.append(path)
    return updated_items


def file_to_string(file_path, line_numbers=False):
    """Convert a file's content to a string with the specified format."""
    if not os.path.isfile(file_path):
        print(file_path)
        return ""

    with open(file_path, 'r') as file:
        try:
            content = file.readlines()
        except UnicodeDecodeError:
            content = []

    if line_numbers:
        content = [f"{i + 1}\t{line}" for i, line in enumerate(content)]

    return f"\n```{file_path}\n{''.join(content)}\n```\n"


def get_file_content(file_path):
    """Retrieve the content of a file."""
    if not os.path.isfile(file_path):
        return ""

    with open(file_path, 'r') as file:
        try:
            content = file.read()
        except UnicodeDecodeError:
            content = ""

    return content


def get_files_content(paths, exclusion_files=['.gitignore', '.gptignore'], exclusion_rules=set(config['exclude']), line_numbers=False):
    """Get the content of files in the specified format with .gptassert integration."""
    all_files = []
    for path in paths:
        files = crawl_files(path, exclusion_files=exclusion_files, exclusion_rules=exclusion_rules)
        all_files.extend(files)

    if not all_files:
        return ""

    output = ""
    cwd = os.path.abspath('.')

    processed_dirs = set()

    for file_path in all_files:
        abs_file_path = os.path.abspath(file_path)
        dir_path = os.path.dirname(abs_file_path)

        assert_blocks = []

        # Traverse from file's directory up to the root directory
        current_dir = dir_path
        while True:
            if current_dir in processed_dirs:
                # Already processed this directory for assertions
                current_dir = os.path.dirname(current_dir)
                if current_dir == os.path.dirname(current_dir):
                    break
                continue

            gptassert_path = os.path.join(current_dir, '.gptassert')
            if os.path.isfile(gptassert_path):
                try:
                    with open(gptassert_path, 'r') as assert_file:
                        assert_content = assert_file.read().strip()
                    # Calculate relative path from cwd
                    relative_path = os.path.relpath(current_dir, cwd)
                    if relative_path == '.':
                        relative_path = './'
                    else:
                        relative_path = f"./{'/'.join(relative_path.split(os.sep))}/"

                    assert_block = f"<<<ASSERT {relative_path}>>>\n{assert_content}\n<<<//ASSERT>>>"
                    assert_blocks.append(assert_block)
                except Exception as e:
                    # If there's an error reading the .gptassert file, skip it
                    print(f"Warning: Could not read {gptassert_path}: {e}")

                # Mark this directory as processed
                processed_dirs.add(current_dir)

            # Move up one directory level
            parent_dir = os.path.dirname(current_dir)
            if current_dir == parent_dir:
                # Reached the root directory
                break
            current_dir = parent_dir

        # Begin DIR block
        relative_dir_path = os.path.relpath(dir_path, cwd)
        if relative_dir_path == '.':
            relative_dir_path = './'
        else:
            relative_dir_path = f"./{'/'.join(relative_dir_path.split(os.sep))}/"
        output += f"\n<<<DIR {relative_dir_path}>>>"

        # Add all ASSERT blocks collected
        for assert_block in assert_blocks:
            output += f"\n{assert_block}"

        # Begin FILE block
        relative_file_path = os.path.relpath(file_path, cwd)
        relative_file_path = f"./{'/'.join(relative_file_path.split(os.sep))}"
        file_extension = os.path.splitext(file_path)[1][1:].lower()  # e.g., 'py', 'js'

        output += f"\n<<<FILE {relative_file_path}>>>"
        output += f"\n<<<TYPE {file_extension} //>>>"
        output += f"\n<<<CONTENT>>>"

        # Get file content
        file_content = get_file_content(file_path)
        output += f"\n{file_content}\n<<<//CONTENT>>>\n<<<//FILE>>>"

        # Close DIR block
        output += f"\n<<<//DIR>>>"

    return output

def display_files(
    paths, exclusion_files=['.gitignore', '.gptignore'], exclusion_rules=set(config['exclude'])
):
    """Display the structure of the files and directories in a tree format."""
    # Get all files using crawl_files
    all_files = []
    for path in paths:
        files = crawl_files(path, exclusion_files=exclusion_files, exclusion_rules=exclusion_rules)
        all_files.extend(files)

    if not all_files:
        return

    # Build tree structure
    import collections
    Tree = lambda: collections.defaultdict(Tree)
    file_tree = Tree()

    for file_path in all_files:
        rel_path = os.path.relpath(file_path, start='.')
        parts = rel_path.split(os.sep)
        subtree = file_tree
        for part in parts[:-1]:
            subtree = subtree[part]
        subtree[parts[-1]] = None  # Indicate that this is a file

    # Function to print tree
    def print_tree(tree, prefix='   '):
        for key in sorted(tree.keys()):
            if tree[key]:
                print(f"{prefix}|- {key}/")
                print_tree(tree[key], prefix + "|  ")
            else:
                print(f"{prefix}|- {key}")

    print("|- Included files:")
    print_tree(file_tree)
