# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hidden_imports = collect_submodules('django')
hidden_imports += [
    'attendance_app.apps',
    'attendance_app.urls',
    'attendance_app.forms',
    'attendance_app.models',
    'attendance_app.views',
    'webview',
    'webview.platforms.winforms',
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('attendance_app/templates', 'attendance_app/templates'),
        ('attendance_app/static', 'attendance_app/static'),
        ('db.sqlite3', '.'), 
    ],
    hiddenimports=hidden_imports,
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

# FOLDER MODE CONFIGURATION
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True, 
    name='AttendanceSystem',
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AttendanceSystem',
)