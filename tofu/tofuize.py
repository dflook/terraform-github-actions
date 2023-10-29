#!/usr/bin/python3
import re
import shutil
from pathlib import Path
from typing import Iterable


def find_actions(d) -> Iterable[Path]:
    for path in d.iterdir():
        if path.name.startswith('terraform-') and path.is_dir():
            yield path

def rewrite(content: str) -> str:
    rewritten = re.sub(r'(?<!hashicorp\.com/)(?<!\.)(?<!-)(?<!\* `)terraform(?!-github-actions|\.io|\.workspace|-switcher|.html)', 'tofu', content)
    rewritten = re.sub(r'(?<!Hashicorp )Terraform', 'OpenTofu', rewritten)
    rewritten = re.sub(r' a OpenTofu', ' an OpenTofu', rewritten)
    return rewritten

def insert_env(content:str) -> Iterable[str]:
    for line in content.splitlines():
        if line.startswith('runs:'):
            yield line
            yield '  env:'
            yield '    OPENTOFU: true'
        else:
            yield line

def tofuize_action(action: Path):
    tofu_name = action.name.replace('terraform', 'tofu')
    tofu_dir = action.parent / tofu_name

    if tofu_dir.exists():
        shutil.rmtree(tofu_dir, ignore_errors=True)

    tofu_dir.mkdir()

    # copy files
    for path in action.iterdir():
        if not path.is_file():
            continue

        tofu_path = tofu_dir / path.name

        if path.name == 'README.md':
            tofu_path.write_text(rewrite(path.read_text()))
        elif path.name == 'action.yaml':
            metadata = rewrite(path.read_text())
            tofu_path.write_text('\n'.join(insert_env(metadata)) + '\n')
        else:
            shutil.copy(path, tofu_path)

def tofuize():
    for action in find_actions(Path('.')):
        print(action)
        tofuize_action(action)



if __name__ == '__main__':
    tofuize()
