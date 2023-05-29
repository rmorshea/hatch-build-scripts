"""Register hooks for the plugin."""
from hatchling.plugin import hookimpl

from .plugin import BuildScriptsHook


@hookimpl
def hatch_register_build_hook():
    """Get the hook implementation."""
    return BuildScriptsHook
