FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Note: Removed system dependencies as they're not needed for this project

# Copy requirements
COPY leadai/backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY leadai/backend/ /app/backend/
COPY leadai/frontend/ /app/frontend/

# Expose port
EXPOSE 8000

# Set PYTHONPATH
ENV PYTHONPATH=/app/backend:$PYTHONPATH

# Change to backend directory
WORKDIR /app/backend

# Run FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
