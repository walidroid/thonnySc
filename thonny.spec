# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata
import os
import sys

# Ensure pure Python environment for build
block_cipher = None

# Collect metadata for packages
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
        pass

# Collect submodules
friendly_hiddenimports = []
thonny_hiddenimports = collect_submodules('thonny')
jedi_hiddenimports = collect_submodules('jedi')
parso_hiddenimports = collect_submodules('parso')

# Collect Qt/Tkinter data explicitly to ensure bundling
qt_datas = []
# Try to find standard tkinter data if PyInstaller misses it
try:
    import tkinter
    tk_path = os.path.dirname(tkinter.__file__)
    # Add tkinter package files
    # qt_datas.append((tk_path, 'tkinter')) # PyInstaller usually handles this
except ImportError:
    pass

a = Analysis(
    ['thonny/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('thonny', 'thonny'),
        ('local_plugins/thonnycontrib', 'thonnycontrib'), 
    ] + metadata_datas + qt_datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.commondialog',
        'tkinter.simpledialog',
        'tkinter.scrolledtext',
        'xml',
        'xml.parsers.expat',
        
        # Plugins / Contrib
        'thonnycontrib.tunisiaschools',
        'thonnycontrib.thonny_simple_autocomplete',
        'thonnycontrib.thonny_autosave',
        'thonnycontrib.thonny_quick_switch',
        
        # Core Deps
        'jedi',
        'parso',
        'esptool',
        'serial',
        'serial.tools.list_ports',
        'adafruit_board_toolkit',
        
        # PyQt5 specific
        'PyQt5',
        'PyQt5.sip',
        'PyQt5.QtCore',
        'PyQt5.QtWidgets',
        'PyQt5.QtGui',
        'PyQt5.uic',
    ] + thonny_hiddenimports + jedi_hiddenimports + parso_hiddenimports,
    hookspath=[],
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
    exclude_binaries=True,
    name='Thonny',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='thonny/res/thonny.ico',
)

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
