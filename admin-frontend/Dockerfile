# Frontend Dockerfile - React Admin Panel
FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build app
RUN npm run build

# Expose port
EXPOSE 3000

# Start with preview (for production) or dev (for development)
CMD ["npm", "run", "preview"]