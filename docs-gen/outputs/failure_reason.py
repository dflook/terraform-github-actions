from action import Output

failure_reason = Output(
    name='failure-reason',
    type='string',
    description='''
      When the job outcome is `failure` because of a known reason, this will be set to that reason.
      If the job fails for any other reason this will not be set.
      This can be used with the Actions expression syntax to conditionally run a steps.
    '''
)
