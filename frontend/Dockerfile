# syntax=docker/dockerfile:1

# ---------- Stage 1: build the static bundle ----------
FROM node:24-alpine AS builder

WORKDIR /app

# Lockfile first so `npm ci` is cached until dependencies change.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------- Stage 2: serve with nginx ----------
# The unprivileged variant runs as a non-root user and listens on 8080.
FROM nginxinc/nginx-unprivileged:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 8080
