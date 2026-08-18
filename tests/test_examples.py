"""Every example is executed, and must succeed.

Documentation that has never been run is the most common kind of wrong
documentation. This project already applies that standard to the studio -- the
"copy as code" button's output is executed to prove it runs -- and the same
argument applies with more force to `examples/`, which is the first thing
someone reads and the last thing anyone remembers to update.

The examples are not smoke tests dressed up as prose: each one asserts something
about its own result (a conserved quantity, an event time against a closed form,
a measured convergence order), so running them checks the library rather than
merely checking that they do not crash.

Writing this file caught three examples that had been written against APIs I had
assumed rather than read, and one -- `08` -- that borrowed an embedded pair from
a different tableau, giving weights summing to 0.875. That is the same class of
defect as the ROS3P estimator in the README's "bugs worth recording": the solver
did not produce a wrong answer, it failed to converge at all.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parent.parent / "examples"
EXAMPLES = sorted(EXAMPLES_DIR.glob("[0-9]*.py"))

# Anything above a couple of seconds; keeps the default loop quick.
SLOW = {"06_sensitivities", "07_symplectic_energy"}


def _ids(path: Path) -> str:
    return path.stem


def test_the_examples_directory_is_not_empty():
    """A glob that silently matches nothing would make every test below pass."""
    assert EXAMPLES, f"no examples found in {EXAMPLES_DIR}"
    assert len(EXAMPLES) >= 8


@pytest.mark.parametrize("path", EXAMPLES, ids=_ids)
def test_example_runs(path: Path, request):
    if path.stem in SLOW:
        request.applymarker(pytest.mark.slow)

    completed = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=str(path.parent.parent),
    )

    if completed.returncode != 0:
        pytest.fail(
            f"{path.name} exited {completed.returncode}\n"
            f"--- stdout ---\n{completed.stdout}\n"
            f"--- stderr ---\n{completed.stderr}"
        )
    assert completed.stdout.strip(), f"{path.name} printed nothing"


@pytest.mark.parametrize("path", EXAMPLES, ids=_ids)
def test_example_documents_how_to_run_itself(path: Path):
    """Each example opens with a docstring naming its own invocation. Cheap to
    check, and it is the line people actually copy."""
    text = path.read_text(encoding="utf-8")
    assert text.startswith('"""'), f"{path.name} should open with a docstring"
    assert f"examples/{path.name}" in text, (
        f"{path.name}'s docstring should show how to run it"
    )


def test_examples_use_only_the_public_api():
    """An example reaching into a private module is a sign the public surface is
    missing something -- which is worth knowing before a user finds out."""
    offenders = []
    for path in EXAMPLES:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not stripped.startswith(("import ", "from ")):
                continue
            if "odesuite._" in stripped or "from odesuite." in stripped:
                # `from odesuite.problems import ...` is fine; private ones are not.
                if "._" in stripped or ".steppers." in stripped:
                    offenders.append(f"{path.name}:{line_number}: {stripped}")
    assert not offenders, "examples should import from the package root:\n" + "\n".join(
        offenders
    )
