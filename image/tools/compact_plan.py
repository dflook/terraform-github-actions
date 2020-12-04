import sys

if __name__ == '__main__':
    plan = False
    buffer = []

    for line in sys.stdin.readlines():

        if not plan and line.startswith('---'):
            plan = True
            continue

        if not plan and (
            line.startswith('An execution plan has been generated and is shown below') or
            line.startswith('No changes') or
            line.startswith('Error')
        ):
            plan = True

        if plan:
            print(line)
        else:
            buffer.append(line)

    if not plan and buffer:
        for line in buffer:
            print(line)
