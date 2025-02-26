from action import Output

run_id = Output(
    name='run_id',
    type='string',
    description='''
If the root module uses the `remote` or `cloud` backend in remote execution mode, this output will be set to the remote run id.
'''
)
