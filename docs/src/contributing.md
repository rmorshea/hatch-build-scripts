# Contributing

!!! note

    The [Code of Conduct](conduct.md) applies in all community spaces. If you are not familiar with
    our Code of Conduct policy, take a minute to read it before contributing.

## Getting Started

[UV](https://docs.astral.sh/uv/) is used to manage this project, so the first thing
you'll need to do is [install it](https://docs.astral.sh/uv/getting-started/installation/).
From here you should be able to run the test suite:

```bash
uv run dev.py test
```

!!! note

    By default, UV will install an appropriate Python version and make a virtual environment under the `.venv`.

All developer scripts are located in a `dev.py` file at the root of the repository.
To see a full list of commands run:

```bash
uv run dev.py --help
```

!!! tip

    It can be helpful to define an alias if you find yourself typing `uv run dev.py` frequently. For example:

    ```bash
    alias uvr="uv run"
    ```

Common commands include:

```bash
# run the test suite
uv run dev.py test

# run the test suite with coverage enabled
uv run dev.py cov

# run lint checks on the source code and docs
uv run dev.py lint

# build and serve the documentation locally
uv run dev.py docs serve
```

## Project Template

This project was generated from a [template](https://github.com/rmorshea/python-copier-template)
using [Copier](https://github.com/copier-org/copier). To update this project with the latest
changes from that template run:

```bash
uvx copier update
```

Any files with incompatible changes will have conflict markers similar to those found when
performaing a `git merge`. For more information, see the "Checking Out Conflicts" section
of the [`git` documentation](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging).
