# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files
import os

datas = []
binaries = []
hiddenimports = []

# Collect everything for key packages
packages = ['skimage', 'scipy', 'imageio', 'networkx', 'lazy_loader', 'tifffile']
for package in packages:
    try:
        tmp_ret = collect_all(package)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except Exception as e:
        print(f"Warning: Failed to collect {package}: {e}")

# Explicitly add some that might be missed by collect_all if it fails
hiddenimports += [
    'skimage.draw',
    'skimage.filters',
    'skimage.measure',
    'skimage.morphology',
    'skimage.util',
    'skimage.io',
    'scipy.ndimage',
    'scipy.signal',
    'scipy.spatial',
]

block_cipher = None
root_dir = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    ['..\\run_viewer.py'],
    pathex=[root_dir],
    binaries=binaries,
    datas=datas + [
        ('..\\sem_view\\gui\\resources\\*.png', 'sem_view/gui/resources'),
        ('..\\sem_view\\gui\\resources\\icon.ico', 'sem_view/gui/resources'),
    ],
    hiddenimports=hiddenimports,
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
    name='SEM_Viewer_Plus',
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
