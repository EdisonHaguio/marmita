FROM node:18-alpine

WORKDIR /app/frontend

# Copiar package files
COPY package.json yarn.lock ./

# Instalar dependências
RUN yarn install --frozen-lockfile

# Copiar código
COPY . .

# Expor porta
EXPOSE 3000

# Comando de inicialização
CMD ["yarn", "start"]
