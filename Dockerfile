# Dockerfile for Render deployment
FROM python:3.10-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .
COPY keep_alive.py .

# Token będzie z Environment Variable na Render
# NIE kopius .env - Discord token ustawiasz w panelu Render!

# Run bot na Pythonie
CMD ["python", "bot.py"]
