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
        '::set-output name=my_tuple::["one","two"]',
        '::add-mask::["one","two"]',
        '::set-output name=my_sensitive_tuple::["one","two"]'
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
        '::set-output name=my_list::["one","two"]',
        '::add-mask::["one","two"]',
        '::set-output name=my_sensitive_list::["one","two"]'
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
        '::set-output name=my_map::{"first":"one","second":"two","third":"3"}',
        '::add-mask::{"first":"one","second":"two","third":3}',
        '::set-output name=my_sensitive_map::{"first":"one","second":"two","third":3}'
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
        '::set-output name=my_object::{"first":"one","second":"two","third":3}',
        '::add-mask::{"first":"one","second":"two","third":3}',
        '::set-output name=my_sensitive_object::{"first":"one","second":"two","third":3}'
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
        '::set-output name=my_set::["one","two"]',
        '::add-mask::["one","two"]',
        '::set-output name=my_sensitive_set::["one","two"]'
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
        '::set-output name=my_compound_output::' + expected_json
    ]

    output = list(convert_to_github(input))
    assert output == expected_output
