from action import Output

json_output_path = Output(
    name='json_output_path',
    type='string',
    description='''
This is the path to all the root module outputs in a JSON file.
The path is relative to the Actions workspace.

For example, with the $ProductName config:

```hcl
output "service_hostname" {
  value = "example.com"
}
```

The file pointed to by this output will contain:

```json
{
  "service_hostname": "example.com"
}
```

$ProductName list, set and tuple types are cast to a JSON array, map and object types are cast to a JSON object.
'''
)
