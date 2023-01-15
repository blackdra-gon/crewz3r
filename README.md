# Crewz3r

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)
[![license](https://img.shields.io/github/license/bhennies/Crew_Logic)](https://github.com/bhennies/Crew_Logic/blob/master/COPYING)

Calculate solutions to the cooperative card game _The Crew_ using
the [Z3 Theorem Prover](https://github.com/Z3Prover/z3/).

## Webserver

Start the server with `poetry run python server.py`.
You can access the user interface on port `5000` via localhost or your local
network.

## Dependencies

Dependencies are managed through [poetry](https://python-poetry.org).
After installing poetry and cloning the repository, run `poetry install` to install all dependencies.

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

To run the [MyPy](https://github.com/pre-commit/mirrors-mypy/)
type checker manually:

```
pre-commit run -a --hook-stage manual mypy
```

To run the other pre-commit hooks manually:

```
pre-commit run -a
```

This project uses the [Black](https://github.com/psf/black) auto-formatter to enforce a
consistent code style. For editor/IDE integration, see
[the documentation](https://black.readthedocs.io/en/stable/integrations/editors.html).

### Setup with Pycharm

1. Install Python 3.11 `sudo apt install python3.11`
2. Setup Python Interpreter in Pycharm
3. Install Poetry
   1. Install python-venv
      ``sudo apt install python3.11-venv`
   2. Install poetry
      `curl -sSL https://install.python-poetry.org | python3 -`
      https://python-poetry.org/docs/#installing-with-the-official-installer
   3. Update Path
      If the install script tells you so, add
      export PATH="/home/benjamin/.local/bin:$PATH"
      to ~/.bashrc
4. Install dependencies with `poetry install`
5. Now you should be ready to execute crewz3r with pycharm or poetry (s. above)

6. Run the following commands to enable pre-commit-hooks:

```
pip install pre-commit
pre-commit install -f --install-hooks
```

## Testing

Unit tests and coverage analysis with
[pytest](https://docs.pytest.org/en/latest/contents.html) and
[hypothesis](https://hypothesis.readthedocs.io/en/latest/index.html) (WIP). Run with:

```
poetry run pytest
```
