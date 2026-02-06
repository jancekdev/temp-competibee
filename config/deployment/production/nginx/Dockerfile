
# Multi-stage build to get React files from frontend build
FROM node:25-alpine AS frontend-build

WORKDIR /app/frontend

# Copy package files
COPY frontend/react/package*.json ./
RUN npm install

# Copy frontend source and build
COPY frontend/react/ ./
RUN npm run build

# Production nginx image
FROM docker.io/nginx:1.29.5-alpine

# Copy nginx configuration
COPY ./config/deployment/production/nginx/default.conf /etc/nginx/conf.d/default.conf


# Copy React build files to nginx html directory
COPY --from=frontend-build /app/frontend/dist /usr/share/nginx/html

# Create media directory for Django media files
RUN mkdir -p /usr/share/nginx/media

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html /usr/share/nginx/media

