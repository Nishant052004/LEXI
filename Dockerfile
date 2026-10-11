# Base official image
FROM python:3.11-slim

# Prevent python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install basic build tools, curl, and Node.js 20 (LTS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Install frontend dependencies (cached layer)
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci || npm install
WORKDIR /app

# Copy all project files
COPY . .

# Convert Windows CRLF line endings to Linux LF and make start script executable
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Build Next.js application for production
WORKDIR /app/frontend
RUN npm run build
WORKDIR /app

# Expose ports: 3000 (Next.js default), 8000 (FastAPI), 8501 (Streamlit), 10000 (Render default)
EXPOSE 3000 8000 8501 10000

# Run services on container startup
CMD ["./start.sh"]
