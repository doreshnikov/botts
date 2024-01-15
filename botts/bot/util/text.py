def escape_md(s: str):
    return (s
            .replace('_', '\\_')
            .replace('*', '\\*')
            .replace('[', '\\[')
            .replace('`', '\\`')
            .replace('-', '\\-'))
