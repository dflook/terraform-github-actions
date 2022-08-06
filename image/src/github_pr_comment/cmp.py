import re


def remove_unchanged_attributes(plan: str) -> str:
    """
    Remove unchanged attribute comments from plan text
    """

    return '\n'.join(line for line in plan.splitlines() if not re.match(r'\s+# \(\d+ unchanged attributes hidden\)', line)).strip()

def remove_warnings(plan: str) -> str:
    """
    Remove warnings from the plan text
    """

    plan_lines = []

    plan_summary_reached = False

    for line in plan.splitlines():
        if plan_summary_reached and (line.startswith('Warning') or line.startswith('╷')):
            break

        plan_lines.append(line)

        if re.match(r'Plan: \d+ to add, \d+ to change, \d+ to destroy', line):
            plan_summary_reached = True

    return '\n'.join(plan_lines).strip()

def plan_cmp(a: str, b: str) -> bool:
    return a.strip() == b.strip()
