# ruff: noqa: S607,S603,S404,FBT001,D401,D103

import os
import subprocess
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Literal

import click

IN_CI = bool(os.getenv("GITHUB_ACTIONS"))


@click.group()
def main():
    """A collection of dev utilities."""


@main.command("test")
@click.argument("args", nargs=-1)
def test(args: list[str]):
    """Run the test suite."""
    run(["pytest", "-v", *args])


@main.command("cov")
@click.option("--no-test", is_flag=True, help="Skip running tests with coverage")
@click.option("--old-coverage-xml", default=None, type=str, help="Path to target coverage.xml.")
def cov(no_test: bool, old_coverage_xml: str | None):
    """Run the test suite with coverage."""
    if not no_test:
        try:
            run(["coverage", "run", "-m", "pytest", "-v"])
        finally:
            run(["coverage", "combine"], check=False)
            run(["coverage", "report"])
            run(["coverage", "xml"])
    if old_coverage_xml is not None:
        if Path(old_coverage_xml).exists():
            run(
                [
                    "pycobertura",
                    "diff",
                    old_coverage_xml,
                    "coverage.xml",
                    "--source1",
                    ".",
                    "--source2",
                    ".",
                ]
            )
        else:
            msg = f"Target coverage file {old_coverage_xml} does not exist"
            raise click.ClickException(msg)
    elif not IN_CI:
        run(["diff-cover", "coverage.xml", "--config-file", "pyproject.toml"])


@main.command("lint")
@click.option("--check", is_flag=True, help="Check for linting issues without fixing.")
@click.option("--no-md-style", is_flag=True, help="Skip style check Markdown files.")
@click.option("--no-py-style", is_flag=True, help="Skip style check Python files.")
@click.option("--no-py-types", is_flag=True, help="Skip type check Python files.")
@click.option("--no-uv-locked", is_flag=True, help="Skip check that the UV lock file is synced")
@click.option("--no-yml-style", is_flag=True, help="Skip style check YAML files.")
def lint(
    check: bool,
    no_md_style: bool,
    no_py_style: bool,
    no_py_types: bool,
    no_uv_locked: bool,
    no_yml_style: bool,
):
    """Linting commands."""
    if not no_uv_locked:
        run(["uv", "lock", "--locked"])
    if not no_py_style:
        if check:
            run(["ruff", "format", "--check", "--diff"])
            run(["ruff", "check"])
        else:
            run(["ruff", "format"])
            run(["ruff", "check", "--fix"])
    if not no_md_style:
        if check:
            run(
                [
                    "mdformat",
                    "--ignore-missing-references",
                    "--check",
                    "README.md",
                    "docs",
                ]
            )
            doc_cmd(["ruff", "format", "--check"], no_pad=True)
            doc_cmd(["ruff", "check"], no_pad=True)
        else:
            run(["mdformat", "--ignore-missing-references", "README.md", "docs"])
            doc_cmd(["ruff", "format"], no_pad=True)
            doc_cmd(["ruff", "check", "--fix"], no_pad=True)
    if not no_yml_style:
        if check:
            run(["yamlfix", "--check", "docs", ".github"])
        else:
            run(["yamlfix", "docs", ".github"])
    if not no_py_types:
        run(["pyright"])


@main.group("docs")
def docs():
    """Documentation commands."""


@docs.command("build")
def docs_build():
    """Build documentation."""
    run(["mkdocs", "build", "-f", "docs/mkdocs.yml"])


@docs.command("publish")
def docs_publish():
    """Publish documentation."""
    run(["mkdocs", "gh-deploy", "-f", "docs/mkdocs.yml"])


@docs.command("serve")
def docs_serve():
    """Serve documentation."""
    run(["mkdocs", "serve", "-f", "docs/mkdocs.yml"])


@docs.command("fix")
def fix():
    """Fix style issues."""
    run(["pytest", "tests/test_docs.py", "--update-examples"])


if TYPE_CHECKING:
    run = subprocess.run
else:

    def run(*args, **kwargs):
        cmd, *args = args
        cmd = tuple(map(str, cmd))
        kwargs.setdefault("check", True)
        click.echo(click.style(" ".join(cmd), bold=True))
        try:
            return subprocess.run(cmd, *args, **kwargs)
        except subprocess.CalledProcessError as e:
            raise click.ClickException(e) from None
        except FileNotFoundError as e:
            msg = f"File not found {e}"
            raise click.ClickException(msg) from None


def report(
    kind: Literal["notice", "warning", "error"],
    /,
    *,
    title: str = "",
    message: str = "",
    file: str | None = None,
    line: int | None = None,
    end_line: int | None = None,
    col: int | None = None,
    end_col: int | None = None,
):
    if not IN_CI:
        file_parts = []
        if file:
            file_parts.append(f"{file}")
            if line:
                file_parts.append(f":{line}")
                if end_line:
                    file_parts.append(f"-{end_line}")
            if col:
                file_parts.append(f":{col}")
                if end_col:
                    file_parts.append(f"-{end_col}")
        file_info = "".join(file_parts)
        click.echo(" - ".join(filter(None, [kind.upper(), file_info, title, message])))
    else:
        file_parts = []
        if title or message:
            file_parts.append(f"{title}::{message}")
        if file:
            file_parts.append(f"file={file}")
            if line:
                file_parts.append(f"line={line}")
                if end_line:
                    file_parts.append(f"endLine={end_line}")
            if col:
                file_parts.append(f"col={col}")
                if end_col:
                    file_parts.append(f"endCol={end_col}")
        click.echo(f"::{kind} {','.join(file_parts)}")


def doc_cmd(cmd: Sequence[str], *, no_pad: bool = False):
    run(
        list(
            filter(
                None,
                [
                    "doccmd",
                    "-v",
                    "--language=python",
                    "--no-pad-file" if no_pad else "",
                    "--command",
                    " ".join(cmd),
                    "docs",
                ],
            )
        )
    )


if __name__ == "__main__":
    main()
