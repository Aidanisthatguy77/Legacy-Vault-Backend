# Production Dockerfile - Backend + Frontend combined
# Deploys to any cloud container platform
# No local dependencies - everything cloud-hosted!

FROM python:3.11-slim

WORKDIR /app

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | sh - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Copy and setup backend
COPY backend/ ./backend/
WORKDIR /app/backend
RUN pip install --no-cache-dir emergentintegrations \
    --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/ && \
    pip install --no-cache-dir -r requirements.txt

# Copy and build frontend
COPY admin-frontend/ ./admin-frontend/
WORKDIR /app/admin-frontend
RUN npm install && npm run build

# Create static file output
RUN mkdir -p /app/static
COPY --from=0 /app/admin-frontend/dist /app/static

WORKDIR /app

# Expose ports
EXPOSE 8001 3000

# Start backend (serves API and static files)
CMD ["sh", "-c", "cd backend && uvicorn server:app --host 0.0.0.0 --port 8001"]
