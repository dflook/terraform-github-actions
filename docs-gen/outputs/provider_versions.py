from action import Output

provider_versions = Output(
    name='Provider Versions',
    meta_output=True,
    type='string',
    description='''
      Additional outputs are added with the version of each provider that
      is used by the $ProductName configuration. For example, if the random
      provider is used:
    
      ```hcl
      provider "random" {
        version = "2.2.0"
      }
      ```
    
      A `random` output will be created with the value `2.2.0`.
    '''
)
