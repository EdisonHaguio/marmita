# Sistema Dona Guedes - Marmitaria

## Status: COMPLETO

## Versões Disponíveis

### 1. Versão Online (Preview)
- URL: https://marmitex-3.preview.emergentagent.com
- Usa MongoDB
- Requer internet

### 2. Versão Offline (Desktop)
- Pasta: `/app/desktop/`
- Usa SQLite (não precisa instalar banco)
- Funciona 100% offline
- Gera executável .exe único

## Funcionalidades

### Autenticação
- Login por código (atendentes)
- Login com senha (admin: admin/admin123)

### Produtos
- Marmitas P/M/G
- Acompanhamentos
- Bebidas, Cafés, Saladas
- Lanches, Pizzas, Sobremesas
- Outros produtos

### Regra de Marmitas
- P = 1 proteína
- M = 2 proteínas (2ª grátis)
- G = 2 proteínas (2ª grátis)

### Pagamento
- Dinheiro (com troco automático)
- PIX
- Cartão
- Fiado

### Impressão
- ESC/POS (Tanca T650)
- Windows (impressora padrão)
- Segunda via
- Cupom individual por funcionário

### Relatórios
- Vendas por dia
- Total de pedidos
- Faturamento
- Por atendente
- Por tamanho de marmita

## Como Criar o Instalador .exe

1. No Windows, abra a pasta `desktop`
2. Execute `CRIAR_INSTALADOR.bat`
3. Aguarde terminar
4. O arquivo `DonaGuedes.exe` estará em `dist\`

## Arquivos

```
/app/
├── backend/           # API Online (MongoDB)
├── frontend/          # Interface React
├── desktop/           # Versão Offline
│   ├── server_offline.py    # API SQLite
│   ├── static/              # Frontend compilado
│   ├── dona_guedes.db       # Banco de dados
│   └── CRIAR_INSTALADOR.bat # Gera o .exe
└── memory/
    └── PRD.md
```

## Suporte
Japão Informática - (19) 99813-2220
