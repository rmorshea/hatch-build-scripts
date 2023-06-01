from os.path import join as joinpath

from hatch_build_scripts.plugin import OneScriptConfig

from .utils import create_project


def test_plugin(tmpdir):
    (tmpdir / "some-dir").mkdir()
    (tmpdir / "another-dir").mkdir()

    some_dir_out = tmpdir / "some-dir-out"
    some_dir_out.mkdir()
    # we expect that this file will not be cleaned
    (some_dir_out / "module.py").write_text('print("hello")', "utf-8")
    # we expect that this file will be cleaned
    (some_dir_out / "f3.txt").write_text("this should be cleaned", "utf-8")

    another_dir_out = tmpdir / "another-dir-out"
    another_dir_out.mkdir()
    # we expect that this file will be cleaned
    (another_dir_out / "module.py").write_text('print("hello")', "utf-8")

    proj = create_project(
        tmpdir,
        [
            OneScriptConfig(
                out_dir="fake",
                commands=["echo 'hello world' > fake.txt"],
                artifacts=["fake.txt"],
            ),
            OneScriptConfig(
                out_dir="some-dir-out",
                work_dir="some-dir",
                commands=[
                    "echo 'hello world' > f1.txt",
                    "echo 'hello world' > f2.txt",
                ],
                # this will not clean the data.json file
                artifacts=["*.txt"],
            ),
            OneScriptConfig(
                out_dir="another-dir-out",
                work_dir="another-dir",
                commands=[
                    "echo 'hello world' > f1.txt",
                    "echo 'hello world' > f2.txt",
                ],
                artifacts=["*.txt"],
                clean_out_dir=True,
            ),
        ],
    )

    proj.build()

    with proj.dist() as dist:
        files = {file.filename for file in dist.filelist}

        assert joinpath("fake", "fake.txt") in files
        assert joinpath("some-dir-out", "module.py") in files
        assert joinpath("another-dir-out", "module.py") not in files
        assert joinpath("some-dir-out", "f3.txt") not in files
