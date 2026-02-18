# 🍱 DONA GUEDES - Sistema de Marmitaria (Versão Offline)

## 📋 Requisitos

- **Windows 10 ou superior**
- **Python 3.9+** (baixe em https://www.python.org/downloads/)
  - ⚠️ Durante a instalação, **MARQUE** a opção "Add Python to PATH"

---

## 🚀 Como Usar

### Opção 1: Executar Diretamente (Mais Simples)

1. Dê **duplo clique** no arquivo `INICIAR_SISTEMA.bat`
2. Aguarde a mensagem "SISTEMA INICIANDO..."
3. Abra o navegador e acesse: **http://localhost:8000**
4. Faça login com:
   - **Código:** `admin`
   - **Senha:** `admin123`

### Opção 2: Criar Executável (.exe)

Se você quer um arquivo único que pode copiar para qualquer PC:

1. Dê **duplo clique** no arquivo `CRIAR_INSTALADOR.bat`
2. Aguarde o processo (pode levar alguns minutos)
3. O arquivo `DonaGuedes.exe` será criado na pasta `dist/`
4. Copie esse arquivo para onde quiser e execute com duplo clique

---

## 📦 Estrutura dos Arquivos

```
desktop/
├── INICIAR_SISTEMA.bat     <- Execute este para iniciar
├── CRIAR_INSTALADOR.bat    <- Execute para criar o .exe
├── server_offline.py       <- Servidor backend
├── dona_guedes.db          <- Banco de dados SQLite
├── static/                 <- Frontend compilado
│   ├── index.html
│   └── static/
└── README.md               <- Este arquivo
```

---

## 🔐 Login Padrão

- **Administrador:**
  - Código: `admin`
  - Senha: `admin123`

- **Atendentes:**
  - Crie novos atendentes no painel do administrador

---

## ⚙️ Funcionalidades

- ✅ Cadastro de produtos (proteínas, acompanhamentos, bebidas, etc.)
- ✅ Cadastro de clientes (pessoa física e empresa)
- ✅ Pedidos com múltiplas marmitas
- ✅ Regra de 2 proteínas para marmitas M e G
- ✅ Pedidos de empresa com cupons por funcionário
- ✅ Cálculo de troco automático
- ✅ Visualização e reimpressão de cupons
- ✅ Tela da cozinha em tempo real
- ✅ Relatório de vendas diárias
- ✅ Impressão na impressora padrão do Windows

---

## 🛠️ Solução de Problemas

### "Python não encontrado"
- Baixe Python em: https://www.python.org/downloads/
- **IMPORTANTE:** Marque "Add Python to PATH" durante instalação
- Reinicie o computador após instalar

### "Porta 8000 já está em uso"
- Feche outras instâncias do programa
- Ou reinicie o computador

### Impressora não funciona
- O sistema usa a impressora padrão do Windows
- Configure sua impressora como padrão nas configurações do Windows

---

## 📞 Suporte

- **Japão Informática**
- **(19) 99813-2220**

---

## 📝 Backup dos Dados

Todos os dados são salvos no arquivo `dona_guedes.db`. 
Para fazer backup, simplesmente copie este arquivo para outro local.
