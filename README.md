# Hatch Build Scripts

[![PyPI - Version](https://img.shields.io/pypi/v/hatch_build_scripts.svg)](https://pypi.org/project/hatch_build_scripts)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch_build_scripts.svg)](https://pypi.org/project/hatch_build_scripts)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A plugin for [Hatch](https://github.com/pypa/hatch) that allows you to run arbitrary
build scripts and include their artifacts in your package distributions.

## Installation

To set up `hatch-build-scripts` for your project you'll need to configure it in your
project's `pyproject.toml` file as a `build-system` requirement:

```toml
[build-system]
requires = ["hatchling", "hatch-build-scripts"]
build-backend = "hatchling.build"
```

## Usage

Now you'll need to configure the build scripts you want to run. This is done by adding
an array of scripts to the `tool.hatch.build.hooks.build-scripts.scripts` key in your
`pyproject.toml` file. Each script is configured with the following keys:

| Key               | Default  | Description                                                                                             |
| ----------------- | -------- | ------------------------------------------------------------------------------------------------------- |
| `commands`        | required | An array of commands to run. Each command is run in a separate shell.                                   |
| `artifacts`       | required | An array of artifact patterns (same as `.gitignore`) to include in your package distributions.          |
| `out_dir`         | `"."`    | The directory to copy artifacts into.                                                                   |
| `work_dir`        | `"."`    | The directory to run the commands in. All artifact patterns are relative to this directory.             |
| `clean_artifacts` | `true`   | Whether to clean files from the `out_dir` that match the artifact patterns before running the commands. |
| `clean_out_dir`   | `false`  | Whether to clean the `out_dir` before running the commands.                                             |

In practice this looks like:

```toml
[[tool.hatch.build.hooks.build-scripts.scripts]]
out_dir = "out"
commands = [
    "echo 'Hello, world!' > hello.txt",
    "echo 'Goodbye, world!' > goodbye.txt",
]
artifacts = [
    "hello.txt",
    "goodbye.txt",
]

[[tool.hatch.build.hooks.build-scripts.scripts]]
# you can add more scripts here...
```

You can configure script defaults for scripts by adding a
`[tool.hatch.build.hooks.build-scripts]` table to your `pyproject.toml` file. The
following keys are supported:

| Key               | Default | Description                                                                                             |
| ----------------- | ------- | ------------------------------------------------------------------------------------------------------- |
| `out_dir`         | `"."`   | The directory to copy artifacts into.                                                                   |
| `work_dir`        | `"."`   | The directory to run the commands in. All artifact patterns are relative to this directory.             |
| `clean_artifacts` | `true`  | Whether to clean files from the `out_dir` that match the artifact patterns before running the commands. |
| `clean_out_dir`   | `false` | Whether to clean the `out_dir` before running the commands.                                             |
