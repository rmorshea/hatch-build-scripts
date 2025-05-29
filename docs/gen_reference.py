from pathlib import Path

from mkdocs_gen_files.editor import FilesEditor
from mkdocs_gen_files.nav import Nav


def editor() -> FilesEditor:
    return FilesEditor.current()


nav = Nav()
mod_symbol = '<code class="doc-symbol doc-symbol-nav doc-symbol-module"></code>'

root = Path(__file__).parent.parent
src = root / "src"

for path in sorted(src.rglob("*.py")):
    module_path = path.relative_to(src).with_suffix("")
    doc_path = path.relative_to(src / "hatch_build_scripts").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    if parts[-1] == "__init__" or parts[-1].startswith("_"):
        continue

    nav_parts = [f"{mod_symbol} {part}" for part in parts]
    nav[tuple(nav_parts)] = doc_path.as_posix()

    with editor().open(str(full_doc_path), "w") as fd:
        ident = ".".join(parts)
        fd.write(f"---\ntitle: {ident}\n---\n\n::: {ident}")

    editor().set_edit_path(str(full_doc_path), str(".." / path.relative_to(root)))

with editor().open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
