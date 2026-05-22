import hashlib
import json
from pathlib import Path

import canonicaljson

from github_actions.debug import debug
from github_pr_comment.cmp import remove_warnings, remove_unchanged_attributes


def comment_hash(value: bytes, salt: str) -> str:
    h = hashlib.sha256(f'dflook/terraform-github-actions/{salt}'.encode())
    h.update(value)
    return h.hexdigest()


def plan_json_hash(json_plan_path: Path, salt: str) -> str:
    """
    Compute a deterministic hash of the plan using the JSON plan output.

    Excluded volatile fields:
    - timestamp: generated fresh on every plan run, carries no information about what will change
    """

    debug(f'Hashing JSON plan {json_plan_path} with salt {salt}')

    with open(json_plan_path) as f:
        plan = json.load(f)

    plan.pop('timestamp', None)

    return comment_hash(canonicaljson.encode_canonical_json(plan), salt)


def plan_hash(plan_text: str, salt: str) -> str:
    """
    Compute a hash of the plan text.

    Legacy function retained for backward compatibility with PR comments that were created
    before JSON-based hashing was introduced. Use plan_json_hash where possible.
    """

    debug(f'Hashing plan text with salt {salt}')

    plan = remove_warnings(remove_unchanged_attributes(plan_text))

    return comment_hash(plan.encode(), salt)

def plan_out_hash(plan_path: str, salt: str) -> str:
    """
    Compute a sha256 hash of the binary plan file
    """

    debug(f'Hashing {plan_path} with salt {salt}')

    h = hashlib.sha256(f'dflook/terraform-github-actions/{salt}'.encode())

    with open(plan_path, 'rb') as f:
        while data := f.read(65536):
            h.update(data)

    return h.hexdigest()
