# 🍱 Sistema Dona Guedes - Marmitaria

Sistema completo de gerenciamento de pedidos para marmitaria.

## 📋 Requisitos

Instale na ordem:

1. **Python 3.11+** - https://www.python.org/downloads/
   - ⚠️ Marque "Add Python to PATH" durante instalação!

2. **Node.js 18+** - https://nodejs.org/
   - Escolha a versão LTS

3. **MongoDB Community** - https://www.mongodb.com/try/download/community
   - ⚠️ Marque "Install MongoDB as a Service"

4. **Reinicie o computador** após instalar tudo

## 🚀 Como Executar

**Duplo clique em:** `INICIAR_SISTEMA.bat`

Ou execute manualmente:

### Backend (Terminal 1):
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn server:app --host 0.0.0.0 --port 8001
```

### Frontend (Terminal 2):
```cmd
cd frontend
npm install
set REACT_APP_BACKEND_URL=http://localhost:8001
npm start
```

## 🔐 Acesso

- **URL:** http://localhost:3000
- **Admin:** código `admin`, senha `admin123`
- **Atendente:** usar código cadastrado (ex: `1`)

## 📁 Estrutura

```
├── backend/           # API FastAPI + MongoDB
├── frontend/          # React + Tailwind CSS
├── license-server/    # Servidor de licenças (opcional)
├── INICIAR_SISTEMA.bat    # Inicia tudo automaticamente
├── start_backend.bat      # Inicia só backend
├── start_frontend.bat     # Inicia só frontend
└── GUIA_INSTALACAO_COMPLETO.md  # Manual completo
```

## 📞 Suporte

**Japão Informática**
- Telefone: (19) 99813-2220
- Email: japaoinformatica@yahoo.com.br
