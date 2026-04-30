# -*- mode: python ; coding: utf-8 -*-
# main.spec - Configuração do PyInstaller para gerar o .exe
# Este arquivo substitui os argumentos de linha de comando

import os

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[BASE_DIR],
    binaries=[],
    # Inclui arquivos de dados (banco de dados, templates, etc.)
    datas=[
        (os.path.join(BASE_DIR, 'db.sqlite3'), '.'),
    ],
    hiddenimports=[
        # Django eapps
        'django',
        'django.conf',
        'django.core',
        'django.db',
        'django.middleware',
        'django.urls',
        'django.views',
        'django.template',
        'django.template.loaders',
        'djangorestframework',
        'djangorestframework.parsers',
        'djangorestframework.renderers',
        # Waitress
        'waitress',
        'waitress.channel',
        'waitress.server',
        # Outros
        'pandas',
        'pandas.core',
        'ortools',
        'ortools.linear_solver',
        'psycopg2',
        'corsheaders',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclui módulos desnecessários para reduzir tamanho
        'tkinter',
        'matplotlib',
        'numpy',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ServidorAgenda',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
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
    name='dist',
)
