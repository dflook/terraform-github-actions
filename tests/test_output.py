from convert_output import convert_to_github

def test_string():
    input = {
      'sensitive_string': {
        'sensitive': True,
        'type': 'string',
        'value': 'abc'
      },
      'string': {
        'sensitive': False,
        'type': 'string',
        'value': 'xyz'
      }
    }

    expected_output = [
        '::add-mask::abc',
        '::set-output name=sensitive_string::abc',
        '::set-output name=string::xyz'
    ]

    output = list(convert_to_github(input))
    assert output == expected_output


def test_number():
    input = {
        "int": {
            "sensitive": False,
            "type": "number",
            "value": 123
        },
        "sensitive_int": {
            "sensitive": True,
            "type": "number",
            "value": 123
        }
    }

    expected_output = [
        '::set-output name=int::123',
        '::add-mask::123',
        '::set-output name=sensitive_int::123'
    ]

    output = list(convert_to_github(input))
    assert output == expected_output

def test_bool():
    input = {
        "bool": {
            "sensitive": False,
            "type": "bool",
            "value": True
        }
    }

    expected_output = [
        '::set-output name=bool::true'
    ]

    output = list(convert_to_github(input))
    assert output == expected_output
