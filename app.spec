# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.pyw'],
    pathex=[],
    binaries=[('/opt/homebrew/bin/ffmpeg', 'lib')],
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
    a.binaries,
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
app = BUNDLE(
    exe,
    name='app.app',
    icon=None,
    bundle_identifier=None,
)
