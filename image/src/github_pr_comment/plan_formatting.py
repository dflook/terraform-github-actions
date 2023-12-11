import re

def format_diff(plan_text: str) -> str:
    lines = []

    heredoc = False

    for line in plan_text.splitlines():
        if heredoc and line.lstrip().startswith('EOT'):
            heredoc = False
            lines.append(line)
            continue
        elif heredoc:
            lines.append(line)
            continue
        elif line.endswith('EOT'):
            heredoc = True
            lines.append(line)
            continue

        replaced = (re.sub(
            r'^(?P<leading_space>\s+)(?P<operation>[+-/~]+)(?P<trailing>.*)',
            '\g<operation>\g<leading_space>\g<trailing>',
            line,
            count=1
        ))

        replaced = replaced.replace('~', '!')

        replaced = re.sub(
            r'(?P<leading_space>\s+)\# (?P<trailing>\(.*hidden)',
            '#\g<leading_space>\g<trailing>',
            replaced,
            count=1
        )

        lines.append(replaced)

    return '\n'.join(lines)