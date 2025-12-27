# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
root_dir = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    ['..\\run_viewer.py'],
    pathex=[root_dir],
    binaries=[],
    datas=[
        ('..\\sem_view\\gui\\resources\\*.png', 'sem_view/gui/resources'),
        ('..\\sem_view\\gui\\resources\\icon.ico', 'sem_view/gui/resources'),
    ],
    hiddenimports=[],
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
    name='SEM Viewer',
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
    icon='..\\sem_view\\gui\\resources\\icon.ico'
)
