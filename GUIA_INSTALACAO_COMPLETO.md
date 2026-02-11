# 📦 GUIA COMPLETO DE INSTALAÇÃO - Sistema Dona Guedes
## Japão Informática - (19) 99813-2220

---

## 🎯 SISTEMA COMPLETO INCLUI:

✅ **Instalação Local** (funciona sem internet)  
✅ **Controle Online de Licenças** (bloqueia inadimplentes)  
✅ **Logo Personalizável** (troque facilmente)  
✅ **Múltiplos Clientes** (use em vários restaurantes)  
✅ **Impressora Windows** (qualquer impressora)  
✅ **Pedidos para Empresas** (cupons individuais)

---

## 📥 PARTE 1: DOWNLOAD E INSTALAÇÃO

### Passo 1: Baixar o Sistema

1. Clique em **"Save to GitHub"** (se ainda não fez)
2. Acesse seu repositório GitHub
3. Clique em **"Code" → "Download ZIP"**
4. Extraia o ZIP em uma pasta (ex: `C:\DonaGuedes`)

### Passo 2: Instalar Pré-requisitos

**Instale na seguinte ordem:**

1. **Python 3.11+**
   - Download: https://www.python.org/downloads/
   - ✅ Marque "Add Python to PATH" durante instalação
   - Reinicie o computador após instalar

2. **Node.js 18+**
   - Download: https://nodejs.org/
   - Escolha versão LTS (recomendada)
   - Reinicie o computador após instalar

3. **MongoDB Community Edition**
   - Download: https://www.mongodb.com/try/download/community
   - Durante instalação:
     - ✅ Marque "Install MongoDB as a Service"
     - ✅ Marque "Install MongoDB Compass" (opcional)

### Passo 3: Executar o Sistema

**Duplo clique em:** `INICIAR_SISTEMA.bat`

O sistema vai:
- Instalar dependências automaticamente
- Iniciar backend (porta 8001)
- Iniciar frontend (porta 3000)
- Abrir navegador automaticamente

**Primeiro acesso:**
- Login: `admin`
- Senha: `admin123`

---

## 🔐 PARTE 2: ATIVAR LICENÇA DO CLIENTE

### Passo 1: Tela de Ativação

Ao abrir o sistema pela primeira vez, aparecerá:

```
⚠️ SISTEMA NÃO ATIVADO
Para ativar, preencha os dados abaixo:
```

### Passo 2: Preencher Dados

- **Nome do Cliente/Empresa:** Nome da marmitaria
- **CNPJ/CPF:** Documento do cliente
- **Telefone:** Contato do cliente
- **Email:** Email para notificações

### Passo 3: Enviar para Ativação

- Sistema envia dados para servidor Japão Informática
- Você recebe notificação
- Cliente fica com licença TRIAL (7 dias)
- Você ativa permanente após confirmar pagamento

---

## 💰 PARTE 3: CONTROLE DE MENSALIDADE

### Como Funciona?

**Sistema verifica licença:**
- ✅ **Online:** A cada 24h conecta ao servidor
- ✅ **Offline:** Usa cache local (até 7 dias)
- ❌ **Expirado:** Bloqueia acesso ao sistema

### Painel de Controle (Você - Japão Informática)

Acesse: `https://japao-licencas.herokuapp.com/admin`

**Funções:**
- 📋 Ver todos os clientes
- ✅ Ativar/renovar licenças
- ❌ Bloquear inadimplentes
- 📊 Relatório de vencimentos
- 📧 Enviar notificações automáticas

### Avisos Automáticos

**Cliente vê avisos:**
- 🟢 Mais de 5 dias: "Licença ativa"
- 🟡 5 dias ou menos: "⚠️ Licença vence em X dias"
- 🔴 Vencido: "❌ Sistema bloqueado. Contate (19) 99813-2220"

### Renovação Manual

Se servidor estiver offline, você pode renovar manualmente:

