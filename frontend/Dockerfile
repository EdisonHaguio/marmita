FROM node:18-alpine

WORKDIR /app/frontend

# Copiar package files
COPY package.json ./

# Instalar dependencias
RUN npm install --legacy-peer-deps

# Copiar codigo
COPY . .

# Expor porta
EXPOSE 3000

# Comando de inicializacao
CMD ["npm", "start"]
