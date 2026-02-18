#!/usr/bin/env python3
"""
Script para criar o instalador .exe do sistema Dona Guedes
Este script:
1. Prepara todos os arquivos necessários
2. Usa PyInstaller para criar um executável único
3. Copia os arquivos estáticos (frontend compilado)
"""

import os
import sys
import shutil
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 60)
    print("  DONA GUEDES - Criador de Instalador")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("[OK] PyInstaller encontrado")
    except ImportError:
        print("[!] Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Check dependencies
    deps = ["fastapi", "uvicorn", "pydantic"]
    for dep in deps:
        try:
            __import__(dep)
            print(f"[OK] {dep} encontrado")
        except ImportError:
            print(f"[!] Instalando {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
    
    # Create output directory
    dist_dir = os.path.join(SCRIPT_DIR, "dist")
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Create spec file for PyInstaller
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{os.path.join(SCRIPT_DIR, "server_offline.py")}'],
    pathex=['{SCRIPT_DIR}'],
    binaries=[],
    datas=[
        ('{os.path.join(SCRIPT_DIR, "static")}', 'static'),
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'starlette',
        'pydantic',
    ],
    hookspath=[],
    hooksconfig={{}},
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
    name='DonaGuedes',
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
    icon=None,
)
'''
    
    spec_path = os.path.join(SCRIPT_DIR, "DonaGuedes.spec")
    with open(spec_path, "w") as f:
        f.write(spec_content)
    print(f"[OK] Arquivo spec criado: {spec_path}")
    
    # Run PyInstaller
    print("\n[...] Criando executável (pode demorar alguns minutos)...")
    result = subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--clean", spec_path],
        cwd=SCRIPT_DIR
    )
    
    if result.returncode == 0:
        exe_path = os.path.join(dist_dir, "DonaGuedes.exe")
        if os.path.exists(exe_path):
            print("\n" + "=" * 60)
            print("  SUCESSO!")
            print("=" * 60)
            print(f"\nExecutável criado em: {exe_path}")
            print("\nPara usar:")
            print("1. Copie o arquivo DonaGuedes.exe para qualquer pasta")
            print("2. Execute com duplo clique")
            print("3. Acesse http://localhost:8000 no navegador")
            print("\nLogin: admin / admin123")
        else:
            print("\n[ERRO] Executável não foi criado")
    else:
        print("\n[ERRO] Falha ao criar executável")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
