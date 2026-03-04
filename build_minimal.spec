# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 最小化打包配置
优化包体大小，只包含必要的模块
"""

import sys
import os
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files, collect_dynamic_libs

block_cipher = None

# 使用collect_all收集所有依赖库的内容
pygame_binaries, pygame_datas, pygame_hiddenimports = collect_all('pygame')
pil_binaries, pil_datas, pil_hiddenimports = collect_all('PIL')
numpy_binaries, numpy_datas, numpy_hiddenimports = collect_all('numpy')
pytmx_binaries, pytmx_datas, pytmx_hiddenimports = collect_all('pytmx')
pyglet_binaries, pyglet_datas, pyglet_hiddenimports = collect_all('pyglet')

# 合并所有二进制文件和数据文件
all_binaries = pygame_binaries + pil_binaries + numpy_binaries + pytmx_binaries + pyglet_binaries
all_datas = pygame_datas + pil_datas + numpy_datas + pytmx_datas + pyglet_datas

EXCLUDES = [
    # 仅排除大型第三方库和明显不需要的模块
    'tkinter', 'matplotlib', 'scipy', 'pandas', 'IPython',
    'jupyter', 'notebook', 'pytest', 'sphinx', 'docutils',
    'py.test',
    # 开发调试工具
    'pdb', 'profile', 'pstats',
    'curses', 'readline', 'rlcompleter',
    # 编译/构建工具
    'compileall', 'py_compile',
    'distutils', 'setuptools', 'pkg_resources',
    'venv', 'ensurepip', 'pip',
    # 网络相关（游戏不需要）
    'email', 'http', 'urllib', 'xmlrpc',
    'ssl', 'socket', 'select', 'selectors',
    # 数据库（使用JSON存档）
    'dbm', 'sqlite3',
    # 其他大型库
    'multiprocessing', 'concurrent', 'asyncio',
]

HIDDEN_IMPORTS = list(set(
    pygame_hiddenimports + pil_hiddenimports + numpy_hiddenimports + pytmx_hiddenimports + pyglet_hiddenimports +
    [
        'pygame',
        'PIL', 'PIL.Image', 'PIL.ImageDraw', 'PIL.ImageFont',
        'numpy',
        'pytmx',
        'pyglet',
        'dataclasses',
        'enum',
        'json',
        'typing',
        'pathlib',
        'abc',
        'inspect',
    ]
))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=HIDDEN_IMPORTS,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DiabloMini',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
