from github_actions.commands import generate_delimiter


def test_delimiter_length():
    delimiter = generate_delimiter()
    assert len(delimiter) == 20


def test_delimiter_is_lowercase_alpha():
    delimiter = generate_delimiter()
    assert delimiter.isalpha()
    assert delimiter.islower()


def test_delimiter_is_unique():
    delimiters = {generate_delimiter() for _ in range(100)}
    assert len(delimiters) == 100
