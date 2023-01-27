from lock_info.__main__ import get_lock_info

def test_not_locked():
    err = '''
Something went wrong
Really wrong
'''

    assert get_lock_info(err.splitlines()) is None

def test_no_lock_info():
    err = '''
Error: Error acquiring the state lock

Error message: ConditionalCheckFailedException: The conditional request
failed

Terraform acquires a state lock to protect the state from being written
by multiple users at the same time. Please resolve the issue above and try
again. For most commands, you can disable locking with the "-lock=false"
flag, but this is not recommended.
'''

    assert get_lock_info(err.splitlines()) == {}

def test_locked_1_3_7():
    err = '''
Error: Error acquiring the state lock

Error message: ConditionalCheckFailedException: The conditional request
failed
Lock Info:
  ID:        82bb6a6a-3286-30f7-99cd-7831a1c98b9f
  Path:      terraform-github-actions/test-unlock-state
  Operation: OperationTypeApply
  Who:       root@93367e6dabee
  Version:   1.3.7
  Created:   2023-01-11 19:38:18.347143348 +0000 UTC
  Info:      


Terraform acquires a state lock to protect the state from being written
by multiple users at the same time. Please resolve the issue above and try
again. For most commands, you can disable locking with the "-lock=false"
flag, but this is not recommended.
'''

    expected_info = {
        'ID': '82bb6a6a-3286-30f7-99cd-7831a1c98b9f',
        'Path': 'terraform-github-actions/test-unlock-state',
        'Operation': 'OperationTypeApply',
        'Who': 'root@93367e6dabee',
        'Version': '1.3.7',
        'Created': '2023-01-11 19:38:18.347143348 +0000 UTC',
        'Info': ''
    }

    assert get_lock_info(err.splitlines()) == expected_info

def test_locked_0_12_0():
    err = '''
Error: Error locking state: Error acquiring the state lock: ConditionalCheckFailedException: The conditional request failed
	status code: 400, request id: B3NKKUK0A441HQM14MR3ACJ6BFVV4KQNSO5AEMVJF66Q9ASUAAJG
Lock Info:
  ID:        82bb6a6a-3286-30f7-99cd-7831a1c98b9f
  Path:      terraform-github-actions/test-unlock-state
  Operation: OperationTypeApply
  Who:       root@93367e6dabee
  Version:   1.3.7
  Created:   2023-01-11 19:38:18.347143348 +0000 UTC
  Info:      


Terraform acquires a state lock to protect the state from being written
by multiple users at the same time. Please resolve the issue above and try
again. For most commands, you can disable locking with the "-lock=false"
flag, but this is not recommended.


'''

    expected_info = {
        'ID': '82bb6a6a-3286-30f7-99cd-7831a1c98b9f',
        'Path': 'terraform-github-actions/test-unlock-state',
        'Operation': 'OperationTypeApply',
        'Who': 'root@93367e6dabee',
        'Version': '1.3.7',
        'Created': '2023-01-11 19:38:18.347143348 +0000 UTC',
        'Info': ''
    }

    assert get_lock_info(err.splitlines()) == expected_info