from __future__ import annotations

from pathlib import Path
import subprocess
import sys
from typing import Sequence, Iterator
import toml
import zipfile
from dataclasses import asdict
from contextlib import contextmanager

import hatch_build_scripts
from hatch_build_scripts.plugin import ScriptConfig


ROOT_DIR = Path(__file__).parent.parent


def create_project(path: Path | str, scripts: Sequence[ScriptConfig]) -> FakeProject:
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
            [sys.executable, "-m", "pip", "cache", "remove", hatch_build_scripts.__name__], cwd=self.path, check=True
        )
        subprocess.run([sys.executable, "-m", "hatch", "build"], cwd=self.path, check=True)

    @contextmanager
    def dist(self) -> Iterator[zipfile.ZipFile]:
        files = list((self.path / "dist").glob("*.whl"))
        assert len(files) == 1
        with zipfile.ZipFile(str(files[0])) as whl:
            yield whl