```bash
cd C:\DonaGuedes\backend
python
>>> from license_manager import license_manager
>>> license_manager.license_data['expires_at'] = '2026-03-10T00:00:00+00:00'
>>> license_manager._save_license()
```

---

## 🎨 PARTE 4: TROCAR LOGO DO CLIENTE

### Método 1: Pelo Sistema (Mais Fácil)

1. Login como **admin**
2. **Admin → Configurações**
3. Campo **"URL da Logo"**
4. Cole a URL da imagem online
   - Ex: `https://imgur.com/suaimagem.png`
5. **Salvar**

### Método 2: Imagem Local (Avançado)

1. Coloque a imagem em: `C:\DonaGuedes\frontend\public\logos\cliente.png`

2. Edite: `C:\DonaGuedes\frontend\src\pages\Login.js`

Linha 33, altere:
```javascript
// DE:
store_logo_url

// PARA:
"/logos/cliente.png"
```

3. Reinicie o sistema

### Método 3: Criar Pacote Personalizado

Antes de entregar ao cliente:

1. Baixe logo do cliente
2. Coloque em `frontend/public/logos/`
3. Edite `Login.js` com caminho da logo
4. **Compacte tudo em novo ZIP**
5. Entregue ZIP personalizado

---

## 📱 PARTE 5: FUNCIONAR ONLINE (Acesso Remoto)

### Opção A: Ngrok (Temporário - Grátis)

1. Download: https://ngrok.com/download
2. Extrair na pasta do sistema
3. Executar:
```bash
ngrok http 3000
```
4. Copiar URL: `https://abc123.ngrok.io`
5. Compartilhar com cliente

**Limitações:**
- URL muda a cada reinício
- Grátis para teste

### Opção B: Deploy na Nuvem (Permanente)

**Heroku (Recomendado):**

1. Criar conta: https://heroku.com
2. Instalar Heroku CLI
3. Na pasta do sistema:
```bash
heroku login
heroku create dona-guedes-cliente1
git push heroku main
```

4. URL permanente: `https://dona-guedes-cliente1.herokuapp.com`

**Railway.app (Alternativa):**
- Mais fácil
- Conecta direto com GitHub
- URL: `https://dona-guedes.railway.app`

### Opção C: Servidor Próprio

Contratar VPS:
- **DigitalOcean:** $5/mês
- **Vultr:** $2.50/mês
- **AWS EC2:** Free tier 12 meses

Instalar Docker:
```bash
docker-compose up -d
```

---

## 🖨️ PARTE 6: CONFIGURAR IMPRESSORA

### Impressora Normal (Windows)

1. **Admin → Configurações**
2. **Tipo de Impressora:** "Impressora Padrão do Windows"
3. No Windows, defina sua impressora como padrão
4. Pronto! Sistema usa ela automaticamente

### Impressora Térmica (Tanca T650)

1. Conectar impressora na rede
2. Anotar IP (ex: `192.168.1.100`)
3. **Admin → Configurações**
4. **Tipo:** "Impressora Térmica ESC/POS"
5. **IP:** `192.168.1.100`
6. **Porta:** `9100`
7. Testar criando um pedido

---

## 🔧 PARTE 7: CONFIGURAÇÃO INICIAL

### Passo 1: Criar Funcionários

1. **Admin → Funcionários → Novo**
2. Código: `001`
3. Nome: `Maria Silva`
4. Repetir para cada atendente

### Passo 2: Cadastrar Produtos

**Acompanhamentos:**
- Arroz, Feijão, Salada, Farofa, etc
- Preço: 0 (já incluídos)

**Misturas (Proteínas):**
- Frango: P: 12.00, M: 15.00, G: 18.00
- Carne: P: 13.00, M: 16.00, G: 19.00
- Peixe: P: 15.00, M: 18.00, G: 21.00

**Saladas:**
- Salada Verde: R$ 3.00
- Salada Caesar: R$ 5.00

