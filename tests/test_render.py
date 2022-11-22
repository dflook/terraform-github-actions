from plan_renderer.variables import (
    render_value, render_mapping, render_sequence, render_bool, render_number,
    render_string, render_argument_list, render_null, render_sensitive, Sensitive
)


def test_render_number():
    assert render_number(2) == '2'
    assert render_number(3.4) == '3.4'


def test_render_bool():
    assert render_bool(True) == 'true'
    assert render_bool(False) == 'false'


def test_render_null():
    assert render_null() == 'null'


def test_render_sensitive():
    assert render_sensitive() == '(sensitive value)'


def test_render_string():
    assert render_string('hello') == '"hello"'
    assert render_string('hello"') == '"hello\\""'
    assert render_string('multi\nline') == '''<<-EOT
    multi
    line
EOT'''
    assert render_string('trailing\nnewline\n') == '''<<-EOT
    trailing
    newline
EOT'''
    assert render_string('trailing\nnewline\n\n\n') == '''<<-EOT
    trailing
    newline


EOT'''

def test_render_sequence():
    assert render_sequence([]) == '[]'
    assert render_sequence(['a']) == '''[
    "a",
]'''
    assert render_sequence(['a', 'b']) == '''[
    "a",
    "b",
]'''

def test_render_mapping():
    assert render_mapping({}) == '{}'
    assert render_mapping({'a': 1}) == '''{
    a = 1
}'''
    assert render_mapping({'a': 1, 'b': 2}) == '''{
    a = 1
    b = 2
}'''

def test_render_value():
    assert render_value("hello") == '"hello"'
    assert render_value(1) == '1'
    assert render_value(None) == 'null'
    assert render_value(Sensitive()) == '(sensitive value)'
    assert render_value(True) == 'true'
    assert render_value(['a']) == '''[
    "a",
]'''
    assert render_value({'a': 1}) == '''{
    a = 1
}'''

def test_render_argument_list():
    assert render_argument_list({}) == '\n'
    assert render_argument_list({'a': True}) == 'a = true\n'
    assert render_argument_list({'a': True, 'b': False}) == 'a = true\nb = false\n'

    a = render_argument_list({
        'b': {
            'c': 'hello',
            'f': {
                'efdsdf': 'f',
                'g': 'h',
                'long': 'this\nis\na\nreally\nlong\nstring\n\n'
            },
            'g': 2,
            'a': Sensitive(),
            'b': [],
            'e': {},
            'd': [
                {
                    'nested': 'yep'
                },
                False,
                1.4
            ]
        },
        'zed': 'world',
        'a': 'hello'
    })

    print(a)

    assert a == '''a   = "hello"
b   = {
    a = (sensitive value)
    b = []
    c = "hello"
    d = [
        {
            nested = "yep"
        },
        false,
        1.4,
    ]
    e = {}
    f = {
        efdsdf = "f"
        g      = "h"
        long   = <<-EOT
            this
            is
            a
            really
            long
            string

        EOT
    }
    g = 2
}
zed = "world"
'''