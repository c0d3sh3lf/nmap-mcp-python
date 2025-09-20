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
ENV SECRET_KEY="SAg1bVGhzkvB2FvxjEoRfcKE323Xw1gR"
ENV AUTH_USERNAME="admin"
ENV AUTH_PASSWORD="admin123"
ENV ACCESS_TOKEN_EXPIRE_MINUTES=15
ENV REFRESH_TOKEN_EXPIRE_HOURS=24

EXPOSE 8080

# Start uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
