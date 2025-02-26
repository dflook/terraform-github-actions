from action import Output

changes = Output(
    name='changes',
    type='boolean',
    description='''
Set to 'true' if the plan would apply any changes, 'false' if it wouldn't.
'''
)
