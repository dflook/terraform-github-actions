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
        '::error file=terraform/main.tf,line=2,col=1::Duplicate resource "null_resource" configuration'
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
              "line": 2,
              "column": 33,
              "byte": 68
            }
          }
        }
      ]
    }

    expected_output = [
        '::error file=tests/validate/invalid/main.tf,line=2,col=1::Duplicate resource "null_resource" configuration',
        '::error file=tests/validate/module/invalid.tf,line=2,col=1::Duplicate resource "null_resource" configuration'
    ]

    output = list(convert_to_github(input, 'tests/validate/invalid'))
    assert output == expected_output
