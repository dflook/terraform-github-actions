from action import Output



terraform_outputs = Output(
    name='$ProductName Outputs',
    meta_output=True,
    description='''
An action output will be created for each output of the $ProductName configuration.

For example, with the $ProductName config:

```hcl
output "service_hostname" {
  value = "example.com"
}
```

Running this action will produce a `service_hostname` output with the value `example.com`.

### Primitive types (string, number, bool)

The values for these types get cast to a string with boolean values being 'true' and 'false'.

### Complex types (list/set/tuple & map/object)

The values for complex types are output as a JSON string. $ProductName `list`, `set` & `tuple` types are cast to a JSON array, `map` and `object` types are cast to a JSON object.

These values can be used in a workflow expression by using the [fromJSON](https://docs.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions#fromjson) function
'''
)
