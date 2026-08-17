# PyInstaller specification for the odesuite studio.
#
#   py -3.10 -m PyInstaller packaging/odesuite.spec --noconfirm
#
# Produces a one-folder distribution under dist/odesuite-studio/. One-folder
# rather than one-file: a single executable has to unpack ~200 MB of Qt and
# scientific libraries into a temporary directory on every launch, which turns
# a one-second start into ten.
#
# Two things need help from the spec. Qt's platform plugins are loaded by name
# at runtime, so PyInstaller's import analysis cannot see them; and neither
# scipy's compiled solver internals nor sympy's printing back-ends are reached
# by a static import graph either.

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).parent

hidden = [
    # Imported lazily by the library and the app.
    "odesuite", "odesuite_app",
    "scipy.special.cython_special",
    "scipy.sparse.linalg._isolve",
    "scipy.integrate",
    "sympy.printing.lambdarepr",
    "sympy.printing.numpy",
    "pyqtgraph.graphicsItems.PlotItem",
    "pyqtgraph.exporters",
]
hidden += collect_submodules("odesuite")
hidden += collect_submodules("odesuite_app")

# matplotlib is used off-thread for thumbnails and contour extraction, always
# through the Agg backend; the interactive ones only bloat the bundle.
excluded = [
    "tkinter", "PyQt5", "PyQt6", "PySide2", "IPython", "jupyter",
    "notebook", "pytest", "matplotlib.backends.backend_qt5agg",
    "matplotlib.backends.backend_qtagg",
    # sympy.lambdify can emit code for torch, tensorflow and jax, and imports
    # them behind try/except to find out. Static analysis cannot tell an
    # optional backend from a required one, so torch alone was contributing
    # 263 MB -- more than everything else in the bundle combined.
    "torch", "tensorflow", "jax", "jaxlib", "numba", "cupy",
]

# Qt ships a great deal this application never touches -- a browser engine, a
# QML runtime, 3D and multimedia stacks. Left in, they roughly triple the
# bundle. Only QtCore, QtGui and QtWidgets are actually used.
excluded += [
    f"PySide6.{module}"
    for module in (
        "QtWebEngineCore", "QtWebEngineWidgets", "QtWebEngineQuick",
        "QtQuick", "QtQuick3D", "QtQuickWidgets", "QtQml", "QtQmlModels",
        "Qt3DCore", "Qt3DRender", "Qt3DInput", "Qt3DLogic", "Qt3DAnimation",
        "Qt3DExtras", "QtMultimedia", "QtMultimediaWidgets", "QtCharts",
        "QtDataVisualization", "QtGraphs", "QtPdf", "QtPdfWidgets",
        "QtSql", "QtTest", "QtDesigner", "QtHelp", "QtBluetooth",
        "QtLocation", "QtPositioning", "QtSerialPort", "QtSensors",
        "QtNfc", "QtWebSockets", "QtWebChannel", "QtRemoteObjects",
        "QtScxml", "QtSpatialAudio", "QtTextToSpeech", "QtHttpServer",
    )
]

analysis = Analysis(
    [str(ROOT / "packaging" / "launch.py")],
    pathex=[str(ROOT / "src")],
    binaries=[],
    datas=collect_data_files("pyqtgraph") + collect_data_files("sympy"),
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=excluded,
    noarchive=False,
)

# `excludes` filters Python modules only; Qt arrives as DLLs and plugin
# directories that no import statement references, so the unused ones have to
# be dropped from the binary and data lists directly.
_UNUSED_BINARIES = (
    "Qt6WebEngine", "Qt6Quick", "Qt6Qml", "Qt63D", "Qt6Multimedia",
    "Qt6Charts", "Qt6DataVisualization", "Qt6Graphs", "Qt6Pdf", "Qt6Sql",
    "Qt6Test", "Qt6Designer", "Qt6Help", "Qt6Bluetooth", "Qt6Location",
    "Qt6Positioning", "Qt6SerialPort", "Qt6Sensors", "Qt6Nfc",
    "Qt6WebSockets", "Qt6WebChannel", "Qt6RemoteObjects", "Qt6Scxml",
    "Qt6SpatialAudio", "Qt6TextToSpeech", "Qt6HttpServer", "Qt6Quick3D",
    "opengl32sw",          # a software GL fallback pyqtgraph does not need
    "_avif",               # PIL codecs unused here
    "_webp", "_heif",
)


def _keep(entry) -> bool:
    name = entry[0].replace("\\", "/")
    return not any(token.lower() in name.lower() for token in _UNUSED_BINARIES)


analysis.binaries = TOC([entry for entry in analysis.binaries if _keep(entry)])
analysis.datas = TOC([entry for entry in analysis.datas if _keep(entry)])

pyz = PYZ(analysis.pure, analysis.zipped_data)

executable = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="odesuite-studio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,          # a GUI application; no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

COLLECT(
    executable,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="odesuite-studio",
)
