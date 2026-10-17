# --- STAGE 1: Compilation ---
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm install

COPY . .
RUN npm run build

# --- STAGE 2: Nginx Web Server ---
FROM nginx:alpine

# Copia i file compilati di React dentro la cartella pubblica di Nginx
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
