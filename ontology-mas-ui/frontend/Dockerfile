# Frontend Dockerfile - Multi-stage build for smaller, safer runtime

# 1) Builder stage
FROM node:20-bookworm-slim AS builder
WORKDIR /app
RUN corepack enable
COPY package*.json ./
RUN npm ci && npm cache clean --force
COPY . .
RUN npm run build

# 2) Runtime stage (static files served by nginx)
FROM nginx:stable-alpine
WORKDIR /usr/share/nginx/html

# Copy built assets
COPY --from=builder /app/dist/ ./

# Copy SPA-friendly nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose HTTP port
EXPOSE 80

# Nginx runs as non-root (nginx) by default on this image
RUN apk update && apk upgrade --no-cache
CMD ["nginx", "-g", "daemon off;"]
