python := `poetry run which python3`

test:
    {{python}} -m pytest
