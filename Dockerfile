# Multi-stage Dockerfile for ProcessCube Robot Agent
# Stage 1: Python dependencies builder
FROM python:3.12-slim as python-builder

WORKDIR /tmp

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


# Stage 2: Node.js builder for Studio Extension
FROM node:18-alpine as node-builder

WORKDIR /tmp

COPY package.json package-lock.json ./
RUN npm ci

COPY studio_extension ./studio_extension
WORKDIR /tmp/studio_extension
RUN npm ci && npm run build


# Stage 3: Runtime image
FROM python:3.12-slim

LABEL maintainer="5Minds IT-Solutions GmbH & Co. KG"
LABEL description="ProcessCube Robot Agent - RPA Integration for ProcessCube"
LABEL version="1.0.0"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 agent && \
    mkdir -p /app /var/log/processcube-robot-agent && \
    chown -R agent:agent /app /var/log/processcube-robot-agent

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=python-builder /root/.local /home/agent/.local

# Copy application code
COPY --chown=agent:agent . .

# Set environment variables
ENV PATH=/home/agent/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LOG_LEVEL=INFO

# Switch to non-root user
USER agent

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:42042/health || exit 1

# Expose ports
EXPOSE 42042

# Default command
CMD ["npm", "run", "processcube_robot_agent"]
