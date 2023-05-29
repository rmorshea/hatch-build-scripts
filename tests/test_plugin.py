from os.path import join as joinpath
from .utils import create_project

from hatch_build_scripts.plugin import ScriptConfig


def test_simple(tmpdir):
    proj = create_project(
        tmpdir,
        [
            ScriptConfig(
                out_dir="fake",
                commands=["echo 'hello world' > fake.txt"],
                artifacts=["fake.txt"],
            )
        ],
    )
    proj.build()

    with proj.dist() as dist:
        for file in dist.filelist:
            if file.filename == joinpath("fake", "fake.txt"):
                break
        else:
            assert False
