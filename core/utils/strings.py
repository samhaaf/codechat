import re

def tab_left(text, indents=None, spaces=None):
    if indents is None and spaces is None:
        spaces = 4
    elif indents is not None:
        assert spaces is None, 'Ambiguous request where spaces and indents given'
        spaces = 4 * indents
    indent_str = ' ' * spaces
    lines = text.split('\n')
    indented_lines = [indent_str + line for line in lines]
    indented_text = '\n'.join(indented_lines)
    return indented_text


def match_patterns(test_string, patterns):
    """Test if the test_string matches any of the strings or regex patterns in the list,
       using a prefix in the pattern to indicate its type ('r:' for regex and 'l:' for literals)."""
    matches = []
    for pattern in patterns:
        if pattern.startswith('r:'):
            # It's a regex pattern
            regex = pattern[2:]  # Remove the 'r:' prefix
            if re.search(regex, test_string):
                matches.append(pattern)
        else:
            if pattern == test_string:
                matches.append(pattern)
    return matches
