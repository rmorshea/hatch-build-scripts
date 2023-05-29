from __future__ import annotations

import subprocess
import sys
import zipfile
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Iterator, Sequence

import toml

import hatch_build_scripts
from hatch_build_scripts.plugin import OneScriptConfig

ROOT_DIR = Path(__file__).parent.parent


def create_project(path: Path | str, scripts: Sequence[OneScriptConfig]) -> FakeProject:
    path = Path(path)

    full_config = {
        "project": {
            "name": "test-project",
            "version": "0.0.0",
            "description": "A test project",
        },
        "build-system": {
            "requires": ["hatchling", f"hatch-build-scripts @ {ROOT_DIR.as_uri()}"],
            "build-backend": "hatchling.build",
        },
        "tool": {
            "hatch": {
                "build": {
                    "hooks": {
                        "build-scripts": {
                            "scripts": list(map(asdict, scripts)),
                        }
                    }
                }
            }
        },
    }

    (path / "pyproject.toml").write_text(toml.dumps(full_config), encoding="utf-8")

    return FakeProject(path)


class FakeProject:
    def __init__(self, path: Path) -> None:
        self.path = path

    def build(self) -> None:
        subprocess.run(
            [  # noqa: S603
                sys.executable,
                "-m",
                "pip",
                "cache",
                "remove",
                hatch_build_scripts.__name__,
            ],
            cwd=self.path,
            check=True,
        )
        subprocess.run(
            [sys.executable, "-m", "hatch", "build"], cwd=self.path, check=True  # noqa: S603
        )

    @contextmanager
    def dist(self) -> Iterator[zipfile.ZipFile]:
        files = list((self.path / "dist").glob("*.whl"))
        assert len(files) == 1
        with zipfile.ZipFile(str(files[0])) as whl:
            yield whl
