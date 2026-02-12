# Script para criar o executável do Dona Guedes
# Execute: python build_exe.py

import subprocess
import os
import shutil

print("=" * 50)
print("  CRIANDO INSTALADOR - Dona Guedes")
print("=" * 50)

# 1. Instalar dependências
print("\n[1/4] Instalando dependencias...")
subprocess.run(["pip", "install", "pyinstaller", "fastapi", "uvicorn", "pydantic"], check=True)

# 2. Compilar frontend
print("\n[2/4] Compilando frontend...")
os.chdir("../frontend")
subprocess.run(["npm", "run", "build"], check=True)

# 3. Copiar build para pasta static
print("\n[3/4] Preparando arquivos...")
os.chdir("../desktop")
if os.path.exists("static"):
    shutil.rmtree("static")
shutil.copytree("../frontend/build", "static")

# 4. Criar executável
print("\n[4/4] Criando executavel...")
subprocess.run([
    "pyinstaller",
    "--onefile",
    "--windowed",
    "--name=DonaGuedes",
    "--add-data=static;static",
    "--add-data=dona_guedes.db;.",
    "--icon=icon.ico",
    "server_offline.py"
], check=True)

print("\n" + "=" * 50)
print("  PRONTO!")
print("  Executavel criado em: dist/DonaGuedes.exe")
print("=" * 50)
