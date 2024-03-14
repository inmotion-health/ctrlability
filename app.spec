# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[('/opt/homebrew/bin/ffmpeg/', 'lib')],
    datas=[('./ctrlability/processors/face_landmarker_v2_with_blendshapes.task', 'ctrlability/processors/'), ('./ctrlability_ui/config.yaml', 'ctrlability_ui'), ('./ctrlability_ui/data', 'ctrlability_ui/data')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['ffmpegPath.py'],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app',
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
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app',
)
app = BUNDLE(
    coll,
    name='app.app',
    icon=None,
    bundle_identifier=None,
)
