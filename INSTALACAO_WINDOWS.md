# Sistema Dona Guedes - Instalação Windows

## 📦 Opção 1: Usar Docker Desktop (Recomendado)

### Pré-requisitos
1. Baixar e instalar [Docker Desktop para Windows](https://www.docker.com/products/docker-desktop/)
2. Reiniciar o computador após instalação

### Instalação
1. Extrair os arquivos do sistema em uma pasta (ex: `C:\DonaGuedes`)
2. Abrir PowerShell ou CMD na pasta do sistema
3. Executar: `docker-compose up -d`
4. Acessar: `http://localhost:3000`

## 🖥️ Opção 2: Instalação Nativa Windows

### Pré-requisitos
1. **Python 3.11+**: https://www.python.org/downloads/
2. **Node.js 18+**: https://nodejs.org/
3. **MongoDB Community**: https://www.mongodb.com/try/download/community

### Passo a Passo

#### 1. Instalar MongoDB
```bash
# Após instalar MongoDB, iniciar o serviço:
net start MongoDB
```

#### 2. Configurar Backend
```bash
cd C:\DonaGuedes\backend

# Criar ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar .env (editar com IP local)
# Trocar MONGO_URL para: mongodb://localhost:27017
```

#### 3. Configurar Frontend
```bash
cd C:\DonaGuedes\frontend

# Instalar dependências
npm install
# ou
yarn install
```

#### 4. Criar Scripts de Inicialização

**start_backend.bat:**
```batch
@echo off
cd /d C:\DonaGuedes\backend
call venv\Scripts\activate
python -m uvicorn server:app --host 0.0.0.0 --port 8001
pause
```

**start_frontend.bat:**
```batch
@echo off
cd /d C:\DonaGuedes\frontend
set REACT_APP_BACKEND_URL=http://localhost:8001
npm start
pause
```

**start_sistema.bat (Iniciar tudo):**
```batch
@echo off
echo Iniciando Sistema Dona Guedes...
start "Backend" cmd /k start_backend.bat
timeout /t 5
start "Frontend" cmd /k start_frontend.bat
echo.
echo Sistema iniciado!
echo Acesse: http://localhost:3000
echo.
pause
```

#### 5. Executar
Duplo clique em `start_sistema.bat`

## 🎯 Opção 3: Executável Standalone (Electron)

Para criar um executável único sem dependências:

### 1. Criar app Electron

**package.json** (na raiz):
```json
{
  "name": "dona-guedes",
  "version": "1.0.0",
  "main": "electron-main.js",
  "scripts": {
    "electron": "electron .",
    "build": "electron-builder"
  },
  "devDependencies": {
    "electron": "^28.0.0",
    "electron-builder": "^24.9.1"
  },
  "build": {
    "appId": "com.donaaguedes.app",
    "productName": "Dona Guedes - Sistema de Pedidos",
    "win": {
      "target": "nsis",
      "icon": "icon.ico"
    }
  }
}
```

**electron-main.js:**
```javascript
const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let backendProcess;
let mainWindow;

function startBackend() {
  const pythonPath = path.join(__dirname, 'backend', 'venv', 'Scripts', 'python.exe');
  const serverPath = path.join(__dirname, 'backend', 'server.py');
  
  backendProcess = spawn(pythonPath, ['-m', 'uvicorn', 'server:app', '--host', '127.0.0.1', '--port', '8001'], {
    cwd: path.join(__dirname, 'backend')
  });
  
  backendProcess.stdout.on('data', (data) => console.log(`Backend: ${data}`));
  backendProcess.stderr.on('data', (data) => console.error(`Backend Error: ${data}`));
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    },
    icon: path.join(__dirname, 'icon.ico')
  });

  // Aguardar backend iniciar
  setTimeout(() => {
    mainWindow.loadFile(path.join(__dirname, 'frontend', 'build', 'index.html'));
  }, 3000);

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  if (backendProcess) backendProcess.kill();
  app.quit();
});

app.on('activate', () => {
  if (mainWindow === null) createWindow();
});
```

### 2. Build do Frontend para produção
```bash
cd frontend
npm run build
```

### 3. Criar executável
```bash
npm install
npm run build
```

O executável estará em `dist/Dona Guedes Setup.exe`

## ⚙️ Configuração Impressora

1. Conectar impressora Tanca T650 na rede
2. Anotar o IP da impressora (ex: 192.168.1.100)
3. No sistema: Admin → Configurações → IP da Impressora
4. Salvar

## 🔐 Credenciais Padrão

- **Admin**: `admin` / `admin123`
- **Funcionários**: criar no Admin → Funcionários

## 📞 Suporte

**Japão Informática**  
Telefone: (19) 99813-2220

---

## 🚀 Uso Diário

1. Executar `start_sistema.bat` (ou abrir Docker Desktop)
2. Acessar `http://localhost:3000`
3. Login com código do funcionário
4. Começar a usar!

## 💡 Dicas

- Manter MongoDB sempre rodando (serviço Windows)
- Fazer backup regular do banco de dados
- Configurar impressora antes de usar
- Cadastrar produtos e funcionários no Admin

## 🐛 Problemas Comuns

**MongoDB não conecta:**
```bash
net start MongoDB
```

**Porta 8001 em uso:**
```bash
netstat -ano | findstr :8001
taskkill /PID [número] /F
```

**Frontend não carrega:**
- Verificar se backend está rodando (http://localhost:8001/api/)
- Limpar cache do navegador (Ctrl + Shift + Del)
