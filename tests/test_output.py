import json
from convert_output import convert_to_github, Mask, Output, read_input


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
        Mask(value='abc'),
        Output(name='sensitive_string', value='abc'),
        Output(name='string', value='xyz')
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
        Output(name='int', value='123'),
        Mask(value='123'),
        Output(name='sensitive_int', value='123')
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
        Output(name='bool', value='true')
    ]

    output = list(convert_to_github(input))
    assert output == expected_output

def test_tuple():
    input = {
        "my_tuple": {
            "sensitive": False,
            "type": [
                "tuple",
                [
                    "string",
                    "string"
                ]
            ],
            "value": [
                "one",
                "two"
            ]
        },
        "my_sensitive_tuple": {
            "sensitive": True,
            "type": [
                "tuple",
                [
                    "string",
                    "string"
                ]
            ],
            "value": [
                "one",
                "two"
            ]
        }
    }

    expected_output = [
        Output(name='my_tuple', value='["one","two"]'),
        Mask(value='["one","two"]'),
        Output(name='my_sensitive_tuple', value='["one","two"]')
    ]

    output = list(convert_to_github(input))
    assert output == expected_output

def test_list():
    input = {
        "my_list": {
            "sensitive": False,
            "type": [
                "list",
                "string"
            ],
            "value": [
                "one",
                "two"
            ]
        },
        "my_sensitive_list": {
            "sensitive": True,
            "type": [
                "list",
                "string"
            ],
            "value": [
                "one",
                "two"
            ]
        }
    }

    expected_output = [
        Output(name='my_list', value='["one","two"]'),
        Mask(value='["one","two"]'),
        Output(name='my_sensitive_list', value='["one","two"]')
    ]

    output = list(convert_to_github(input))
    assert output == expected_output

def test_map():
    input = {
        "my_map": {
            "sensitive": False,
            "type": [
                "map",
                "string"
            ],
            "value": {
                "first": "one",
                "second": "two",
                "third": "3"
            }
        },
        "my_sensitive_map": {
            "sensitive": True,
            "type": [
                "map",
                "string"
            ],
            "value": {
                "first": "one",
                "second": "two",
                "third": 3
            }

        }
    }

    expected_output = [
        Output(name='my_map', value='{"first":"one","second":"two","third":"3"}'),
        Mask(value='{"first":"one","second":"two","third":3}'),
        Output(name='my_sensitive_map',
               value='{"first":"one","second":"two","third":3}')
    ]

    output = list(convert_to_github(input))
    assert output == expected_output

def test_object():
    input = {
        "my_object": {
            "sensitive": False,
            "type": [
                "object",
                {
                    "first": "string",
                    "second": "string",
                    "third": "number"
                }
            ],
            "value": {
                "first": "one",
                "second": "two",
                "third": 3
            }
        },
        "my_sensitive_object": {
            "sensitive": True,
            "type": [
                "object",
                {
                    "first": "string",
                    "second": "string",
                    "third": "number"
                }
            ],
            "value": {
                "first": "one",
                "second": "two",
                "third": 3
            }
        }
    }

    expected_output = [
        Output(name='my_object', value='{"first":"one","second":"two","third":3}'),
        Mask(value='{"first":"one","second":"two","third":3}'),
        Output(name='my_sensitive_object',
               value='{"first":"one","second":"two","third":3}')
    ]

    output = list(convert_to_github(input))
    assert output == expected_output

def test_set():
    input = {
        "my_set": {
            "sensitive": False,
            "type": [
                "set",
                "string"
            ],
            "value": [
                "one",
                "two"
            ]
        },
        "my_sensitive_set": {
            "sensitive": True,
            "type": [
                "set",
                "string"
            ],
            "value": [
                "one",
                "two"
            ]
        }
    }

    expected_output = [
        Output(name='my_set', value='["one","two"]'),
        Mask(value='["one","two"]'),
        Output(name='my_sensitive_set', value='["one","two"]')
    ]

    output = list(convert_to_github(input))
    assert output == expected_output


def test_compound():
    input = {
        "my_compound_output": {
            "sensitive": False,
            "type": [
                "object",
                {
                    "first": [
                        "list",
                        "string"
                    ],
                    "second": [
                        "set",
                        "string"
                    ],
                    "third": "number"
                }
            ],
            "value": {
                "first": [
                    "one",
                    "two"
                ],
                "second": [
                    "one",
                    "two"
                ],
                "third": 3
            }
        }
    }

    expected_json = json.dumps({
        "first": ["one", "two"],
        "second": ["one", "two"],
        "third": 3
    }, separators=(',', ':'))

    expected_output = [
        Output('my_compound_output', expected_json)
    ]

    output = list(convert_to_github(input))
    assert output == expected_output


def test_read_input_with_junk_lines():
    input_string = ''' There was an error connecting to Terraform Cloud. Please do not exit
Terraform to prevent data loss! Trying to restore the connection...

Still trying to restore the connection... (3s elapsed)
Still trying to restore the connection... (5s elapsed)
{
    "output1": {"type": "string", "value": "value1", "sensitive": false}
}'''
    result = read_input(input_string)
    assert result == {
        "output1": {"type": "string", "value": "value1", "sensitive": False}
    }

def test_read_input_without_junk_lines():
    input_string = '''{
    "output1": {"type": "string", "value": "value1", "sensitive": false}
}'''
    result = read_input(input_string)
    assert result == {
        "output1": {"type": "string", "value": "value1", "sensitive": False}
    }

def test_read_input_empty_string():
    input_string = ''
    try:
        read_input(input_string)
        assert False, "Expected an exception"
    except json.JSONDecodeError:
        pass

def test_read_input_invalid_json():
    input_string = '''{
    "output1": {"type": "string", "value": "value1", "sensitive": false'''
    try:
        read_input(input_string)
        assert False, "Expected an exception"
    except json.JSONDecodeError:
        pass
