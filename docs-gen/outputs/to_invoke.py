from action import Output, Terraform

to_invoke = Output(
    name='to_invoke',
    type='number',
    description='''
The number of actions that would be invoked by the plan, using `action_trigger` lifecycle events.

Requires Terraform 1.14+.
''',
    meta_description='The number of actions that would be invoked by this operation.',
    available_in=[Terraform]
)
