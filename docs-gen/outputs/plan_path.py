from action import Output

plan_path = Output(
    name='plan_path',
    type='string',
    description='''
This is the path to the generated plan in an opaque binary format.
The path is relative to the Actions workspace.

The plan can be used as the `plan_file` input to the [dflook/$ToolName-apply](https://github.com/dflook/terraform-github-actions/tree/main/$ToolName-apply) action.

$ProductName plans often contain sensitive information, so this output should be treated with care.
'''
)
