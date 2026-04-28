FROM python:3.11-slim

WORKDIR /app

# System dependencies for pdfplumber
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (Docker cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/

# Create data directories
RUN mkdir -p data/uploads data/vector_store data/eval

# Copy evaluation question set
COPY data/eval/questions.json ./data/eval/questions.json

# Run as non-root for security
RUN useradd --create-home --shell /bin/bash raguser \
    && chown -R raguser:raguser /app
USER raguser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
