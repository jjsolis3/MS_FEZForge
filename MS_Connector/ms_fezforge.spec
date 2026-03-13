# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for MS FEZForge
Build command: pyinstaller ms_fezforge.spec
"""

import os

block_cipher = None

# All Python modules to include
py_modules = [
    'easy_runner.py',
    'measuresquare_extractor.py',
    'cloud_api_complete_workflow.py',
    'cloud_text_editor.py',
    'probuildiq_fez_editor.py',
    'probuildiq_reportlab_generator.py',
    'pdf_page_filter.py',
    'workflow_examples.py',
    'test_extractor.py',
]

a = Analysis(
    ['easy_runner.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Bundle config.json template alongside the exe
        ('config.json', '.'),
    ],
    hiddenimports=[
        'measuresquare_extractor',
        'cloud_api_complete_workflow',
        'cloud_text_editor',
        'probuildiq_fez_editor',
        'probuildiq_reportlab_generator',
        'pdf_page_filter',
        'workflow_examples',
        'tkinter',
        'tkinter.filedialog',
    ],
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
    name='MS_FEZForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console app (shows terminal window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
