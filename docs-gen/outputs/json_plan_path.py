from action import Output

json_plan_path = Output(
    name='json_plan_path',
    type='string',
    description='''
This is the path to the generated plan in [JSON Output Format]($JsonFormatUrl).
The path is relative to the Actions workspace.

$ProductName plans often contain sensitive information, so this output should be treated with care.
'''
)
