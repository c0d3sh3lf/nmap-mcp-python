FROM python:3.11-slim

# Install nmap and required system packages
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      nmap \
      gcc \
      libxml2 \
      libxml2-dev \
      && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy python requirements & install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy app
COPY app /app/app

ENV PYTHONUNBUFFERED=1
ENV API_KEY="changeme"

EXPOSE 8080

# Start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
