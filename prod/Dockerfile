# Production Dockerfile - Backend + Frontend together
# Serves API on port 8001 and static files on port 3000

FROM python:3.11-slim

WORKDIR /app

# Install system deps and Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | sh - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy backend
COPY backend/ ./backend/
WORKDIR /app/backend
RUN pip install --no-cache-dir -r requirements.txt

# Copy frontend and build
COPY admin-frontend/ ./admin-frontend/
WORKDIR /app/admin-frontend
RUN npm install && npm run build

# Go back to app root
WORKDIR /app

# Expose ports
EXPOSE 8001 3000

# Start backend (frontend is built, can be served separately)
CMD ["sh", "-c", "cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 & npx serve dist -l 3000 & wait"]