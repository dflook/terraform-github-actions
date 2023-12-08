from typing import Any

from plan_renderer.variables import render_argument_list, Sensitive


def render_outputs(outputs: dict[str, Any]) -> str:
    return render_argument_list({
        key: Sensitive() if value['sensitive'] else value['value'] for key, value in outputs.items()
    })
