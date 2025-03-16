from action import Output

lock_info = Output(
    name='lock-info',
    type='string',
    description='''
When the job outcome is `failure` and the failure-reason is `state-locked`, this output will be set.

It is a json object containing any available state lock information and typically has the form:

```json
{
  "ID": "838fbfde-c5cd-297f-84a4-d7578b4a4880",
  "Path": "terraform-github-actions/test-unlock-state",
  "Operation": "OperationTypeApply",
  "Who": "root@e9d43b0c6478",
  "Version": "1.3.7",
  "Created": "2023-01-28 00:16:41.560904373 +0000 UTC",
  "Info": ""
}
```
'''
)
