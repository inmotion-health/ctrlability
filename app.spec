# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[('C:\\Users\\alexa\\AppData\\Local\\Microsoft\\WinGet\\Packages\\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\\ffmpeg-6.1.1-full_build\\bin\\ffmpeg.exe', 'lib')],
    datas=[('./ctrlability/processors/face_landmarker_v2_with_blendshapes.task', 'ctrlability/processors/'), ('./ctrlability_ui/config.yaml', 'ctrlability_ui'), ('./ctrlability_ui/data', 'ctrlability_ui/data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['ffmpegPath.py'],
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
    name='app',
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
)
