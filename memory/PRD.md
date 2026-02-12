# Sistema de Pedidos - Dona Guedes Marmitaria

## Visão Geral
Sistema completo de gerenciamento de pedidos para marmitaria, desenvolvido com FastAPI (backend), React (frontend) e MongoDB.

## Funcionalidades Implementadas

### Autenticação
- Login por código para atendentes
- Login com código e senha para administrador
- Credenciais: Admin (admin/admin123), Atendente (código numérico)

### Painel de Administração
- Gerenciamento de Usuários (criar/editar/excluir atendentes)
- Gerenciamento de Clientes (pessoa física e empresas)
- Gerenciamento de Produtos:
  - Marmitas (proteínas com preços P/M/G)
  - Acompanhamentos
  - Bebidas (preço único)
  - Saladas (preço único)
  - **☕ Cafés** (preço único) - NOVO
  - **🥪 Lanches** (preço único) - NOVO
  - **🍕 Pizzas** (preços P/M/G) - NOVO
  - **🍰 Sobremesas** (preço único) - NOVO
  - **📦 Outros** (preço único) - NOVO
- Configurações do sistema (logo, impressora, dados da empresa)

### Painel do Atendente
- Carrinho de múltiplas marmitas por pedido
- Seleção de tamanho (P/M/G)
- Seleção de acompanhamentos e proteínas
- Adição de bebidas, saladas, cafés, lanches, sobremesas e outros
- Cálculo automático do preço total
- Pedidos normais e para empresas (com nome do funcionário)
- Tipos de pedido: Balcão ou Entrega

### Tela da Cozinha
- Exibição de pedidos ativos para preparo
- Atualização de status dos pedidos

### Sistema de Impressão
- Suporte para impressora ESC/POS (Tanca T650)
- Suporte para impressora padrão do Windows
- Cupons individuais para pedidos de empresas

### Sistema de Licenciamento
- Servidor de licenças em Node.js separado
- Verificação de licença na inicialização e login
- Painel de gerenciamento de licenças (admin-panel.html)

## Arquitetura Técnica
- **Backend:** FastAPI + MongoDB + JWT Auth
- **Frontend:** React + Tailwind CSS + Shadcn/UI
- **Database:** MongoDB
- **Licenciamento:** Node.js/Express (serviço separado)

## Correções Aplicadas
- 11/02/2025: Corrigido erro de renderização React "insertBefore" usando IDs únicos como key em listas
- 12/02/2025: Removido `emergentintegrations` do requirements.txt (não necessário para este projeto)
- 12/02/2025: Adicionados novos tipos de produtos (Café, Lanche, Pizza, Sobremesa, Outro)

## Status: COMPLETO E FUNCIONAL

## Backlog/Melhorias Futuras
- P2: Tornar painel de licenças (admin-panel.html) funcional com API real
- P3: Relatórios de vendas e estatísticas
- P3: Histórico de pedidos com filtros avançados
