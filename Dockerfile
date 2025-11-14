# Multi-stage Docker build for FIL Deployer

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Setup Python backend
FROM python:3.11-slim AS backend

WORKDIR /app

# Install git (required for GitPython)
RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Create config directory
RUN mkdir -p /app/config

# Stage 3: Production image with Nginx
FROM nginx:alpine

# Install Python and git in Nginx image
RUN apk add --no-cache python3 py3-pip git

WORKDIR /app

# Copy Python dependencies (install them again in final image)
COPY backend/requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directories
RUN mkdir -p /app/config /tmp/fil-deployer-repos

# Expose ports
EXPOSE 80

# Start script
COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]

