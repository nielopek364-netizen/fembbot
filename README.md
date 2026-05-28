# ✨ FembGirl v2.0 - Discord Femboy Image Bot

🎀 **Kompletny bot Discord do wysyłania zdjęć femboyów z wykorzystaniem slash commands, wielu API i losowymi avatarami**

---

## 🌟 Nowe Features (v2.0)

✅ **Nazwa Brandu:** ✨ FembGirl ✨
✅ **Wiele API:** api.femboy.pics + api.waifu.pics (fallback system)
✅ **Losowy Avatar:** Bot zmienia swój avatar co godzinę z API
✅ **Nowe Komendy:** `/femboy-random`, `/femboy-stats`, `/femboy-help`
✅ **Lepszy Error Handling:** Automatyczne fallbacki między API
✅ **Status Bot:** Piękny status online z informacją

---

## 🎯 Funkcjonalności

### 📸 Komendy Główne

| Komenda | Opis | Parametry |
|---------|------|-----------|
| `/femboy-sfw` | Bezpieczne zdjęcia | `ilosc` (1-5), `tag` (opcjonalny) |
| `/femboy-nsfw` | Zdjęcia dla dorosłych (18+) | `ilosc` (1-5), `tag` (opcjonalny) |
| `/femboy-random` | Jedno losowe zdjęcie | `nsfw` (bool) |
| `/femboy-help` | Pomoc i instrukcje | - |
| `/femboy-stats` | Statystyki bota | - |

### 🎨 Cechy Specjalne

🎬 **Losowy Avatar** - Co godzinę bot zmienia avatar z API
💾 **Wiele API** - Automatyczne fallbacki na api.waifu.pics
🏷️ **Filtrowanie Tagów** - Szukaj konkretnych tematyk (cosplay, maid, itd.)
📊 **Statystyki** - Polecenie `/femboy-stats` pokazuje dane bota
🎲 **Losowe Zdjęcie** - Szybki losowy wybór `/femboy-random`
⚠️ **NSFW Check** - NSFW komenda działa tylko na kanałach z włączonym NSFW
🌈 **Piękne Embedy** - Każde zdjęcie w estetycznej ramce z tagami i informacjami

---

## 📋 Wymagania

- Python 3.8+
- Konto Discord
- Discord Server (serwer testowy)
- Token bota Discord

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

### 3. Konfiguracja Discord Bot

**Krok A: Discord Developer Portal**

1. Przejdź na https://discord.com/developers/applications
2. Kliknij **"New Application"** i nadaj nazwę (np. "FembGirl")
3. Przejdź do zak numer **"Bot"** i kliknij **"Add Bot"**
4. Skopiuj token bota (kliknij **"Copy"**)
5. W zak numer **"OAuth2" → "URL Generator"** zaznacz:
   - **Scopes:** `bot`, `applications.commands`
   - **Permissions:** `Send Messages`, `Embed Links`, `Read Message History`, `Change Nickname`
6. Skopiuj wygenerowany link i dodaj bota do serwera

**Krok B: Zmienne środowiskowe**

```bash
cp .env.example .env
```

Otwórz `.env` i wstaw swój token:

```
DISCORD_TOKEN=your_actual_token_here
```

### 4. Uruchomienie lokalnie

```bash
python bot.py
```

Powinna zobaczyć:
```
==================================================
✅ ✨ FembGirl ✨ v2.0 zalogowany pomyślnie!
✅ Bot: FembGirl#1234
✅ Ping: 45ms
==================================================

✅ Zsynchronizowano 5 komend slash
✅ Serwery: 1
==================================================
```

### 5. Testowanie komend

Na serwerze Discord wpisz:

```
/femboy-sfw
/femboy-sfw ilosc:3
/femboy-sfw tag:cosplay
/femboy-nsfw ilosc:2 tag:maid
/femboy-random
/femboy-random nsfw:true
/femboy-help
/femboy-stats
```

---

## 📡 API Integracje

Bot korzysta z **dwóch niezawodnych API**:

### 1. **api.femboy.pics** (Główne)
```
GET /v2/femboy?type=sfw
GET /v2/femboy?type=nsfw
```

**Response:**
```json
{
  "image": "https://...",
  "tags": ["cosplay", "maid"],
  "source": "..."
}
```

### 2. **api.waifu.pics** (Fallback)
```
GET /sfw/trap
GET /nsfw/trap
```

**Response:**
```json
{
  "url": "https://..."
}
```

---

## 🌐 Deployment 24/7 na Darmowym Hostingu

### Opcja 1: **Render.com** (Rekomendowany) ⭐

#### Setup:

1. **Utw ów konto**: https://render.com (zaloguj się przez GitHub)

2. **Utw ów nowy Web Service**:
   - Kliknij **"New +"** → **"Web Service"**
   - Połącz swoje repozytorium GitHub
   - Wybierz gałąź `main`

3. **Konfiguracja**:
   - **Name**: `fembgirl-bot`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Free

4. **Environment Variables**:
   - Przejdź do **Environment**
   - Dodaj: `DISCORD_TOKEN` = (twój token)

5. **Deploy**:
   - Kliknij **"Deploy"**
   - Bot uruchamia się automatycznie

**Problem:** Render zamyka serwisy darmowe po 15 minutach braku aktywności.

**Rozwiązanie:** Użyj UptimeRobot (patrz poniżej).

