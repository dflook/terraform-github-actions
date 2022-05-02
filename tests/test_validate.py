from convert_validate_report import convert_to_github


def test_valid():
    input = {
        "valid": True,
        "error_count": 0,
        "warning_count": 0,
        "diagnostics": []
    }

    output = list(convert_to_github(input, 'terraform'))
    assert output == []


def test_invalid():
    input = {
        "valid": False,
        "error_count": 2,
        "warning_count": 0,
        "diagnostics": [
            {
                "severity": "error",
                "summary": "Could not satisfy plugin requirements",
                "detail": "\nPlugin reinitialization required. Please run \"terraform init\".\n\nPlugins are external binaries that Terraform uses to access and manipulate\nresources. The configuration provided requires plugins which can't be located,\ndon't satisfy the version constraints, or are otherwise incompatible.\n\nTerraform automatically discovers providers requirements from your\nconfiguration, including plugin-cache used in child modules. To see the\nrequirements and constraints from each module, run \"terraform plugin-cache\".\n"
            },
            {
                "severity": "error",
                "summary": "providers.null: no suitable version installed\n  version requirements: \"(any version)\"\n  versions installed: none"
            }
        ]
    }

    expected_output = [
        '::error ::Could not satisfy plugin requirements',
        '::error ::providers.null: no suitable version installed'
    ]

    output = list(convert_to_github(input, 'terraform'))
    assert output == expected_output


def test_blah():
    input = {
        "valid": False,
        "error_count": 1,
        "warning_count": 0,
        "diagnostics": [
            {
                "severity": "error",
                "summary": "Duplicate resource \"null_resource\" configuration",
                "detail": "A null_resource resource named \"hello\" was already declared at main.tf:1,1-33. Resource names must be unique per type in each module.",
                "range": {
                    "filename": "main.tf",
                    "start": {
                        "line": 2,
                        "column": 1,
                        "byte": 36
                    },
                    "end": {
                        "line": 2,
                        "column": 33,
                        "byte": 68
                    }
                }
            }
        ]
    }

    expected_output = [
        '::error file=terraform/main.tf,line=2,col=1,endLine=2,endColumn=33::Duplicate resource "null_resource" configuration'
    ]

    output = list(convert_to_github(input, 'terraform'))
    assert output == expected_output


def test_invalid_paths():
    input = {
        "valid": False,
        "error_count": 2,
        "warning_count": 0,
        "diagnostics": [
            {
                "severity": "error",
                "summary": "Duplicate resource \"null_resource\" configuration",
                "detail": "A null_resource resource named \"hello\" was already declared at main.tf:1,1-33. Resource names must be unique per type in each module.",
                "range": {
                    "filename": "main.tf",
                    "start": {
                        "line": 2,
                        "column": 1,
                        "byte": 36
                    },
                    "end": {
                        "line": 2,
                        "column": 33,
                        "byte": 68
                    }
                }
            },
            {
                "severity": "error",
                "summary": "Duplicate resource \"null_resource\" configuration",
                "detail": "A null_resource resource named \"goodbye\" was already declared at ../module/invalid.tf:1,1-33. Resource names must be unique per type in each module.",
                "range": {
                    "filename": "../module/invalid.tf",
                    "start": {
                        "line": 2,
                        "column": 1,
                        "byte": 36
                    },
                    "end": {
                        "line": 5,
                        "column": 66,
                        "byte": 68
                    }
                }
            }
        ]
    }

    expected_output = [
        '::error file=tests/validate/invalid/main.tf,line=2,col=1,endLine=2,endColumn=33::Duplicate resource "null_resource" configuration',
        '::error file=tests/validate/module/invalid.tf,line=2,col=1,endLine=5,endColumn=66::Duplicate resource "null_resource" configuration'
    ]

    output = list(convert_to_github(input, 'tests/validate/invalid'))
    assert output == expected_output


def test_json_0_1():
    input = {
        "format_version": "0.1",
        "valid": False,
        "error_count": 2,
        "warning_count": 0,
        "diagnostics": [
            {
                "severity": "error",
                "summary": "Duplicate resource \"null_resource\" configuration",
                "detail": "A null_resource resource named \"hello\" was already declared at main.tf:1,1-33. Resource names must be unique per type in each module.",
                "range": {
                    "filename": "main.tf",
                    "start": {
                        "line": 2,
                        "column": 1,
                        "byte": 36
                    },
                    "end": {
                        "line": 2,
                        "column": 33,
                        "byte": 68
                    }
                },
                "snippet": {
                    "context": None,
                    "code": "resource \"null_resource\" \"hello\" {}",
                    "start_line": 2,
                    "highlight_start_offset": 0,
                    "highlight_end_offset": 32,
                    "values": []
                }
            },
            {
                "severity": "error",
                "summary": "Duplicate resource \"null_resource\" configuration",
                "detail": "A null_resource resource named \"goodbye\" was already declared at main.tf:5,1-33. Resource names must be unique per type in each module.",
                "range": {
                    "filename": "main.tf",
                    "start": {
                        "line": 6,
                        "column": 1,
                        "byte": 110
                    },
                    "end": {
                        "line": 6,
                        "column": 33,
                        "byte": 142
                    }
                },
                "snippet": {
                    "context": None,
                    "code": "resource \"null_resource\" goodbye {}",
                    "start_line": 6,
                    "highlight_start_offset": 0,
                    "highlight_end_offset": 32,
                    "values": []
                }
            },
            {
              "severity": "error",
              "summary": "Module not installed",
              "detail": "This module is not yet installed. Run \"terraform init\" to install all modules required by this configuration.",
              "range": {
                "filename": "main.tf",
                "start": {
                  "line": 11,
                  "column": 1,
                  "byte": 201
                },
                "end": {
                  "line": 11,
                  "column": 13,
                  "byte": 213
                }
              },
              "snippet": {
                "context": None,
                "code": "module \"vpc\" {",
                "start_line": 11,
                "highlight_start_offset": 0,
                "highlight_end_offset": 12,
                "values": []
              }
            }
        ]
    }

    expected_output = [
        '::error file=tests/validate/invalid/main.tf,line=2,col=1,endLine=2,endColumn=33::Duplicate resource "null_resource" configuration',
        '::error file=tests/validate/invalid/main.tf,line=6,col=1,endLine=6,endColumn=33::Duplicate resource "null_resource" configuration'
    ]

    output = list(convert_to_github(input, 'tests/validate/invalid'))
    assert output == expected_output
