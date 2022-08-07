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
