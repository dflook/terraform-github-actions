import hashlib

from github_actions.debug import debug
from github_pr_comment.cmp import remove_warnings, remove_unchanged_attributes


def comment_hash(value: bytes, salt: str) -> str:
    h = hashlib.sha256(f'dflook/terraform-github-actions/{salt}'.encode())
    h.update(value)
    return h.hexdigest()


def plan_hash(plan_text: str, salt: str) -> str:
    """
    Compute a hash of the plan

    This currently uses the plan text output.
    TODO: Change to use the plan json output
    """

    debug(f'Hashing with salt {salt}')

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
