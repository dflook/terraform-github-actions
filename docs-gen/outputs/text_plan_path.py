from action import Output

text_plan_path = Output(
    name='text_plan_path',
    type='string',
    description='''
This is the path to the generated plan in a human-readable format.
The path is relative to the Actions workspace.
'''
)
