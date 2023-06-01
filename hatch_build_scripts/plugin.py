from __future__ import annotations

import logging
import os
import shutil
from dataclasses import MISSING, dataclass, fields
from functools import cached_property
from pathlib import Path
from subprocess import run
from typing import Any, Sequence

import pathspec
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

logger = logging.getLogger(__name__)


class BuildScriptsHook(BuildHookInterface):
    PLUGIN_NAME = "build-scripts"

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, Any],
    ) -> None:
        created: set[Path] = set()

        all_scripts = load_scripts(self.config)

        for script in all_scripts:
            if script.clean_out_dir:
                out_dir = Path(self.root, script.out_dir)
                logger.info(f"Cleaning {out_dir}")
                shutil.rmtree(out_dir, ignore_errors=True)
            elif script.clean_artifacts:
                for out_file in script.out_files(self.root):
                    out_file.unlink(missing_ok=True)

        for script in all_scripts:
            work_dir = Path(self.root, script.work_dir)
            out_dir = Path(self.root, script.out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

            for cmd in script.commands:
                run(cmd, cwd=str(work_dir), check=True, shell=True)  # noqa: S602

            logger.info(f"Copying artifacts to {out_dir}")
            for artifact_file in script.artifact_files():
                src_file = work_dir / artifact_file
                out_file = out_dir / artifact_file
                if src_file not in created:
                    out_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src_file, out_file)
                    created.add(out_file)

            build_data["artifacts"].append(str(out_dir.relative_to(self.root)))

        print(build_data["artifacts"])


def load_scripts(config: dict[str, Any]) -> Sequence[OneScriptConfig]:
    script_defaults = dataclass_defaults(OneScriptConfig)
    script_defaults.update({k: config[k] for k in script_defaults if k in config})
    return [
        OneScriptConfig(**{**script_defaults, **script_config})
        for script_config in config.get("scripts", [])
    ]


@dataclass
class OneScriptConfig:
    """A configuration for a single build script."""

    commands: Sequence[str]
    """The commands to run"""

    artifacts: Sequence[str]
    """Git file patterns relative to the work_dir to save as build artifacts"""

    out_dir: str = "."
    """The path where build artifacts will be saved"""

    work_dir: str = "."
    """The path where the build script will be run"""

    clean_artifacts: bool = True
    """Whether to clean the build directory before running the scripts"""

    clean_out_dir: bool = False
    """Whether to clean the output directory before running the scripts"""

    def __post_init__(self) -> None:
        self.out_dir = conv_path(self.out_dir)
        self.work_dir = conv_path(self.work_dir)

    def work_files(self, root: str | Path) -> Sequence[Path]:
        """Get the files that will be used by the script."""
        work_dir = Path(root, self.work_dir)
        if not work_dir.exists():
            return []
        return [Path(root, self.work_dir, f) for f in self.artifacts_spec.match_tree(work_dir)]

    def out_files(self, root: str | Path) -> Sequence[Path]:
        """Get the files that will be created by the script."""
        out_dir = Path(root, self.out_dir)
        if not out_dir.exists():
            return []
        return [Path(root, self.out_dir, f) for f in self.artifacts_spec.match_tree(out_dir)]

    def artifact_files(self) -> Sequence[Path]:
        return [Path(conv_path(p)) for p in self.artifacts_spec.match_tree(self.work_dir)]

    @cached_property
    def artifacts_spec(self) -> pathspec.PathSpec:
        """A pathspec for the artifacts."""
        return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, self.artifacts)


def dataclass_defaults(obj: Any) -> dict[str, Any]:
    defaults: dict[str, Any] = {}
    for f in fields(obj):
        if f.default is not MISSING:
            defaults[f.name] = f.default
        elif f.default_factory is not MISSING:
            defaults[f.name] = f.default_factory()
    return defaults


def conv_path(path: str) -> str:
    """Convert a unix path to a platform-specific path."""
    return path.replace("/", os.sep)
