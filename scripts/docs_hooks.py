"""mkdocs build hook: reuse the README instead of duplicating it.

The README is the best writing in this project, and a documentation site whose
home page is a second, drifting copy of it is worse than no site. So the build
copies `README.md` to `docs/index.md` and `figures/` to `docs/figures/` before
mkdocs reads them, and both copies are git-ignored.

Copying rather than symlinking because symlinks need elevation on Windows, and
a hook rather than a plugin because this is fifteen lines and a plugin is a
dependency.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

#: Written by this hook, so `.gitignore` lists them.
GENERATED = ("index.md", "license.md", "figures")


def on_pre_build(config, **kwargs) -> None:
    DOCS.mkdir(exist_ok=True)

    # The README links to `LICENSE`, a plain file that means nothing to a static
    # site. Publish it as a page and repoint the link, so the same sentence is
    # correct in the repository and in the docs.
    licence = ROOT / "LICENSE"
    if licence.is_file():
        (DOCS / "license.md").write_text(
            "# License\n\n```\n" + licence.read_text(encoding="utf-8") + "```\n",
            encoding="utf-8",
        )

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8").replace("](LICENSE)", "](license.md)")
    (DOCS / "index.md").write_text(text, encoding="utf-8")

    figures = ROOT / "figures"
    if figures.is_dir():
        destination = DOCS / "figures"
        if destination.exists():
            shutil.rmtree(destination)
        # The JSON result file is data, not an asset; the site only needs images.
        shutil.copytree(
            figures, destination, ignore=shutil.ignore_patterns("*.json")
        )

    print(f"  docs_hooks: staged README.md and figures/ into {DOCS}")
