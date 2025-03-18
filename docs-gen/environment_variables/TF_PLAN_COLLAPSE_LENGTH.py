from action import EnvVar

TF_PLAN_COLLAPSE_LENGTH = EnvVar(
    name='TF_PLAN_COLLAPSE_LENGTH',
    type='integer',
    default='10',
    description='''
When PR comments are enabled, the $ToolName output is included in a collapsable pane.
  
If a $ToolName plan has fewer lines than this value, the pane is expanded
by default when the comment is displayed.

```yaml

env:
  TF_PLAN_COLLAPSE_LENGTH: 30
```
'''
)
