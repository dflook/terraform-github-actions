from typing import Any, Union
from textwrap import indent


class Sensitive: pass


def render_argument_list(argument_list: dict[str, Any]) -> str:
    """
    An argument list is a list of named values that are formatted as a block

    For example: the attributes in a resource block or object, a list of variables, a list of outputs.
    """

    if not argument_list:
        return '\n'

    max_key_length = max(len(k) for k in argument_list)

    s = ''

    for key in sorted(argument_list):
        value = argument_list[key]
        s += f'{key:{max_key_length}} = {render_value(value)}\n'

    return s


def render_string(value: str) -> str:
    if '\n' in value:
        s = '<<-EOT\n'
        s += indent(value, ' ' * 4)
        if not s.endswith('\n'):
            s += '\n'
        s += 'EOT'
        return s
    else:
        return '"' + value.replace('"', '\\"') + '"'


def render_bool(value: bool) -> str:
    return 'true' if value else 'false'


def render_sequence(sequence: list) -> str:
    if not sequence:
        return '[]'

    s = '['
    for value in sequence:
        s += '\n' + indent(render_value(value) + ',', ' ' * 4)
    s += '\n]'

    return s


def render_mapping(mapping: dict) -> str:
    if not mapping:
        return '{}'

    s = '{\n'
    s += indent(render_argument_list(mapping), ' ' * 4)
    s += '}'

    return s


def render_number(value: Union[int, float]) -> str:
    return str(value)


def render_null() -> str:
    return 'null'


def render_sensitive() -> str:
    return '(sensitive value)'


def render_value(value: Any) -> str:
    if isinstance(value, str):
        return render_string(value)
    if isinstance(value, bool):
        return render_bool(value)
    if isinstance(value, (int, float)):
        return render_number(value)
    if isinstance(value, list):
        return render_sequence(value)
    if isinstance(value, dict):
        return render_mapping(value)
    if isinstance(value, Sensitive):
        return render_sensitive()
    if value is None:
        return render_null()

    # Unknown value type
    return 'unknown value type'
