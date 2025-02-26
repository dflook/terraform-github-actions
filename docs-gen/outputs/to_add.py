from action import Output

to_add = Output(
    name='to_add',
    type='number',
    description='''
The number of resources that would be affected by each type of operation.
''',
    meta_description='The number of resources that would be affected by this operation.',
    aliases=['to_change', 'to_destroy', 'to_move', 'to_import']
)