**Bebidas:**
- Coca-Cola 350ml: R$ 5.00
- Suco Natural: R$ 4.00

### Passo 3: Cadastrar Clientes (Opcional)

Para facilitar pedidos repetidos:
- **Admin → Clientes**
- Nome, Telefone, Endereço

---

## 📞 PARTE 8: SUPORTE E TROUBLESHOOTING

### Problemas Comuns

**Sistema não inicia:**
```bash
# Verificar se MongoDB está rodando:
net start MongoDB

# Verificar portas:
netstat -ano | findstr :3000
netstat -ano | findstr :8001
```

**Licença não ativa:**
- Verificar conexão internet
- Verificar se dados foram preenchidos corretamente
- Contatar: (19) 99813-2220

**Impressora não imprime:**
- Verificar se está ligada e no Windows
- Testar imprimindo arquivo .txt do Windows
- Verificar IP (se térmica)

### Logs do Sistema

**Backend:**
```
C:\DonaGuedes\backend\logs\
```

**Frontend:**
```
Pressione F12 no navegador → Console
```

---

## 💼 PARTE 9: MODELO DE NEGÓCIO

### Sugestão de Preços

**Instalação:** R$ 300 - R$ 500
**Mensalidade:** R$ 50 - R$ 100/mês
**Suporte:** R$ 80/hora

### Contratos

Use contrato incluindo:
- Instalação e treinamento
- Mensalidade pelo uso do sistema
- Suporte remoto incluso
- Visita técnica: R$ 100

---

## 📋 CHECKLIST DE ENTREGA AO CLIENTE

- [ ] Sistema instalado e funcionando
- [ ] Licença ativada (trial ou permanente)
- [ ] Logo personalizada configurada
- [ ] Impressora testada
- [ ] 3-5 funcionários cadastrados
- [ ] 10-15 produtos cadastrados
- [ ] Treinamento de 1h com atendente
- [ ] Documento com login admin
- [ ] Telefone de suporte: (19) 99813-2220

---

## 🚀 PARTE 10: RECURSOS AVANÇADOS

### Backup Automático

Criar script `backup.bat`:
```batch
@echo off
set DATA=%date:~-4,4%%date:~-7,2%%date:~-10,2%
mongodump --out C:\Backups\%DATA%
```

Agendar no Windows (Tarefas Agendadas):
- Executar `backup.bat` todo dia às 23h

### Múltiplas Lojas

Instalar em cada loja:
- Banco local (MongoDB)
- Sistema independente
- Licença individual

### Estatísticas

**Admin → Relatórios** (futuro):
- Vendas por dia/mês
- Produto mais vendido
- Atendente com mais pedidos

---

## 📞 CONTATO JAPÃO INFORMÁTICA

**Telefone/WhatsApp:** (19) 99813-2220  
**Email:** japaoinformatica@yahoo.com.br  
**Suporte:** Segunda a Sábado, 8h às 18h

---

## 📄 APÊNDICE: COMANDOS ÚTEIS

### Iniciar Manualmente

```bash
# Backend
cd C:\DonaGuedes\backend
python -m uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend  
cd C:\DonaGuedes\frontend
yarn start
```

### Ver Logs

```bash
# Backend
tail -f C:\DonaGuedes\logs\backend.log

# MongoDB
tail -f "C:\Program Files\MongoDB\Server\7.0\log\mongod.log"
```

### Resetar Admin

```bash
cd C:\DonaGuedes\backend
python
>>> from server import db
>>> db.users.delete_one({"role": "admin"})
# Reiniciar sistema - admin será recriado
```

---

**✅ Sistema completo e documentado!**  
**💰 Pronto para cobrar mensalidade!**  
**🎨 Logo personalizável!**  
**☁️ Funciona online e offline!**

---

*Desenvolvido por Japão Informática*  
*Todos os direitos reservados © 2026*
