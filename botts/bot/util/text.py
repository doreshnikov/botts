_SPECIAL_CHARS = [
    '_', '*', '[', '`', '-'
]


def escape_md(s: str):
    for char in _SPECIAL_CHARS:
        s = s.replace(char, '\\' + char)
    return s
