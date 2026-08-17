"""Home-screen thumbnails: one small picture per problem.

Each is a real solve rendered to a PNG, not an icon -- so the card grid is a
gallery of what the library actually produces. They are generated once, cached
on disk, and reused; regenerating twenty of them takes a few seconds, which is
too long to spend on every launch but fine once.

Rendering uses matplotlib's Agg backend rather than pyqtgraph because this
happens off the GUI thread and must not touch Qt at all -- and a bare `Figure`
rather than pyplot, because pyplot's figure registry and `matplotlib.use` are
global state that a worker thread must not mutate.
"""

from __future__ import annotations

import hashlib
import io
from pathlib import Path

import numpy as np

from odesuite import solve

from .catalog import CATALOG, CatalogEntry, preview_curves
from .theme import Palette

__all__ = ["cache_dir", "thumbnail_path", "render_thumbnail", "ensure_all"]

#: Bump when the rendering changes, so stale caches are ignored rather than
#: silently reused.
_VERSION = "1"


def cache_dir() -> Path:
    """Per-user cache directory, created on demand."""
    try:
        from PySide6.QtCore import QStandardPaths

        base = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        root = Path(base) if base else Path.home() / ".cache" / "odesuite_app"
    except Exception:
        root = Path.home() / ".cache" / "odesuite_app"
    path = root / "thumbnails"
    path.mkdir(parents=True, exist_ok=True)
    return path


def thumbnail_path(entry: CatalogEntry, palette: Palette) -> Path:
    token = hashlib.md5(
        f"{_VERSION}:{entry.key}:{palette.name}".encode()
    ).hexdigest()[:12]
    return cache_dir() / f"{entry.key}-{palette.name}-{token}.png"


def _preview_solution(entry: CatalogEntry):
    """A quick, deliberately coarse solve -- enough to show the shape."""
    params = entry.defaults()

    # Trim the expensive problems: a thumbnail does not need eleven decades of
    # Robertson or two thousand Kepler orbits.
    trims = {
        "robertson": {"log_t_end": 5.0},
        "robertson_dae": {"log_t_end": 5.0},
        "kepler_symplectic": {"n_orbits": 6.0},
        "kuramoto_sivashinsky": {"n_modes": 64, "t_end": 60.0},
        "allen_cahn": {"n_modes": 64, "t_end": 20.0},
        "hires": {"t_end": 321.8122},
        "van_der_pol": {"mu": 2.0, "t_end": 25.0},
    }
    params.update(trims.get(entry.key, {}))

    bench = entry.build(params)
    if entry.default_method in ("verlet", "yoshida4", "yoshida6", "etdrk4"):
        solution = solve(bench.problem, method=entry.default_method, n_steps=4000)
    else:
        solution = solve(
            bench.problem, method=entry.default_method, rtol=1e-6, atol=1e-9,
            max_steps=200_000,
        )
    return bench, solution


def render_thumbnail(entry: CatalogEntry, palette: Palette,
                     size=(3.2, 2.0), dpi: int = 100) -> bytes:
    """Render one thumbnail and return the PNG bytes.

    A bare `Figure` with an Agg canvas, never pyplot. pyplot keeps a global
    registry of open figures, and `matplotlib.use` swaps the global backend --
    neither is safe to touch from a worker thread, which is exactly where this
    runs. The same reasoning produced `mathrender._render`; this function was
    left on pyplot when that one was written.
    """
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    figure = Figure(figsize=size, dpi=dpi)
    FigureCanvasAgg(figure)
    axes = figure.add_axes((0, 0, 1, 1))
    axes.set_facecolor(palette.surface)
    figure.patch.set_facecolor(palette.surface)
    axes.set_xticks([])
    axes.set_yticks([])
    for spine in axes.spines.values():
        spine.set_visible(False)

    try:
        bench, solution = _preview_solution(entry)
        if not solution.success:
            raise RuntimeError(solution.message)

        if entry.plot_kind == "spacetime":
            field = bench.to_real(solution.y)
            limit = float(np.abs(field).max()) or 1.0
            axes.imshow(
                field, aspect="auto", origin="lower", cmap="RdBu_r",
                vmin=-limit, vmax=limit,
            )
        else:
            curves = preview_curves(entry, solution)
            for index, (x, y) in enumerate(curves):
                axes.plot(
                    x, y, lw=1.4,
                    color=palette.series[index % len(palette.series)],
                    solid_capstyle="round",
                )
            if entry.plot_kind in ("phase", "orbit"):
                axes.set_aspect("equal", adjustable="datalim")
            axes.margins(0.08)
    except Exception as exc:                            # never break the grid
        axes.text(
            0.5, 0.5, f"preview unavailable\n{type(exc).__name__}",
            ha="center", va="center", fontsize=7, color=palette.text_muted,
            transform=axes.transAxes,
        )

    buffer = io.BytesIO()
    figure.savefig(buffer, format="png", facecolor=palette.surface)
    return buffer.getvalue()


def ensure_all(palette: Palette, keys=None, force: bool = False,
               progress=None) -> dict[str, Path]:
    """Generate any missing thumbnails, returning ``{key: path}``.

    Safe to call on a worker thread: it touches only matplotlib and the file
    system.
    """
    paths: dict[str, Path] = {}
    entries = [CATALOG[k] for k in (keys or CATALOG)]
    for index, entry in enumerate(entries):
        path = thumbnail_path(entry, palette)
        if force or not path.exists():
            try:
                path.write_bytes(render_thumbnail(entry, palette))
            except Exception:
                continue
        paths[entry.key] = path
        if progress is not None:
            progress(index + 1, len(entries), entry.key)
    return paths
