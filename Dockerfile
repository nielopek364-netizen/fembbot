FROM python:3.10-slim

WORKDIR /app

# Zainstaluj zależności
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Skopiuj pliki bota
COPY bot.py .
COPY keep_alive.py .

# Bot Discord - uruchom na Pythonie
CMD ["python", "bot.py"]
