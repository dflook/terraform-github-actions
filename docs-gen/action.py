import textwrap
from dataclasses import dataclass, field
from textwrap import indent
from typing import Callable, Type


def heading(text: str, level: int=1) -> str:
    return f'{"#" * level} {text}\n\n'

def text_chunk(text: str, prefix_length: int=0, trailing_blank_line: bool=True) -> str:
    return textwrap.indent(textwrap.dedent(text).strip(), ' ' * prefix_length) + ('\n\n' if trailing_blank_line else '\n')

class Tool:
    ProductName: str
    ToolName: str
    JsonFormatUrl: str
    VariableDefinitionUrl: str

class Terraform(Tool):
    ProductName = 'Terraform'
    ToolName = 'terraform'
    JsonFormatUrl = 'https://www.terraform.io/docs/internals/json-format.html'
    VariableDefinitionUrl = 'https://developer.hashicorp.com/terraform/language/values/variables#variable-definitions-tfvars-files'
    DestroyModeUrl = 'https://developer.hashicorp.com/terraform/cli/commands/plan#planning-modes'
    RequiredVersionUrl = 'https://developer.hashicorp.com/terraform/language/terraform#terraform-required_version'

class OpenTofu(Tool):
    ProductName = 'OpenTofu'
    ToolName = 'tofu'
    JsonFormatUrl = 'https://opentofu.org/docs/internals/json-format/'
    VariableDefinitionUrl = 'https://opentofu.org/docs/language/values/variables/#variable-definitions-tfvars-files'
    DestroyModeUrl = 'https://opentofu.org/docs/cli/commands/plan/#planning-modes'
    RequiredVersionUrl = 'https://opentofu.org/docs/language/settings/#specifying-a-required-opentofu-version'

@dataclass
class Input:
    name: str
    type: str
    description: str
    meta_description: str = None
    default: str = None
    default_description: str = None
    required: bool = False
    deprecation_message: str = None
    show_in_docs: bool = True
    example: str = None

    def markdown(self, tool: Tool) -> str:
        if self.deprecation_message is None:
            s = f'* `{self.name}`\n\n'
        else:
            s = f'* ~~`{self.name}`~~\n\n'
            s += f'  > :warning: **Deprecated**: {self.deprecation_message}\n\n'

        s += text_chunk(self.description, 2)

        if self.example:
            s += text_chunk(self.example, 2)

        s += f'  - Type: {self.type}\n'
        s += '  - Required\n' if self.required else '  - Optional\n'
        if self.default or self.default_description:
            s += f'  - Default: {self.default_description or f"`{self.default}`"}\n'

        return s.strip()

@dataclass
class EnvVar:
    name: str
    description: str
    example: str=None
    type: str='string'
    default: str=None

    def markdown(self, tool: Tool) -> str:
        s = f'* `{self.name}`\n\n'
        s += text_chunk(self.description, 2)

        if self.example:
            s += text_chunk(self.example, 2)

        s += f'  - Type: {self.type}\n'
        s += '  - Optional\n'

        if self.default is not None:
            s += f'  - Default: `{self.default}`\n'

        return s.strip()

@dataclass
class Output:
    name: str
    description: str
    meta_description: str = None
    type: str = None
    aliases: list[str] = field(default_factory=list)
    meta_output: bool = False
    available_in: list[Type[Terraform] | Type[OpenTofu]] = field(default_factory=lambda: [Terraform, OpenTofu])

    def markdown(self, tool: Tool) -> str:
        if self.meta_output:
            s = f'* {self.name}\n'
        else:
            s = f'* `{self.name}`\n'

        for alias in self.aliases:
            s += f'* `{alias}`\n'

        s += '\n'

        s += text_chunk(self.description, 2)

        if self.type is not None:
            s += f'  - Type: {self.type}\n'

        return s.strip()

def nice_yaml_string(key: str, value: str, prefix_length: int=0) -> str:
    if '\n' not in value.strip():
        s = f'{key}: {value.strip()}\n'
    else:
        s = f'{key}: |\n'
        s += text_chunk(value, 2, trailing_blank_line=False)

    return indent(s, ' ' * prefix_length)

def productize(s: str, tool: Tool) -> str:
    for field, value in vars(tool).items():
        if not field.startswith('_'):
            s = s.replace(f'${field}', value)
    return s

