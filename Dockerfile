# Dockerfile for deployment (optional, for Hugging Face Spaces or similar)
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .
COPY .env .env

# Run bot
CMD ["python", "bot.py"]
