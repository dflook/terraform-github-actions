from action import Input

lock_id = Input(
    name='lock_id',
    type='string',
    description='The ID of the state lock to release.',
    required=True
)
