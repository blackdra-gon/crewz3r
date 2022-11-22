# Crew Logic

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Calculate solutions to the cooperative card game _The Crew_ using
the [Z3 Theorem Prover ](https://github.com/Z3Prover/z3/).

## Webserver

Start the server with `poetry python server.py`.
You can access the user interface on port `5000` via localhost or your local
network.

## Code style

The [pre-commit](https://pre-commit.com/) framework is used to apply various code
quality assurance tools automatically:

- [pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks)
- [autoflake](https://github.com/PyCQA/autoflake)
- [isort](https://github.com/PyCQA/isort)
- [pyupgrade](https://github.com/asottile/pyupgrade)
- [black](https://github.com/psf/black)
- [flake8](https://github.com/PyCQA/flake8)
- [prettier](https://github.com/pre-commit/mirrors-prettier)

The [MyPy](https://github.com/pre-commit/mirrors-mypy/)
type checker can be run manually with:

`pre-commit run -a --hook-stage manual mypy`.

This project uses the [Black](https://github.com/psf/black) auto-formatter to enforce a
consistent code style. For editor/IDE integration, see
[the documentation](https://black.readthedocs.io/en/stable/integrations/editors.html).

### Setup

Run the following commands to enable:

`pip install pre-commit`

`pre-commit install -f --install-hooks`

## Dependencies

Dependencies are managed through [poetry](https://python-poetry.org).
After cloning the repository, run `poetry install` to install all dependencies.