---

### Opcja 2: **Render + UptimeRobot** (Fully 24/7) ✅

1. **Zainstaluj UptimeRobot**: https://uptimerobot.com (bezpłatnie)

2. **Dodaj do bot.py keep-alive** (już wbudowane):
```python
from keep_alive import keep_alive
keep_alive()
```

3. **Utw ów monitor w UptimeRobot**:
   - URL: `https://your-render-url.onrender.com/`
   - Interval: co 5 minut
   - ✅ Bot nigdy się nie wyłączy

---

### Opcja 3: **Hugging Face Spaces**

1. Utw ów konto na https://huggingface.co
2. Utw ów nowe **Space** (Docker)
3. Upload plików bota
4. Hugging Face uruchamia Spaces 24/7 za darmo

---

### Opcja 4: **Railway.app**

1. Zarejestruj się na https://railway.app
2. Połącz repozytorium GitHub
3. Dodaj zmienne środowiskowe
4. Deploy - Railway daje $5/miesiąc free kredytów

---

## 🔧 Konfiguracja Avatar Loop

Bot automatycznie zmienia avatar co godzinę z API. Aby dostosować interwał:

```python
# W bot.py, klasa FemboyBot:
self.avatar_change_interval = 3600  # sekund (1 godzina)

# W dekoratorze @tasks.loop:
@tasks.loop(minutes=45)  # Zmień na żądaną wartość
async def change_avatar_task(self):
    ...
```

---

## 📊 Przykłady Odpowiedzi Bota

### SFW Embed:
```
┌─ ✨ Femboy 1/1
│  [OBRAZ]
│  🏷️ Tagi: cosplay, maid, cute
│  🔍 Szukane: cosplay
│  Źródło: api.femboy.pics | Powered by ✨ FembGirl ✨
└─
```

### NSFW Embed:
```
┌─ 🔞 Femboy NSFW 1/2
│  [OBRAZ]
│  🏷️ Tagi: trap, femboy
│  ⚠️ Uwaga: Treść tylko dla dorosłych
│  Źródło: api.femboy.pics | Powered by ✨ FembGirl ✨
└─
```

### Stats:
```
┌─ 📊 Statystyki ✨ FembGirl ✨
│  ℹ️ Informacje
│  Nazwa: ✨ FembGirl ✨
│  Wersja: 2.0
│  Ping: 45ms
│
│  📈 Statystyki
│  Serwery: 5
│  Użytkownicy: 1,250
│
│  🎨 Avatar
│  Ostatnia zmiana: 1 godzinę temu
│
│  🔗 API
│  • api.femboy.pics
│  • api.waifu.pics
└─
```

---

## 🛠️ Troubleshooting

### "DISCORD_TOKEN not set"
- Sprawdź czy `.env` istnieje
- Wstaw prawidłowy token
- Restart bota

### "Komenda slash nie pojawia się"
- Czekaj ~1 minutę na synchronizację
- Upewnij się, że bot ma permission `applications.commands`
- Restart bota

### "API returns 404"
- Api mogą czasem być niedostępne
- Bot automatycznie fallbackuje na alternatywne API
- Spróbuj za kilka sekund

### "Bot nie zmienia avatara"
- Sprawdź czy bot ma permission `Change Nickname`
- Upewnij się, że session aiohttp jest otwarta
- Sprawdź logi bota

### Bot wyłącza się na Render
- Używaj UptimeRobot keep-alive
- Lub przenieś się na Railway/Hugging Face

---

## 📚 Przydatne Komendy

```bash
# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie lokalnie
python bot.py

# Git push (auto-redeploy na Render)
git add .
git commit -m "Update bot"
git push origin main

# Sprawdzenie statusu
curl http://localhost:5000
```

---

## 📖 Struktura Plików

```
fembbot/
├── bot.py              # Główny plik bota
├── keep_alive.py       # Keep-alive server
├── requirements.txt    # Zależności Python
├── .env.example        # Template zmiennych
├── .gitignore         # Ignoruj prywatne pliki
├── Dockerfile         # Docker deployment
└── README.md          # Ta dokumentacja
```

---

## 🎯 Roadmap (Przyszłe Features)

- [ ] Baza danych do cache'owania zdjęć
- [ ] Komendy prefiksowe (`!femboy`)
- [ ] Custom reactions
- [ ] Server-specific settings
- [ ] Slash commands localization
- [ ] Bot dashboard web
- [ ] Streaming support (YouTube/Twitch)

---

## 📄 Licencja

MIT License - możesz używać i modyfikować kod swobodnie.

---

## ⚠️ Disclaimer

Ten bot jest narzędziem edukacyjnym. Upewnij się, że:

✅ Posiadasz prawo autorskie do korzystania z API
✅ Przestrzegasz TOS Discord
✅ Kanały NSFW są prawidłowo skonfigurowane
✅ Wszyscy użytkownicy serwera są pełnolettni
✅ Bot nie łamie żadnych regulaminów

---

## 🤝 Wsparcie

Masz pytanie lub problem?

- 📝 Otwórz Issue na GitHub
- 💬 Sprawdź Discussions
- 🐛 Zgłoś buga

---

**Powodzenia z botem! 🎀✨**

`Ostatnia aktualizacja: 2026-05-28`
`Wersja: 2.0`
`Twórca: nielopek364-netizen`
