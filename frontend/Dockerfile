FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install --legacy-peer-deps --force

COPY . .
ENV REACT_APP_BACKEND_URL=http://localhost:8001
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]
