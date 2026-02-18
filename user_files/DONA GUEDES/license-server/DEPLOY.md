# 🚀 DEPLOY DO SERVIDOR DE LICENÇAS

## Heroku (Gratuito)

### 1. Criar conta Heroku
https://signup.heroku.com

### 2. Instalar Heroku CLI
https://devcenter.heroku.com/articles/heroku-cli

### 3. Deploy

```bash
cd license-server

# Login
heroku login

# Criar app
heroku create japao-licencas

# Configurar variáveis
heroku config:set ADMIN_KEY=SUA_SENHA_SECRETA_AQUI
heroku config:set MONGODB_URI=sua_connection_string_mongodb_atlas

# Deploy
git init
git add .
git commit -m "License server"
heroku git:remote -a japao-licencas
git push heroku main
```

### 4. MongoDB Atlas (Gratuito)

1. Criar conta: https://www.mongodb.com/cloud/atlas/register
2. Criar cluster gratuito (M0 - 512MB)
3. Criar database: `japao_licencas`
4. Obter connection string
5. Adicionar no Heroku: `heroku config:set MONGODB_URI=...`

### URL Final

Seu servidor ficará em: `https://japao-licencas.herokuapp.com`

## Testar

```bash
# Verificar se está online
curl https://japao-licencas.herokuapp.com

# Listar licenças (admin)
curl "https://japao-licencas.herokuapp.com/api/licenses?admin_key=SUA_SENHA"

# Renovar licença
curl -X POST https://japao-licencas.herokuapp.com/api/renew \
  -H "Content-Type: application/json" \
  -d '{
    "license_key": "CHAVE_DO_CLIENTE",
    "days": 30,
    "admin_key": "SUA_SENHA"
  }'
```

## Atualizar LICENSE_SERVER no Sistema Cliente

Edite: `backend/.env`

```
LICENSE_SERVER_URL=https://japao-licencas.herokuapp.com
```
