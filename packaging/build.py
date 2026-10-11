"""Build the studio as a download, and refuse to ship one that does not work.

    py -3.10 packaging/build.py

Builds `packaging/odesuite.spec`, checks the frozen application, and zips it as
``dist/odesuite-studio-<version>-<platform>.zip``: the file a student downloads,
unzips and double-clicks, with no Python involved.

The checks exist because a frozen build fails in ways the test suite cannot
see. The suite runs from source, where every import resolves; PyInstaller finds
imports by static analysis and silently leaves out whatever it cannot trace. Two
checks cover the two halves of the application:

* ``--selftest`` solves the catalogue's problems and typesets an equation, all
  inside the frozen process: the numerical half, plus matplotlib's fonts.
* A closed form is found through the frozen ``--dsolve-worker``. Every symbolic
  answer in the Learning Hub comes from that subprocess, and `--selftest` never
  starts it. It is driven through `symbolic.solve_symbolically` itself with only
  the command swapped, so the payload is the one the application really sends.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
APP = DIST / "odesuite-studio"
sys.path.insert(0, str(ROOT / "src"))


def executable() -> Path:
    name = "odesuite-studio.exe" if sys.platform == "win32" else "odesuite-studio"
    return APP / name


def build() -> None:
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", str(ROOT / "packaging" / "odesuite.spec"),
         "--noconfirm", "--distpath", str(DIST), "--workpath", str(ROOT / "build")],
        check=True,
    )


def check_selftest() -> None:
    with tempfile.TemporaryDirectory() as scratch:
        report = Path(scratch) / "selftest.txt"
        status = subprocess.run([str(executable()), "--selftest", str(report)],
                                timeout=600).returncode
        text = report.read_text(encoding="utf-8") if report.exists() else "(no report)"
    print(text)
    if status != 0:
        raise SystemExit(f"frozen --selftest failed with status {status}")


def check_symbolic_worker() -> None:
    from odesuite_app import symbolic
    from odesuite_app.symbolic import EquationSpec, parse_equation

    symbolic._worker_command = lambda: [str(executable()), "--dsolve-worker"]
    solution = symbolic.solve_symbolically(
        parse_equation(EquationSpec(equations=["y'' + 2*y' + 5*y = 0"])),
        timeout=120.0,
    )
    general = getattr(solution, "general", None)
    if general is None or "exp(-t)" not in str(general):
        raise SystemExit(f"frozen --dsolve-worker gave no closed form: {solution!r}")
    print(f"frozen --dsolve-worker: y = {general}")


def package() -> Path:
    from odesuite import __version__

    system = {"win32": "windows", "darwin": "macos"}.get(sys.platform, sys.platform)
    stem = DIST / f"odesuite-studio-{__version__}-{system}-{platform.machine().lower()}"
    archive = shutil.make_archive(str(stem), "zip", root_dir=DIST,
                                  base_dir=APP.name)
    return Path(archive)


def main() -> None:
    build()
    check_selftest()
    check_symbolic_worker()
    archive = package()
    print(f"{archive}  {archive.stat().st_size / 2**20:.0f} MB")


if __name__ == "__main__":
    main()
