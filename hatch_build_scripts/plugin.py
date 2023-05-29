from __future__ import annotations
from dataclasses import dataclass
import os
import shutil

import pathspec
from pathlib import Path
import logging
from subprocess import run
from typing import Any, Sequence

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


logger = logging.getLogger(__name__)


class BuildScriptsHook(BuildHookInterface):
    PLUGIN_NAME = "build-scripts"

    def initialize(self, version: str, build_data: dict[str, Any]) -> bool | None:
        created: set[Path] = set()
        for script in load_scripts(self.config):
            work_dir = Path(self.root, conv_path(script.work_dir))
            out_dir = Path(self.root, conv_path(script.out_dir))
            out_dir.mkdir(parents=True, exist_ok=True)

            for cmd in script.commands:
                run(cmd, cwd=str(work_dir), check=True, shell=True)

            logger.info(f"Copying artifacts to {out_dir}")
            spec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, list(map(conv_path, script.artifacts))
            )

            for file in map(Path, spec.match_tree(work_dir)):
                src_file = work_dir / file
                out_file = out_dir / file
                if src_file not in created:
                    shutil.copyfile(src_file, out_file)
                    created.add(out_file)

            build_data["artifacts"].append(str(out_dir.relative_to(self.root)))


def load_scripts(config: dict[str, Any]) -> Sequence[ScriptConfig]:
    return [ScriptConfig(**s) for s in config.get("scripts", [])]


def conv_path(path: str) -> str:
    """Convert a unix path to a platform-specific path."""
    return path.replace("/", os.sep)


@dataclass
class ScriptConfig:
    out_dir: str
    """The path where build artifacts will be saved"""

    commands: Sequence[str]
    """The commands to run"""

    artifacts: Sequence[str]
    """A list of file patterns relative to the work_dir to save as build artifacts"""

    work_dir: str = "."
    """The path where the build script will be run"""
