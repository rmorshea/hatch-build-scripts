# Hatch Build Scripts

A plugin for [Hatch](https://github.com/pypa/hatch) that allows you to run arbitrary
build scripts and include their artifacts in your package distributions.


## Installation

To set up `hatch-build-scripts` for your project you'll need to configure it in your
project's `pyproject.toml` file. You'll need to modify two sections of the file:

- `build-system.requires`: To add `hatch-build-scripts` as a build dependency.
- `tool.hatch.build.hooks.build-scripts`: To configure the build scripts you want to run.

In practice this looks like

```toml
[build-system]
requires = ["hatchling", "hatch-build-scripts"]
build-backend = "hatchling.build"

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
```
