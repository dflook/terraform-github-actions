from action import Output, Terraform

junit_xml_path = Output(
    name='junit-xml-path',
    type='string',
    description='''
A test report in JUnit XML format.

The path is relative to the Actions workspace.

This will only be available when using Terraform 1.11.0 or later.
''',
    available_in = [Terraform]
)
