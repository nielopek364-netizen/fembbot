# FembBot - Discord Femboy Image Bot

🤖 **Kompletny bot Discord do wysyłania zdjęć femboyów z wykorzystaniem slash commands i api.femboy.pics**

---

## 🎯 Funkcjonalności

### Komendy

- **`/femboy-sfw`** - Wysyła bezpieczne dla pracy (SFW) zdjęcia femboyów
  - Parametr `ilosc` (1-5): liczba zdjęć do wysłania
  - Parametr `tag` (opcjonalny): filtrowanie po tematyce (np. cosplay, maid, catgirl)

- **`/femboy-nsfw`** - Wysyła zdjęcia dla dorosłych (NSFW) - **tylko na kanałach z włączonym NSFW**
  - Parametr `ilosc` (1-5): liczba zdjęć do wysłania
  - Parametr `tag` (opcjonalny): filtrowanie po tematyce
  - ✅ Automatyczne sprawdzenie, czy kanał ma NSFW włączony

### Cechy

✨ **Piękne embedy** - zdjęcia wysyłane w estetycznych ramkach Discord Embed
🏷️ **Tagi** - każde zdjęcie zawiera swoje tagi dla lepszego kontekstu
🛡️ **Obsługa błędów** - graceful error handling, gdy API nie zwróci zdjęcia
🔒 **Bezpieczeństwo NSFW** - NSFW komenda działa tylko na kanałach z włączonym NSFW
⚡ **Asynchroniczny kod** - szybkie pobieranie wielu zdjęć

---

## 📋 Wymagania

- Python 3.8+
- Konto Discord
- Discord Server (serwer testowy)

---

## 🚀 Instalacja i Uruchomienie

### 1. Klonowanie repozytorium

```bash
git clone https://github.com/nielopek364-netizen/fembbot.git
cd fembbot
```

### 2. Instalacja zależności

```bash
pip install -r requirements.txt
```

### 3. Konfiguracja bota Discord

**Krok A: Utworzenie aplikacji na Discord Developer Portal**

1. Przejdź na [Discord Developer Portal](https://discord.com/developers/applications)
2. Kliknij **"New Application"** i nadaj nazwę (np. "FembBot")
3. Przejdź do zakładki **"Bot"** i kliknij **"Add Bot"**
4. Skopiuj token bota (kliknij **"Copy"** pod tokenem)
5. W zakładce **"OAuth2" → "URL Generator"** zaznacz:
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Send Messages`, `Embed Links`, `Read Message History`
6. Skopiuj wygenerowany link i otwórz go w przeglądarce, aby dodać bota do serwera

**Krok B: Konfiguracja zmiennych środowiskowych**

```bash
cp .env.example .env
```

Otwórz `.env` i wstaw swój token:

```
DISCORD_TOKEN=your_actual_token_here
```

### 4. Uruchomienie bota lokalnie

```bash
python bot.py
```

Powinnaś zobaczyć:
```
✅ Bot zalogowany jako FembBot#1234
✅ Synchronizacja X komend slash
```

### 5. Testowanie komend

Na swoim serwerze Discord wpisz:

```
/femboy-sfw
/femboy-sfw ilosc:3
/femboy-sfw tag:cosplay
/femboy-nsfw ilosc:2 tag:maid
```

---

## 🌍 Deployment 24/7 na Darmowym Hostingu

### Opcja 1: **Render.com** (Rekomendowany)

#### Setup:

1. **Utwórz konto**: https://render.com (zaloguj się przez GitHub)

2. **Utwórz nowy Web Service**:
   - Kliknij **"New +"** → **"Web Service"**
   - Połącz swoje repozytorium GitHub
   - Wybierz gałąź `main`

3. **Konfiguracja**:
   - **Name**: `fembbot`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Free

4. **Zmienne środowiskowe**:
   - Przejdź do **Environment**
   - Dodaj zmienną: `DISCORD_TOKEN` = (twój token bota)

5. **Deploy**:
   - Kliknij **"Deploy"**
   - Bot będzie uruchamiany automatycznie

**Problem**: Render zamyka serwisy darmowe po 15 minutach braku aktywności. **Rozwiązanie**: Skorzystaj z UptimeRobot (patrz poniżej).

---

### Opcja 2: **Render + UptimeRobot** (Fully 24/7)

#### Setup Keep-Alive:

1. **Zainstaluj UptimeRobot serwer** (bezpłatnie): https://uptimerobot.com

2. **Dodaj zmienną do `bot.py`** (już zawarta, ale sprawdź):
   ```python
   from flask import Flask
   app = Flask(__name__)

   @app.route('/')
   def ping():
       return 'Bot is alive!', 200

   # W osobnym threadzoe:
   from threading import Thread
   def run_server():
       app.run(host='0.0.0.0', port=5000)
   Thread(target=run_server, daemon=True).start()
   ```

3. **Utwórz monitor w UptimeRobot**:
   - URL: `https://your-render-url.onrender.com/`
   - Interval: co 5 minut
   - Bot nigdy się nie wyłączy ✅

---

### Opcja 3: **Hugging Face Spaces** (Alternatywa)

1. Utwórz konto na https://huggingface.co
2. Stwórz nowe **Space** (Docker)
3. Upload plików bota
4. Dodaj `Dockerfile`:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "bot.py"]
```

5. Hugging Face uruchamia Spaces 24/7 za darmo (z ograniczeniami)

---

### Opcja 4: **Railway.app** (Alternatywa)

1. Zarejestruj się na https://railway.app
2. Połącz repozytorium GitHub
3. Dodaj zmienne środowiskowe
4. Deploy - Railway udostępnia $5/miesiąc free kredytów (wystarczy)

---

## 📝 Użyteczne Komendy

### Lokalne testowanie:

```bash
# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie bota
python bot.py

# Sprawdzenie statusu
curl http://localhost:5000
```

### Git push do Render:

```bash
git add .
git commit -m "Update bot"
git push origin main
# Render automatycznie redeploy
```

---

## 🔧 Troubleshooting

### "DISCORD_TOKEN not set"
- Upewnij się, że plik `.env` istnieje i zawiera `DISCORD_TOKEN`
- Restart bota

### "Komenda slash nie pojawia się"
- Czekaj ~1 minutę na synchronizację
- Restart bota
- Upewnij się, że bot ma permission `applications.commands`

### "API returns 404 for images"
- api.femboy.pics czasami może mieć downtime
- Bot automatycznie zwraca error message

### Bot wyłącza się na Render
- Użyj UptimeRobot keep-alive
- Lub przenieś się na Railway/Hugging Face

---

## 📚 API Dokumentacja

**API**: https://api.femboy.pics/

**Endpoint SFW**:
```
GET /v2/femboy?type=sfw
```

**Endpoint NSFW**:
```
GET /v2/femboy?type=nsfw
```

**Response**:
```json
{
  "image": "https://...",
  "tags": ["cosplay", "maid"],
  "source": "..."
}
```

---

## 📄 Licencja

MIT License - możesz używać i modyfikować kod swobodnie.

---

## ⚠️ Disclaimer

Ten bot jest narzędziem edukacyjnym. Upewnij się, że:
- ✅ Posiadasz prawo autorskie do korzystania z API
- ✅ Przestrzegasz TOS Discord
- ✅ NSFW kanały są prawidłowo skonfigurowane
- ✅ Wszyscy użytkownicy serwera są pełnoletni

---

**Powodzenia z botem! 🚀**
