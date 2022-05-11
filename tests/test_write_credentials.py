from format_tf_credentials import format_credentials


def test_single_cred():
    input = """app.terraform.io=xxxxxx.atlasv1.zzzzzzzzzzzzz"""

    expected_output = """credentials "app.terraform.io" {
  token = "xxxxxx.atlasv1.zzzzzzzzzzzzz"
}
"""

    output = ''.join(format_credentials(input))
    assert output == expected_output

def test_multiple_creds():
    input = """
    
    app.terraform.io=xxxxxx.atlasv1.zzzzzzzzzzzzz
    
terraform.example.com=abcdefg        

"""

    expected_output = """credentials "app.terraform.io" {
  token = "xxxxxx.atlasv1.zzzzzzzzzzzzz"
}
credentials "terraform.example.com" {
  token = "abcdefg"
}
"""

    output = ''.join(format_credentials(input))
    assert output == expected_output

def test_unrecognised_lines():
    input = """
    
    app.terraform.io=xxxxxx.atlasv1.zzzzzzzzzzzzz    
    
    This doesn't look anything like a credential
    
    """

    try:
        output = ''.join(format_credentials(input))
    except ValueError as e:
        pass
    else:
        assert False, 'Should have raised an exception'
