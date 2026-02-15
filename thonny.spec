# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata
import os

# Try to locate PyQt5 plugins (User Suggestion)
qt_datas = []
qt_hiddenimports = []
try:
    import PyQt5
    pyqt5_path = os.path.dirname(PyQt5.__file__)
    qt_plugin_src = os.path.join(pyqt5_path, 'Qt5', 'plugins')
    if os.path.isdir(qt_plugin_src):
        qt_datas.append((qt_plugin_src, 'PyQt5/Qt5/plugins'))
        qt_hiddenimports.append('PyQt5.sip')
        qt_hiddenimports.append('PyQt5.QtCore')
        qt_hiddenimports.append('PyQt5.QtWidgets')
        qt_hiddenimports.append('PyQt5.uic')
except ImportError:
    pass

block_cipher = None

# Friendly traceback data collection removed
friendly_datas = []


# Collect metadata for packages that query their version at runtime
metadata_datas = []
packages_with_metadata = [
    'thonny',
    'asttokens',
    'jedi',
    'docutils',
    'Send2Trash',
    'packaging',
]

for package in packages_with_metadata:
    try:
        metadata_datas += copy_metadata(package)
    except Exception:
        pass  # Package might not be installed

# Collect all submodules
friendly_hiddenimports = []
thonny_hiddenimports = collect_submodules('thonny')
jedi_hiddenimports = collect_submodules('jedi')
parso_hiddenimports = collect_submodules('parso')

a = Analysis(
    ['thonny/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('thonny', 'thonny'),
        ('local_plugins/thonnycontrib', 'thonnycontrib'),  # Include fixed plugins
    ] + metadata_datas + qt_datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.messagebox',
        'xml',
        'xml.dom',
        'xml.dom.minidom',
        'xml.dom.minidom',

        'thonnycontrib.tunisiaschools',
        'thonnycontrib.thonny_simple_autocomplete',
        'thonnycontrib.thonny_autosave',
        'thonnycontrib.thonny_quick_switch',
        'pkg_resources.py2_warn',
        # Code completion
        'jedi',
        'parso',
        # ESP32/ESP8266 MicroPython support
        'esptool',
        'esptool.cmds',
        'esptool.targets',
        'esptool.loader',
        'serial',
        'serial.tools',
        'serial.tools.list_ports',
        'serial.tools.list_ports_windows',
        # adafruit board toolkit for faster serial port detection
        'adafruit_board_toolkit',
        'adafruit_board_toolkit._list_ports_windows',
        'PyQt5.sip',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.uic',
    ] + thonny_hiddenimports + jedi_hiddenimports + parso_hiddenimports + qt_hiddenimports,
    hookspath=[os.path.abspath('.')],  # Use custom hooks from current directory
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # Key change: Don't bundle everything into one EXE
    name='Thonny',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='thonny/res/thonny.ico',
)

# Create directory-based distribution (onedir mode)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Thonny',
)
