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
GENERATED = ("index.md", "license.md", "security.md", "figures")


def on_pre_build(config, **kwargs) -> None:
    DOCS.mkdir(exist_ok=True)

    # Links that have to be right in two places at once. A path is written in
    # the README as a reader of the *repository* would need it, and the README
    # becomes the site's home page, where the same path is wrong: `docs/` is
    # already the root there, and `LICENSE` is not a page at all. Repointing
    # them here keeps one sentence correct in both, which is the whole reason
    # this hook exists rather than a second hand-written home page.
    #
    # `mkdocs build --strict` fails on a link it cannot resolve, so a new
    # `docs/…` link in the README that is not listed here breaks the build
    # rather than shipping dead.
    LINK_REWRITES = {
        "](LICENSE)": "](license.md)",
        "](SECURITY.md)": "](security.md)",
        "](docs/limits.md)": "](limits.md)",
    }

    # The security policy is markdown already, so it needs staging rather than
    # wrapping. Published because "how do I report this" is a question a reader
    # of the site has as readily as a reader of the repository.
    policy = ROOT / "SECURITY.md"
    if policy.is_file():
        (DOCS / "security.md").write_text(
            policy.read_text(encoding="utf-8"), encoding="utf-8"
        )

    licence = ROOT / "LICENSE"
    if licence.is_file():
        (DOCS / "license.md").write_text(
            "# License\n\n```\n" + licence.read_text(encoding="utf-8") + "```\n",
            encoding="utf-8",
        )

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    for repository_link, site_link in LINK_REWRITES.items():
        text = text.replace(repository_link, site_link)
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
