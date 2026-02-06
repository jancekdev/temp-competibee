FROM node:25-alpine

WORKDIR /app/frontend/react

# Run as non-root user to avoid permission issues with mounted volumes
USER node

EXPOSE 3000

# Install dependencies and start dev server
CMD ["sh", "-c", "npm install && npm run dev"] 
