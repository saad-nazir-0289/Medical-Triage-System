# Medical Triage System - Hugging Face Spaces / Docker
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt backend_reqs.txt
COPY frontend/requirements.txt frontend_reqs.txt
RUN pip install --no-cache-dir -r backend_reqs.txt -r frontend_reqs.txt

# Copy application
COPY . .

# Expose Streamlit port (HF uses 7860)
EXPOSE 7860

# Run launcher (starts backend + frontend)
CMD ["python", "app.py"]
