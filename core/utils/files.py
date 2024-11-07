import os
import re
import pathspec

DEFAULT_EXCLUSION_RULES = set([
    '**/.git/',
    '**/.gitignore',
    '**/.gptignore',
    '.gpt',
    'poetry.lock',
    "**/*.pyc",
    "**/*__pycache__",
    "**/*.pyo",
    "**/*.pyd",
    "**/*.pyc",
    "**/*.pyo",
    "**/*.pyd",
    "**/*.egg-info/",
    "**/dist/",
    "**/build/",
    "**/*.egg",
    "**/node_modules/",
    "**/npm-debug.log",
    "**/yarn-error.log",
    '**/.DS_Store',
    "**/.idea/",
    "**/.vscode/",
    "**/*.iml",
    "**/*.ipr",
    "**/*.iws",
    "**/*.suo",
    "**/*.user",
    "**/*.userosscache",
    "**/*.sln.docstates",
    "**/*.sln.ide/",
    "**/.DS_Store",
])

def crawl_files(
    path, exclusion_files=['.gitignore', '.gptignore'], exclusion_rules=set(), base_path=None
):
    if base_path is None:
        base_path = path if os.path.isdir(path) else os.path.dirname(path)
    result = []

    if os.path.isfile(path):
        # Get the directory containing the file
        dir_path = os.path.dirname(path)
        new_exclusion_rules = set(exclusion_rules)

        # Read exclusion files in the directory of the file
        for excl_file in exclusion_files:
            excl_file_path = os.path.join(dir_path, excl_file)
            if os.path.isfile(excl_file_path):
                with open(excl_file_path, 'r') as f:
                    lines = f.read().splitlines()
                    new_exclusion_rules.update(lines)

        # Prepare the pathspec object with updated exclusion rules
        spec = pathspec.PathSpec.from_lines('gitwildmatch', new_exclusion_rules)

        # Get the relative path from the base path
        relpath = os.path.relpath(path, base_path)

        if spec.match_file(relpath):
            return []
        else:
            return [path]

    elif os.path.isdir(path):
        # Read exclusion files in the current directory and update exclusion_rules
        new_exclusion_rules = set(exclusion_rules)
        for excl_file in exclusion_files:
            excl_file_path = os.path.join(path, excl_file)
            if os.path.isfile(excl_file_path):
                with open(excl_file_path, 'r') as f:
                    lines = f.read().splitlines()
                    new_exclusion_rules.update(lines)

        # Prepare the pathspec object
        spec = pathspec.PathSpec.from_lines('gitwildmatch', new_exclusion_rules)

        # List entries in the directory
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            rel_entry_path = os.path.relpath(entry_path, base_path)

            # Check if the entry matches any exclusion rules
            if spec.match_file(rel_entry_path):
                continue

            if os.path.isfile(entry_path):
                result.extend(crawl_files(entry_path, exclusion_files, new_exclusion_rules, base_path))
            elif os.path.isdir(entry_path):
                # Get subdir exclusion rules
                subdir_exclusion_rules = get_subdir_exclusion_rules(new_exclusion_rules, entry)
                result.extend(crawl_files(entry_path, exclusion_files, subdir_exclusion_rules, base_path))

        return result
    else:
        # Path does not exist
        return []

def get_subdir_exclusion_rules(exclusion_rules, subdir_name):
    subdir_exclusion_rules = set()
    for pattern in exclusion_rules:
        # Normalize the pattern by stripping leading slashes
        pattern = pattern.lstrip('/')
        components = pattern.split('/')

        if components[0] == subdir_name:
            # Pattern applies directly to subdir_name
            adjusted_pattern = '/'.join(components[1:])
            if adjusted_pattern:
                subdir_exclusion_rules.add(adjusted_pattern)
            else:
                # Pattern is exactly the subdir_name, so include everything
                subdir_exclusion_rules.add('**')
        elif components[0] == '**':
            # Pattern is recursive, could apply to subdir
            subdir_exclusion_rules.add('/'.join(components[1:]))
        elif '/' not in pattern:
            # Pattern applies to any matching files in any subdir
            subdir_exclusion_rules.add(pattern)
        else:
            # Pattern does not apply to subdir
            continue

    return subdir_exclusion_rules
