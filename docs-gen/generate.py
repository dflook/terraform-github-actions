from action import OpenTofu, Terraform
from actions.apply import apply
from actions.check import check
from actions.destroy import destroy
from actions.destroy_workspace import destroy_workspace
from actions.fmt import fmt
from actions.fmt_check import fmt_check
from actions.new_workspace import new_workspace
from actions.output import output
from actions.plan import plan
from actions.remote_state import remote_state
from actions.test import test
from actions.unlock_state import unlock_state
from actions.validate import validate
from actions.version import version

def tofuize(str) -> str:
    return str.replace('a OpenTofu', 'an OpenTofu')

for action in [
    plan,
    apply,
    check,
    destroy,
    destroy_workspace,
    fmt,
    fmt_check,
    new_workspace,
    output,
    remote_state,
    test,
    unlock_state,
    validate,
    version

]:
    action.assert_ordering()

    for tool in [Terraform, OpenTofu]:

        print('Generating', f'{tool.ToolName}-{action.name}/README.md')
        with open(f'{tool.ToolName}-{action.name}/README.md', 'w') as f:
            f.write(tofuize(action.markdown(tool)))

        print('Generating', f'{tool.ToolName}-{action.name}/action.yml')
        with open(f'{tool.ToolName}-{action.name}/action.yaml', 'w') as f:
            f.write(tofuize(action.action_yaml(tool)))
