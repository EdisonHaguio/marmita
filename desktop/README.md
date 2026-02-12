# Dona Guedes - Criar Instalador Offline

## Requisitos para CRIAR o instalador:
- Windows 10
- Python 3.11+ (https://python.org)
- Node.js 18+ (https://nodejs.org)

## Como criar o instalador:

### Passo 1: Preparar
```cmd
cd desktop
pip install pyinstaller fastapi uvicorn pydantic
```

### Passo 2: Compilar Frontend
```cmd
cd ..\frontend
npm install --legacy-peer-deps
npm run build
```

### Passo 3: Copiar Frontend
```cmd
cd ..\desktop
xcopy /E /I /Y ..\frontend\build static
```

### Passo 4: Criar EXE
```cmd
pyinstaller --onefile --name=DonaGuedes --add-data "static;static" server_offline.py
```

### Passo 5: Pronto!
O arquivo `dist\DonaGuedes.exe` é o instalador.

## Para usar:
1. Copie `DonaGuedes.exe` para qualquer PC
2. Execute com duplo clique
3. Acesse http://localhost:8000
4. Login: admin / admin123

## Funciona 100% offline!
- Não precisa internet
- Não precisa instalar nada
- Banco de dados local (SQLite)
