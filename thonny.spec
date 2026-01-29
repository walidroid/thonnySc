# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata
import os

block_cipher = None

# Collect friendly_traceback data files (locales)
friendly_datas = collect_data_files('friendly_traceback')

# Collect metadata for packages that query their version at runtime
metadata_datas = []
packages_with_metadata = [
    'thonny',
    'friendly_traceback',
    'asttokens',
    'jedi',
    'pylint',
    'mypy',
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
friendly_hiddenimports = collect_submodules('friendly_traceback')
thonny_hiddenimports = collect_submodules('thonny')

a = Analysis(
    ['thonny/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('thonny', 'thonny'),
        ('local_plugins/thonnycontrib', 'thonnycontrib'),  # Include fixed plugins
    ] + friendly_datas + metadata_datas,
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        'tkinter.messagebox',
        'friendly_traceback',
        'thonnycontrib.thonny_friendly',
        'thonnycontrib.tunisiaschools',
        'thonnycontrib.thonny_simple_autocomplete',
        'thonnycontrib.thonny_quick_switch',
        'pkg_resources.py2_warn',
    ] + friendly_hiddenimports + thonny_hiddenimports,
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
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
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
