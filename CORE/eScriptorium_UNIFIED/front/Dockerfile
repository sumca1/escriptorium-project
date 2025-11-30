# Frontend Development Dockerfile with Hot Reload
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Expose port for webpack dev server
EXPOSE 8080

# Start webpack dev server with hot reload
CMD ["npm", "run", "dev"]
