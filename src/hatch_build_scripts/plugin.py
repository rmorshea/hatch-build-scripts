from __future__ import annotations

import logging
import os
import shutil
from dataclasses import MISSING
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import fields
from functools import cached_property
from pathlib import Path
from subprocess import run
from typing import TYPE_CHECKING
from typing import Any

import pathspec
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

if TYPE_CHECKING:
    from collections.abc import Sequence

log = logging.getLogger(__name__)
log_level = logging.getLevelName(os.getenv("HATCH_BUILD_SCRIPTS_LOG_LEVEL", "INFO"))
log.setLevel(log_level)


class BuildScriptsHook(BuildHookInterface):
    """A build hook that runs custom scripts defined in the pyproject.toml."""

    PLUGIN_NAME = "build-scripts"

    def initialize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, Any],
    ) -> None:
        """Initialize the build hook."""
        created: set[Path] = set()

        all_scripts = load_scripts(self.config)

        for script in all_scripts:
            if script.clean_out_dir:
                out_dir = Path(self.root, script.out_dir)
                log.debug("Cleaning %s", out_dir)
                shutil.rmtree(out_dir, ignore_errors=True)
            elif script.clean_artifacts:
                for out_file in script.out_files(self.root):
                    log.debug("Cleaning %s", out_file)
                    out_file.unlink(missing_ok=True)

        for script in all_scripts:
            log.debug("Script config: %s", asdict(script))
            work_dir = Path(self.root, script.work_dir)
            out_dir = Path(self.root, script.out_dir)
            out_dir.mkdir(parents=True, exist_ok=True)

            for cmd in script.commands:
                log.info("Running command: %s", cmd)
                run(cmd, cwd=str(work_dir), check=True, shell=True)  # noqa: S602

            log.info("Copying artifacts to %s", out_dir)
            for work_file in script.work_files(self.root, relative=True):
                src_file = work_dir / work_file
                out_file = out_dir / work_file
                log.debug("Copying %s to %s", src_file, out_file)
                if src_file not in created and src_file != out_file:
                    out_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(src_file, out_file)
                    shutil.copystat(src_file, out_file)
                    created.add(out_file)
                else:
                    log.debug("Skipping %s - already exists", src_file)

            build_data["artifacts"].append(str(out_dir.relative_to(self.root)))

    def finalize(
        self,
        version: str,  # noqa: ARG002
        build_data: dict[str, Any],  # noqa: ARG002
        artifact_path: str,  # noqa: ARG002
    ) -> None:
        """Finalize the build hook."""
        all_scripts = load_scripts(self.config)

        for script in all_scripts:
            if not script.clean_artifacts_after_build:
                continue

            for out_file in script.out_files(self.root):
                log.debug("After build, cleaning %s", out_file)
                out_file.unlink(missing_ok=True)


def load_scripts(config: dict[str, Any]) -> Sequence[OneScriptConfig]:
    """Load the build scripts from the configuration."""
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

    artifacts: Sequence[str] = ()
    """Git file patterns relative to the work_dir to save as build artifacts"""

    out_dir: str = "."
    """The path where build artifacts will be saved"""

    work_dir: str = "."
    """The path where the build script will be run"""

    clean_artifacts: bool = True
    """Whether to clean the build directory before running the scripts"""

    clean_out_dir: bool = False
    """Whether to clean the output directory before running the scripts"""

    clean_artifacts_after_build: bool = False
    """Whether to clean the build directory after running the scripts"""

    def __post_init__(self) -> None:
        self.out_dir = conv_path(self.out_dir)
        self.work_dir = conv_path(self.work_dir)

    def work_files(self, root: str | Path, *, relative: bool = False) -> Sequence[Path]:
        """Get files in the work directory that match the artifacts spec."""
        abs_dir = Path(root, self.work_dir)
        if not abs_dir.exists():
            return []
        return [
            Path(f) if relative else abs_dir / f for f in self.artifacts_spec.match_tree(abs_dir)
        ]

    def out_files(self, root: str | Path, *, relative: bool = False) -> Sequence[Path]:
        """Get files in the output directory that match the artifacts spec."""
        abs_dir = Path(root, self.out_dir)
        if not abs_dir.exists():
            return []
        return [
            Path(f) if relative else abs_dir / f for f in self.artifacts_spec.match_tree(abs_dir)
        ]

    @cached_property
    def artifacts_spec(self) -> pathspec.PathSpec:
        """A pathspec for the artifacts."""
        return pathspec.PathSpec.from_lines(
            pathspec.patterns.gitwildmatch.GitWildMatchPattern, self.artifacts
        )


def dataclass_defaults(obj: Any) -> dict[str, Any]:
    """Get the default values for a dataclass."""
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
