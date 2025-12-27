# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
# Explicitly list hidden imports since collect_all failed for skimage/scipy in some envs
hiddenimports = [
    'skimage',
    'skimage.draw',
    'skimage.filters',
    'skimage.measure',
    'skimage.morphology',
    'skimage.util',
    'scipy',
    'scipy.ndimage',
    'scipy.signal',
    'scipy.spatial',
]

# Try collect_all as well, just in case, but ignore errors/warnings effectively by having explicit imports
try:
    tmp_ret = collect_all('skimage')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
    tmp_ret = collect_all('scipy')
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
except Exception:
    pass

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
    name='SEM_Viewer',
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
