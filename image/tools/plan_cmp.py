#!/usr/bin/env python3

import sys

with open(sys.argv[1], encoding='utf-8') as f:
    first = f.read()
with open(sys.argv[2], encoding='utf-8') as f:
    second = f.read()
exit(0 if first.strip() == second.strip() else 1)