@dataclass
class Action:
    name: str
    description: str | Callable[[Tool], str]
    meta_description: str = None
    inputs: list[Input] = field(default_factory=list)
    inputs_intro: str = None
    environment_variables: list[EnvVar] = None
    environment_variables_intro: str = None
    outputs: list[Output] = field(default_factory=list)
    outputs_intro: str = None
    extra: str | Callable[[bool], str] = None

    def assert_order(self, expected: list[str], actual: list[Input | Output | EnvVar]):
        for attribute in actual:
            if attribute.name not in expected:
                raise ValueError(f"Unknown ordering for {self.name}: {attribute.name}")

        expected = [name for name in expected if name in [attribute.name for attribute in actual]]

        for expected_input, actual_input in zip(expected, [attribute.name for attribute in actual]):
            if expected_input != actual_input:
                raise ValueError(f"Inputs for {self.name} are not in the expected order: {actual_input} should be before {expected_input}")


    def assert_ordering(self):
        self.assert_order([
            "path",
            "backend_type",
            "workspace",
            "label",
            "test_directory",
            "test_filter",
            "variables",
            "var_file",
            "var",
            "backend_config",
            "backend_config_file",
            "replace",
            "target",
            "destroy",
            "plan_path",
            "auto_approve",
            "add_github_comment",
            "parallelism",
            "lock_id"
        ], self.inputs)

        self.assert_order([
            "changes",
            "plan_path",
            "json_plan_path",
            "text_plan_path",
            "junit-xml-path",
            "to_add",
            "failure-reason",
            "lock-info",
            "run_id",
            "terraform",
            "tofu",
            "Provider Versions",
            "$ProductName Outputs",
        ], self.outputs)

        self.assert_order([
            "GITHUB_TOKEN",
            "TERRAFORM_ACTIONS_GITHUB_TOKEN",
            "GITHUB_DOT_COM_TOKEN",
            "TERRAFORM_CLOUD_TOKENS",
            "TERRAFORM_SSH_KEY",
            "TERRAFORM_HTTP_CREDENTIALS",
            "TF_PLAN_COLLAPSE_LENGTH",
            "TERRAFORM_PRE_RUN",
        ], self.environment_variables)

    def markdown(self, tool: Tool) -> str:

        s = heading(f'{tool.ToolName}-{self.name} action')
        s += f'This is one of a suite of {tool.ProductName} related actions - find them at [dflook/terraform-github-actions](https://github.com/dflook/terraform-github-actions).\n\n'

        if callable(self.description):
            s += text_chunk(self.description(tool))
        else:
            s += text_chunk(self.description)

        if self.inputs:
            s += heading('Inputs', 2)

            if self.inputs_intro:
                s += text_chunk(self.inputs_intro)

            for input in self.inputs:
                if not input.show_in_docs:
                    continue
                s += text_chunk(input.markdown(tool))

        if self.outputs:
            s += heading('Outputs', 2)

            if self.outputs_intro:
                s += text_chunk(self.outputs_intro)

            for output in self.outputs:
                if tool not in output.available_in:
                    continue
                s += text_chunk(output.markdown(tool))

        if self.environment_variables:
            s += heading('Environment Variables', 2)

            if self.environment_variables_intro:
                s += text_chunk(self.environment_variables_intro)

            for env_var in self.environment_variables:
                s += text_chunk(env_var.markdown(tool))

        if self.extra:
            s += text_chunk(self.extra)

        if s.endswith('\n\n'):
            s = s[:-1]

        return productize(s, tool)

    def action_yaml(self, tool: Tool) -> str:
        s = f'name: {tool.ToolName}-{self.name}\n'
        s += nice_yaml_string('description', self.meta_description or self.description)
        s += 'author: Daniel Flook\n\n'

        if self.inputs:
            s += 'inputs:\n'

        for input in self.inputs:
            s += f'  {input.name}:\n'

            description = input.meta_description or input.description
            s += nice_yaml_string('description', description, 4)
            s += f'    required: {"true" if input.required else "false"}\n'

            if input.default is not None:
                s += f'    default: "{input.default}"\n'

            if input.deprecation_message:
                s += f'    deprecationMessage: {input.deprecation_message}\n'

        s += '\n'

        if [output for output in self.outputs if not output.meta_output and tool in output.available_in]:
            s += 'outputs:\n'

            for output in (output for output in self.outputs if not output.meta_output and tool in output.available_in):
                if output.meta_output:
                    continue

                for name in [output.name] + output.aliases:
                    s += f'  {name}:\n'

                    description = output.meta_description or output.description
                    s += nice_yaml_string('description', description, 4)

            s += '\n'

        if tool.ProductName == 'Terraform':
            s += text_chunk(f'''
                runs:
                  using: docker
                  image: ../image/Dockerfile
                  entrypoint: /entrypoints/{self.name}.sh
                
                branding:
                  icon: globe
                  color: purple
            ''', trailing_blank_line=False)
        else:
            s += text_chunk(
                f'''
                runs:
                  env:
                    OPENTOFU: true
                  using: docker
                  image: ../image/Dockerfile
                  entrypoint: /entrypoints/{self.name}.sh

                branding:
                  icon: globe
                  color: purple
            ''', trailing_blank_line=False)

        return productize(s, tool)