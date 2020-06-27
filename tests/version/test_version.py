from convert_version import convert_version

def test_convert_version():
    tf_version_output = 'Terraform v0.12.28'
    expected = [
        '::set-output name=terraform::0.12.28'
    ]

    assert list(convert_version(tf_version_output)) == expected

def test_convert_old_version():
    tf_version_output = 'Terraform v0.11.14'
    expected = [
        '::set-output name=terraform::0.11.14'
    ]

    assert list(convert_version(tf_version_output)) == expected

def test_convert_with_provider():
    tf_version_output = '''Terraform v0.12.28
+ provider.random v2.2.0'''

    expected = [
        '::set-output name=terraform::0.12.28',
        '::set-output name=random::2.2.0'
    ]

    assert list(convert_version(tf_version_output)) == expected

def test_convert_with_multiple_providers():
    tf_version_output = '''Terraform v0.12.28
+ provider.acme v1.5.0
+ provider.random v2.2.0
'''

    expected = [
        '::set-output name=terraform::0.12.28',
        '::set-output name=acme::1.5.0',
        '::set-output name=random::2.2.0'
    ]

    assert list(convert_version(tf_version_output)) == expected
