from action import Input

refresh = Input(
    name='refresh',
    type='boolean',
    description='''
Set to `false` to skip synchronisation of the $ProductName state with actual resources.

This will make the plan faster but may be out of date with the actual resources, which can lead to incorrect plans.
''',
    required=False,
    default='true'
)
