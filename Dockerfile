FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --default-timeout=120 --no-cache-dir -r requirements.txt

# Copy application code
COPY app_mvp.py .
COPY services/ ./services/

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "app_mvp.py"]