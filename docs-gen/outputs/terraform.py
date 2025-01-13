from action import Output

terraform = Output(
    name='terraform',
    type='string',
    description='''
    The Hashicorp Terraform or OpenTofu version that is used by the configuration.
    '''
)
