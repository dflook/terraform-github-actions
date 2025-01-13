from action import Output

tofu = Output(
    name='tofu',
    type='string',
    description='''
    If the action chose a version of OpenTofu, this will be set to the version that is used by the configuration.
    '''
)
