
diff_prompt = """
Before this message was
Generate the diffs based on the recent conversation history.
Your outputs should be in the Unified Diff Format.
"""


def apply_cli(ui, session):
    ui.print_info('Entering /apply mode..')

    # Fork session for delta extraction
    session = session.fork(model='gpt-4o-mini')
    session.append_system_message(diff_prompt)

    # Extract diffs
    response = ""
    for chunk in session.call(custom_prompt):
        content = chunk['choices'][0]['delta']['content']
        if content is None:
            break
        response += content
        print(content, end='', flush=True)

    custom_diffs = extract_diffs(response)

    # Convert custom diffs to unified diffs
    unified_diffs = []
    for c, custom_diff in enumerate(custom_diffs):
        ui.print_info(f"[{c}] Generating diff in Unified Diff Format")
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
            for chunk in session.call(user_input):
                content = chunk['choices'][0]['delta']['content']
                if content is None:
                    break
                delta_response += content
                print(content, end='', flush=True)


def apply_unified_diff(diff_text, target_file_path):
    """
    Apply a unified diff to a target file.

    :param diff_text: The diff text in unified diff format.
    :param target_file_path: Path to the target file to apply the diff.
    """
    import os
    from unidiff import PatchSet

    # Read the original file content
    if os.path.exists(target_file_path):
        with open(target_file_path, 'r') as file:
            original_content = file.read()
    else:
        original_content = ''

    # Create a PatchSet object from the diff text
    patch = PatchSet(diff_text)

    # Find the patch that applies to the target file
    for patched_file in patch:
        if os.path.basename(patched_file.path) == os.path.basename(target_file_path):
            # Apply the patch to the original content
            original_lines = original_content.splitlines(keepends=True)
            patched_lines = apply_patch_to_lines(patched_file, original_lines)

            # Write the patched content back to the target file
            with open(target_file_path, 'w') as file:
                file.writelines(patched_lines)
            break
    else:
        raise ValueError("No matching file in diff for the target file.")

def apply_patch_to_lines(patched_file, original_lines):
    """
    Apply patches from a patched file to the original lines.

    :param patched_file: The patched file object from unidiff.
    :param original_lines: List of original lines.
    :return: List of patched lines.
    """
    patched_lines = original_lines[:]
    line_offset = 0

    for hunk in patched_file:
        hunk_start = hunk.source_start - 1 + line_offset
        hunk_end = hunk_start + hunk.source_length

        # Remove lines to be deleted
        del patched_lines[hunk_start:hunk_end]

        # Insert new lines
        new_lines = [line.value for line in hunk if line.is_added or line.is_context]
        for i, line in enumerate(new_lines):
            patched_lines.insert(hunk_start + i, line)

        # Update line offset
        line_offset += hunk.target_length - hunk.source_length

    return patched_lines
