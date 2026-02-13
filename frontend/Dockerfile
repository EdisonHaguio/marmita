FROM node:18-alpine

WORKDIR /app/frontend

# Copiar package files
COPY package.json ./

# Limpar cache e instalar dependencias
RUN npm cache clean --force && \
    npm install --legacy-peer-deps --force

# Copiar codigo
COPY . .

# Expor porta
EXPOSE 3000

# Variavel de ambiente
ENV REACT_APP_BACKEND_URL=http://localhost:8001

# Comando de inicializacao
CMD ["npm", "start"]
