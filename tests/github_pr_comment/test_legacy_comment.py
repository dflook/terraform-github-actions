"""
These test verify that _from_api_payload continues to correctly match pre-existing comments, without headers
"""

import random
import string

from github_pr_comment.comment import TerraformComment, _from_api_payload

plan = '''An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.'''

issue_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))
comment_url = ''.join(random.choice(string.ascii_letters) for _ in range(10))

def test_path_only():
    payload = '''Terraform plan in __/test/terraform__
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='Terraform plan in __/test/terraform__',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_nondefault_workspace():
    payload = '''Terraform plan in __/test/terraform__ in the __myworkspace__ workspace
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='Terraform plan in __/test/terraform__ in the __myworkspace__ workspace',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_variables_single_line():
    payload = '''Terraform plan in __/test/terraform__
With variables: `var1="value"`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''


    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='Terraform plan in __/test/terraform__\nWith variables: `var1="value"`',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_variables_multi_line():
    payload = '''Terraform plan in __/test/terraform__<details><summary>With variables</summary>

```hcl
var1="value"
var2="value2"
```
</details>

<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan in __/test/terraform__<details><summary>With variables</summary>

```hcl
var1="value"
var2="value2"
```
</details>''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_var():
    payload = '''Terraform plan in __/test/terraform__
With vars: `var1=value`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan in __/test/terraform__
With vars: `var1=value`''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_var_file():
    payload = '''Terraform plan in __/test/terraform__
With var files: `vars.tf`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan in __/test/terraform__
With var files: `vars.tf`''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_backend_config():

    payload = '''Terraform plan in __/test/terraform__
With backend config: `bucket=test,key=backend`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan in __/test/terraform__
With backend config: `bucket=test,key=backend`''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_backend_config_bad_words():
    payload = '''Terraform plan in __/test/terraform__
With backend config: `bucket=test,key=backend`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan in __/test/terraform__
With backend config: `bucket=test,key=backend`''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected

def test_target():
    payload = '''Terraform plan in __/test/terraform__
Targeting resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan in __/test/terraform__
Targeting resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected

def test_replace():
    payload = '''Terraform plan in __/test/terraform__
Replacing resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan in __/test/terraform__
Replacing resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_backend_config_file():
    payload = '''Terraform plan in __/test/terraform__
With backend config files: `backend.tf`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan in __/test/terraform__
With backend config files: `backend.tf`''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_all():
    payload = '''Terraform plan in __/test/terraform__ in the __test__ workspace
Targeting resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
Replacing resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
With backend config: `bucket=mybucket`
With backend config files: `backend.tf`
With vars: `myvar=hello`
With var files: `vars.tf`
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan in __/test/terraform__ in the __test__ workspace
Targeting resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
Replacing resources: `kubernetes_secret.tls_cert_public[0]`, `kubernetes_secret.tls_cert_private`
With backend config: `bucket=mybucket`
With backend config files: `backend.tf`
With vars: `myvar=hello`
With var files: `vars.tf`''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected


def test_label():
    payload = '''Terraform plan for __test_label__
<details open>
<summary>Plan: 1 to add, 0 to change, 0 to destroy.</summary>

```hcl
An execution plan has been generated and is shown below.
...
Plan: 1 to add, 0 to change, 0 to destroy.
```
</details>

Testing'''

    expected = TerraformComment(
        issue_url=issue_url,
        comment_url=comment_url,
        status='Testing',
        headers={},
        description='''Terraform plan for __test_label__''',
        summary='Plan: 1 to add, 0 to change, 0 to destroy.',
        body=plan
    )

    assert _from_api_payload({
        'body': payload,
        'url': comment_url,
        'issue_url': issue_url
    }) == expected
