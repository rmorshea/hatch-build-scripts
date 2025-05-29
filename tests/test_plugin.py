from hatch_build_scripts.plugin import OneScriptConfig

from .utils import create_project


def test_plugin(tmpdir):
    tmp_lib_dir = tmpdir / "lib"
    tmp_lib_dir.mkdir()

    (tmp_lib_dir / "some-dir").mkdir()
    (tmp_lib_dir / "another-dir").mkdir()
    (tmp_lib_dir / "yet-another-dir").mkdir()

    some_dir_out = tmp_lib_dir / "some-dir-out"
    some_dir_out.mkdir()
    # we expect that this file will not be cleaned
    (some_dir_out / "module.py").write_text('print("hello")', "utf-8")
    # we expect that this file will be cleaned
    (some_dir_out / "f3.txt").write_text("this should be cleaned", "utf-8")

    another_dir_out = tmp_lib_dir / "another-dir-out"
    another_dir_out.mkdir()
    # we expect that this file will be cleaned
    (another_dir_out / "module.py").write_text('print("hello")', "utf-8")

    proj = create_project(
        tmp_lib_dir,
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
            OneScriptConfig(
                out_dir="yet-another-dir-out",
                work_dir="yet-another-dir",
                commands=[
                    "echo 'hello world' > f1.txt",
                    "echo 'hello world' > f2.txt",
                ],
                artifacts=["*.txt"],
                clean_out_dir=True,
                clean_artifacts_after_build=True,
            ),
        ],
    )

    proj.build()

    extract_dir = tmpdir / "extract"
    extract_dir.mkdir()

    with proj.dist() as dist:
        dist.extractall(extract_dir)

        assert (extract_dir / "fake" / "fake.txt").exists()
        assert (extract_dir / "some-dir-out" / "module.py").exists()

        assert not (extract_dir / "some-dir-out" / "f3.txt").exists()
        assert not (extract_dir / "another-dir-out" / "module.py").exists()

        # we expect that this file still exists in the source
        assert (tmp_lib_dir / "fake" / "fake.txt").exists()
        # we expect that this file was cleaned in the source but exists in wheel
        assert (extract_dir / "yet-another-dir-out" / "f1.txt").exists()
        assert not (tmp_lib_dir / "yet-another-dir-out" / "f1.txt").exists()
