"""
================================================================================
                      ✨ BOT.PY - PRO-SERIES EDITION ✨
                      System: Discord Application Bot
                      Target: Femboy & Furry High-Speed Content Delivery
                      Language: Python 3.10+ (discord.py v2.3+)
================================================================================
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import random
import asyncio
import os
import sys
import time
from typing import Optional, List, Dict, Set, Any, Tuple
from dotenv import load_dotenv
from datetime import datetime
from keep_alive import keep_alive

# Wczytanie zmiennych środowiskowych z pliku .env
load_dotenv()

# --- KONFIGURACJA PODSTAWOWA ---
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    print("❌ BŁĄD KRYTYCZNY: Brak zmiennej DISCORD_TOKEN w środowisku / pliku .env!")
    sys.exit(1)

# Definicje uprawnień bota (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Wymaga włączenia Server Members Intent w Discord Developer Portal

# Globalne stałe identyfikacji wizualnej i brandingu bota
BOT_NAME = "✨ FembGirl ✨"
BOT_VERSION = "3.1.2-Fix"
COLOR_SFW = 0xFFB6C1        # Klasyczny pastelowy uroczy róż (Light Pink)
COLOR_NSFW = 0x9B59B6       # Głęboki, ekskluzywny fiolet / purpura
COLOR_INFO = 0x3498DB       # Estetyczny błękit informacyjny
COLOR_SUCCESS = 0x2ECC71    # Żywa zieleń sukcesu
COLOR_WARNING = 0xE67E22    # Ciepły pomarańcz ostrzeżeń
COLOR_DANGER = 0xE74C3C     # Czerwień błędu/usuwania

# Inicjalizacja głównej instancji bota
bot = commands.Bot(command_prefix=['!', '.'], intents=intents, help_command=None)

# ==============================================================================
#                 GIGANTYCZNY SŁOWNIK MAPOWANIA TAGÓW (130+ FRAZ)
# ==============================================================================
# Słownik automatycznie tłumaczy, czyści i normalizuje polskie zapytania użytkownika,
# mapując je na profesjonalne, ujednolicone tagi systemów Booru (Danbooru/Safebooru).
# ==============================================================================
POLISH_TAGS_MAP: Dict[str, str] = {
    # --- KATEGORIA: STROJE I ELEMENTY ODZIEŻY ---
    "pokojowka": "maid_uniform",
    "pokojówka": "maid_uniform",
    "zakolanowki": "thighhighs",
    "zakolanówki": "thighhighs",
    "ponczochy": "stockings",
    "pończochy": "stockings",
    "bielizna": "lingerie",
    "sukienka": "dress",
    "spodniczka": "skirt",
    "spódniczka": "skirt",
    "mundurek": "school_uniform",
    "strojekapielowy": "swimsuit",
    "strójkąpielowy": "swimsuit",
    "bikini": "bikini",
    "sweter": "sweater",
    "kostium": "cosplay",
    "szpilki": "high_heels",
    "gorset": "corset",
    "obroza": "collar",
    "obroża": "collar",
    "rajstopy": "pantyhose",
    "podwiazki": "garter_belt",
    "podwiązki": "garter_belt",
    "bluza": "hoodie",
    "kabaretki": "fishnets",
    "koszula": "shirt",
    "krawat": "tie",
    "kokarda": "ribbon",
    "fartuszek": "apron",
    "buty": "shoes",
    "rekawiczki": "gloves",
    "rękawiczki": "gloves",
    "krótkieszorty": "short_shorts",
    "szorty": "shorts",
    "top": "crop_top",
    "zakiet": "jacket",
    "żakiet": "jacket",
    "recznik": "towel",
    "ręcznik": "towel",

    # --- KATEGORIA: BUDOWA CIAŁA I ANATOMIA ---
    "nogi": "legs",
    "uda": "thighs",
    "tylek": "butt",
    "tyłek": "butt",
    "stopy": "feet",
    "brzuch": "abs",
    "plaski-brzuch": "flat_chest",
    "płaski-brzuch": "flat_chest",
    "twarz": "face",
    "skora": "pale_skin",
    "skóra": "pale_skin",
    "plecy": "backs",
    "biodra": "hips",
    "wlosy": "hair",
    "włosy": "hair",
    "oczy": "eyes",
    "kly": "fangs",
    "kły": "fangs",

    # --- KATEGORIA: CECHY ZWIERZĘCE / ANIMAL EARS ---
    "uszy": "animal_ears",
    "kot": "catboy",
    "kotek": "catboy",
    "lis": "fox_boy",
    "wilk": "wolf_boy",
    "rogi": "horns",
    "ogon": "tail",
    "neko": "neko",
    "uszkakota": "cat_ears",
    "uszkalisa": "fox_ears",
    "królik": "bunny_boy",
    "krolik": "bunny_boy",
    "skrzydla": "wings",
    "skrzydła": "wings",

    # --- KATEGORIA: PALETA KOLORÓW I FRYZURY ---
    "dlugiewlosy": "long_hair",
    "długiewłosy": "long_hair",
    "krotkiewlosy": "short_hair",
    "krótkiewłosy": "short_hair",
    "rozowewlosy": "pink_hair",
    "różowewłosy": "pink_hair",
    "blond": "blonde_hair",
    "czarnewlosy": "black_hair",
    "czarnewłosy": "black_hair",
    "bialewlosy": "white_hair",
    "białewłosy": "white_hair",
    "niebieskiewlosy": "blue_hair",
    "niebieskiewłosy": "blue_hair",
    "rudewlosy": "red_hair",
    "rudewłosy": "red_hair",
    "ciemnaskora": "dark_skin",
    "ciemnaskóra": "dark_skin",
    "srebrnewlosy": "silver_hair",
    "srebrnewłosy": "silver_hair",

    # --- KATEGORIA: EMOCJE, GESTY I MIMIKA ---
    "rumieniec": "blush",
    "uroczy": "cute",
    "usmiech": "smile",
    "uśmiech": "smile",
    "smutny": "sad",
    "spojrzenie": "looking_at_viewer",
    "zamknieteoczy": "closed_eyes",
    "zamknięteoczy": "closed_eyes",
    "jezyk": "tongue_out",
    "język": "tongue_out",
    "mruganie": "wink",
    "placze": "crying",
    "płacze": "crying",
    "wstydliwy": "shy",
    "usmiech-gula": "smug",
    "uśmiech-gula": "smug",

    # --- KATEGORIA: POSTACIE I TEMATY SPECJALNE ---
    "astolfo": "astolfo_(fate)",
    "venti": "venti_(genshin_impact)",
    "hideri": "hideri_kanzaki",
    "felix": "felix_argyle",
    "link": "link_(zelda)",
    "trap": "crossdressing",
    "chlopczyca": "tomboy",
    "chłopczyca": "tomboy",
    "gej": "yaoi",
    "chlopak": "boy",
    "chłopak": "boy",
    "bishi": "bishounen",
    "androgyniczny": "androgynous",

    # --- KATEGORIA: OTOCZENIE I SCENERIA ---
    "loze": "bed",
    "łóżko": "bed",
    "lozko": "bed",
    "pokoj": "bedroom",
    "pokój": "bedroom",
    "plaza": "beach",
    "plaża": "beach",
    "szkola": "school",
    "szkoła": "school",
    "natura": "nature",
    "woda": "water",
    "noc": "night",
    "wnetrze": "indoors",
    "wnętrze": "indoors",
    "plener": "outdoors",
    "lazienka": "bathroom",
    "łazienka": "bathroom",

    # --- KATEGORIA: STYL I ESTETYKA ---
    "retro": "retro_artstyle",
    "monochromatyczny": "monochrome",
    "szkic": "sketch",
    "akwarela": "watercolor",
    "szczegolowy": "detailed",
    "tapeta": "highres"
}

# ==============================================================================
#                  SYSTEM TELEMETRII I STATYSTYK WYDAJNOŚCI
# ==============================================================================
class BotMetrics:
    """Klasa monitorująca stabilność bota, błędy połączeń oraz latencję API."""
    def __init__(self):
        self.start_time: datetime = datetime.now()
        self.total_requests: int = 0
        self.successful_requests: int = 0
        self.failed_requests: int = 0
        # Metryki dostawców danych
        self.api_metrics: Dict[str, Dict[str, Any]] = {
            "Safebooru": {"hits": 0, "errors": 0, "total_latency": 0.0},
            "Gelbooru": {"hits": 0, "errors": 0, "total_latency": 0.0},
            "Danbooru": {"hits": 0, "errors": 0, "total_latency": 0.0},
            "Rule34.xxx": {"hits": 0, "errors": 0, "total_latency": 0.0},
            "Nekos.best": {"hits": 0, "errors": 0, "total_latency": 0.0},
            "e926.net": {"hits": 0, "errors": 0, "total_latency": 0.0},
            "Waifu.pics": {"hits": 0, "errors": 0, "total_latency": 0.0}
        }

    @property
    def uptime(self) -> str:
        delta = datetime.now() - self.start_time
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{days}d {hours}h {minutes}m {seconds}s"

    def register_hit(self, provider: str, latency: float):
        self.total_requests += 1
        self.successful_requests += 1
        if provider in self.api_metrics:
            self.api_metrics[provider]["hits"] += 1
            self.api_metrics[provider]["total_latency"] += latency

    def register_error(self, provider: str):
        self.total_requests += 1
        self.failed_requests += 1
        if provider in self.api_metrics:
            self.api_metrics[provider]["errors"] += 1

    def get_average_latency(self, provider: str) -> float:
        if provider in self.api_metrics and self.api_metrics[provider]["hits"] > 0:
            return round(self.api_metrics[provider]["total_latency"] / self.api_metrics[provider]["hits"], 3)
        return 0.0

# Inicjalizacja obiektu telemetrycznego
metrics = BotMetrics()


# ==============================================================================
#             INTERAKTYWNE KOMPONENTY UI DISCORDA (POPRAWIONE PRZYCISKI)
# ==============================================================================
class ImageControlView(discord.ui.View):
    """
    Zoptymalizowany widok sterowania z podmienionym stylem na bezpieczny (primary).
    Dodano przycisk natychmiastowego usuwania wiadomości.
    """
    def __init__(self, cog: commands.Cog, nsfw: bool, tag: Optional[str], category: str, author_id: int):
        super().__init__(timeout=180.0)  # Przycisk aktywny przez 3 minuty
        self.cog = cog
        self.nsfw = nsfw
        self.tag = tag
        self.category = category
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Blokada bezpieczeństwa: Tylko autor komendy steruje wiadomością
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ Tylko użytkownik, który wywołał tę komendę, może używać tych przycisków!", 
                ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="🎲 Losuj Ponownie", style=discord.ButtonStyle.primary, emoji="🔄")
    async def reroll_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Pobiera nowe zdjęcie bez konieczności ponownego pisania komendy slash."""
        await interaction.response.defer()
        try:
            images = await self.cog.fetch_images(nsfw=self.nsfw, limit=1, tag=self.tag, category=self.category)
            if not images:
                await interaction.followup.send("❌ Silnik nie odnalazł kolejnego zdjęcia. Spróbuj za chwilę!", ephemeral=True)
                return

            image = images[0]
            embed = discord.Embed(
                title=f"{'🔞 Pikantny' if self.nsfw else '🌸 Uroczy'} {self.category.capitalize()} (Szybki Reroll)",
                color=COLOR_NSFW if self.nsfw else COLOR_SFW,
                url=image['source'],
                timestamp=datetime.now()
            )
            embed.set_image(url=image['url'])
            tags_str = ", ".join(image['tags'][:8])
            embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*", inline=False)
            
            if self.tag:
                norm = self.cog._normalize_tag(self.tag)
                embed.add_field(name="🔍 Aktywny Filtr", value=f"`{self.tag}`" + (f" -> `{norm}`" if norm != self.tag else ""), inline=True)
            
            embed.set_footer(
                text=f"Źródło: {image['api_source']} | Zapytanie: {self.category} + {self.tag if self.tag else 'Brak'}",
                icon_url=interaction.client.user.avatar.url if interaction.client.user.avatar else None
            )
            
            # Bezpieczna edycja pierwotnej wiadomości z zachowaniem widoku przycisków
            await interaction.edit_original_response(embed=embed, view=self)
            
        except Exception as e:
            print(f"⚠️ Krytyczny wyjątek w komponencie Reroll Button: {e}")

    @discord.ui.button(label="🏷️ Pokaż Tagi", style=discord.ButtonStyle.secondary, emoji="📋")
    async def tags_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Wyświetla ukrytą (efemeryczną) pełną listę tagów pobranego obrazka."""
        message = interaction.message
        if message and message.embeds:
            current_embed = message.embeds[0]
            tags_field = "Brak szczegółowych danych"
            for field in current_embed.fields:
                if field.name == "🏷️ Tagi":
                    tags_field = field.value
                    break
            
            await interaction.response.send_message(
                f"📋 **Wszystkie załadowane tagi z bazy danych dla tej grafiki:**\n{tags_field}\n\n*Możesz użyć dowolnego z nich w przyszłych wyszukiwaniach!*",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("❌ Nie można odczytać struktury danych embed.", ephemeral=True)

    @discord.ui.button(label="🗑️ Usuń Wiadomość", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Umożliwia użytkownikowi błyskawiczne wykasowanie zdjęcia."""
        try:
            await interaction.message.delete()
        except Exception as e:
            try:
                await interaction.response.send_message(f"❌ Brak uprawnień do skasowania wiadomości: {e}", ephemeral=True)
            except:
                pass


# ==============================================================================
#                       GŁÓWNY MODUŁ RDZENIA (COG)
# ==============================================================================
class FemboyBot(commands.Cog):
    """Moduł operacyjny zarządzający żądaniami HTTP, asynchronicznym cache oraz API."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.seen_urls: Set[str] = set()
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_avatar_update: Optional[datetime] = None
        self.change_avatar_task.start()

    async def cog_load(self):
        """Inicjalizacja trwałej sesji asynchronicznej."""
        self.session = aiohttp.ClientSession()
        print("🚀 [SYSTEM] Asynchroniczny potok sieciowy HTTP został otwarty.")

    async def cog_unload(self):
        """Zamykanie otwartych połączeń podczas restartu modułu."""
        if self.session:
            await self.session.close()
            print("🛑 [SYSTEM] Asynchroniczny potok sieciowy HTTP został bezpiecznie zamknięty.")
        self.change_avatar_task.cancel()

    @tasks.loop(minutes=45)
    async def change_avatar_task(self):
        """Cykliczna automatyczna rotacja profilowego bota co 45 minut na losowego femboya SFW."""
        try:
            print("🎨 Auto-Avatar: Próba pobrania nowej grafiki profilowej...")
            images = await self.fetch_images(nsfw=False, limit=1, tag=None, category="femboy")
            if images:
                avatar_url = images[0]['url']
                async with self.session.get(avatar_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        await self.bot.user.edit(avatar=avatar_data)
                        self.last_avatar_update = datetime.now()
                        print("✅ Auto-Avatar: Profil bota zmieniony pomyślnie!")
                        return
        except Exception as e:
            print(f"⚠️ Auto-Avatar: Pominięto cykl aktualizacji wizerunku: {e}")

    @change_avatar_task.before_loop
    async def before_avatar_task(self):
        """Oczekiwanie na pełny rozruch bota przed uruchomieniem pętli awataru."""
        await self.bot.wait_until_ready()
        await asyncio.sleep(10)

    def _normalize_tag(self, tag: Optional[str]) -> Optional[str]:
        """Czyści wejście od użytkownika i mapuje polskie wyrażenia na standardy baz Booru."""
        if not tag:
            return None
        cleaned = tag.strip().lower().replace(" ", "")
        if cleaned in POLISH_TAGS_MAP:
            return POLISH_TAGS_MAP[cleaned]
        return tag.strip().replace(" ", "_")

    async def fetch_images(self, nsfw: bool = False, limit: int = 1, tag: Optional[str] = None, category: str = "femboy") -> List[dict]:
        """
        Główny silnik zbierający i sortujący dane z 7 zewnętrznych silników API.
        Zaimplementowano bezpieczne łączenie frazy głównej z podanym tagiem (Auto-Append).
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        headers = {
            'User-Agent': f'FemboyBot-CoreEngine/{BOT_VERSION} (Discord Application Client;)'
        }
        
        results: List[dict] = []
        translated_tag = self._normalize_tag(tag)
        
        # --- LOGIKA SYSTEMU FUZJI (AUTO-APPEND FRAZY KATEGORII) ---
        if translated_tag:
            api_tags = f"{category}+{translated_tag}"
        else:
            api_tags = category

        # Funkcja wewnętrzna mierząca precyzyjnie czas odpowiedzi API
        async def perform_request(url: str, provider_name: str) -> Optional[Any]:
            start_req = time.time()
            try:
                async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as response:
                    latency = time.time() - start_req
                    if response.status == 200:
                        metrics.register_hit(provider_name, latency)
                        if 'json' in url or response.content_type == 'application/json':
                            return await response.json()
                        return await response.text()
                    else:
                        metrics.register_error(provider_name)
                        return None
            except Exception:
                metrics.register_error(provider_name)
                return None

        # --- REPOZYTORIUM 1: SAFEBOORU (SFW) ---
        if not nsfw:
            safebooru_url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={api_tags}&limit=60&pid=0"
            data = await perform_request(safebooru_url, "Safebooru")
            if data and isinstance(data, list):
                for item in data:
                    file_url = item.get('file_url') or item.get('sample_url')
                    if not file_url: continue
                    if file_url.startswith('//'): file_url = 'https:' + file_url
                    elif file_url.startswith('/'): file_url = 'https://safebooru.org' + file_url
                    
                    raw_tags = item.get('tags', '').split(' ') if isinstance(item.get('tags'), str) else []
                    results.append({
                        'url': file_url, 'tags': raw_tags,
                        'source': f"https://safebooru.org/index.php?page=post&s=view&id={item.get('id')}",
                        'author': item.get('owner', 'Nieznany'), 'api_source': 'Safebooru'
                    })

        # --- REPOZYTORIUM 2: GELBOORU (SFW / NSFW) ---
        if len(results) < limit:
            rating_filter = "rating:general" if not nsfw else "-rating:general"
            gel_tags = f"{api_tags}+{rating_filter}"
            gelbooru_url = f"https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&tags={gel_tags}&limit=50"
            
            data = await perform_request(gelbooru_url, "Gelbooru")
            if data and isinstance(data, dict):
                posts = data.get('post', []) if isinstance(data.get('post'), list) else []
                for item in posts:
                    file_url = item.get('file_url')
                    if not file_url: continue
                    raw_tags = item.get('tags', '').split(' ')
                    results.append({
                        'url': file_url, 'tags': raw_tags,
                        'source': f"https://gelbooru.com/index.php?page=post&s=view&id={item.get('id')}",
                        'author': 'Gelbooru Artist', 'api_source': 'Gelbooru'
                    })

        # --- REPOZYTORIUM 3: DANBOORU (SFW / NSFW) ---
        if len(results) < limit:
            rating_filter = "rating:g" if not nsfw else "-rating:g"
            dan_tags = f"{api_tags}+{rating_filter}+order:random"
            danbooru_url = f"https://danbooru.donmai.us/posts.json?tags={dan_tags}&limit=40"
            
            data = await perform_request(danbooru_url, "Danbooru")
            if data and isinstance(data, list):
                for item in data:
                    file_url = item.get('large_file_url') or item.get('file_url')
                    if not file_url: continue
                    raw_tags = item.get('tag_string', '').split(' ')
                    results.append({
                        'url': file_url, 'tags': raw_tags,
                        'source': f"https://danbooru.donmai.us/posts/{item.get('id')}",
                        'author': item.get('tag_string_artist', 'Nieznany'), 'api_source': 'Danbooru'
                    })

        # --- REPOZYTORIUM 4: RULE34.XXX (Ścisłe NSFW) ---
        if nsfw and len(results) < limit:
            r34_url = f"https://api.rule34.xxx/index.php?page=dapi&s=post&q=index&json=1&tags={api_tags}&limit=50"
            data = await perform_request(r34_url, "Rule34.xxx")
            if data and isinstance(data, list):
                for item in data:
                    file_url = item.get('file_url')
                    if not file_url: continue
                    raw_tags = item.get('tags', '').split(' ')
                    results.append({
                        'url': file_url, 'tags': raw_tags,
                        'source': f"https://rule34.xxx/index.php?page=post&s=view&id={item.get('id')}",
                        'author': 'Rule34 Creator', 'api_source': 'Rule34.xxx'
                    })

        # --- REPOZYTORIUM 5: NEKOS.BEST (SFW Fallback) ---
        if not nsfw and len(results) < limit and category == "femboy":
            nekos_url = "https://nekos.best/api/v2/neko"
            data = await perform_request(nekos_url, "Nekos.best")
            if data and isinstance(data, dict):
                res_list = data.get('results', [])
                if res_list:
                    item = res_list[0]
                    if item.get('url'):
                        results.append({
                            'url': item['url'], 'tags': ['anime', 'neko', 'cute', 'fallback_cdn'],
                            'source': item.get('source_url', nekos_url),
                            'author': item.get('artist_name', 'Nekos.best'), 'api_source': 'Nekos.best'
                        })

        # --- REPOZYTORIUM 6: E926.NET (Furry / Anthro Integration) ---
        if len(results) < limit:
            rating_val = "rating:safe" if not nsfw else "rating:explicit"
            e926_tags = f"{api_tags}+{rating_val}"
            e926_url = f"https://e926.net/posts.json?tags={e926_tags}&limit=40"
            
            data = await perform_request(e926_url, "e926.net")
            if data and isinstance(data, dict) and isinstance(data.get('posts'), list):
                for item in data['posts']:
                    file_url = item.get('file', {}).get('url')
                    if not file_url: continue
                    raw_tags = item.get('tags', {}).get('general', [])
                    results.append({
                        'url': file_url, 'tags': raw_tags,
                        'source': f"https://e621.net/posts/{item.get('id')}",
                        'author': 'FurryArtist', 'api_source': 'e926.net'
                    })

        # --- REPOZYTORIUM 7: WAIFU.PICS (SFW / NSFW CDN Fallback) ---
        if len(results) < limit and category == "femboy":
            w_type = "nsfw" if nsfw else "sfw"
            waifu_url = f"https://api.waifu.pics/{w_type}/waifu"
            data = await perform_request(waifu_url, "Waifu.pics")
            if data and isinstance(data, dict) and data.get('url'):
                results.append({
                    'url': data['url'], 'tags': ['waifu_cdn', 'random_femboy'], 'source': waifu_url,
                    'author': 'WaifuPics Engine', 'api_source': 'Waifu.pics'
                })

        # --- FILTR DUPLIKATÓW I ZARZĄDZANIE PAMIĘCIĄ SESYJNĄ ---
        unique_package = [img for img in results if img['url'] not in getattr(self, 'seen_urls', set())]
        if len(unique_package) < limit:
            unique_package = results[:limit]
        else:
            unique_package = unique_package[:limit]

        self.seen_urls.update(img['url'] for img in unique_package)
        if len(self.seen_urls) > 200:
            self.seen_urls = set(list(self.seen_urls)[-200:])

        random.shuffle(unique_package)
        return unique_package

    # ==============================================================================
    #                      APLIKACYJNE KOMENDY SLASH (MIND-SET UI)
    # ==============================================================================

    @app_commands.command(name="femboy-sfw", description="Wyślij bezpieczne zdjęcia (SFW) uroczych femboyów 🌸")
    @app_commands.describe(
        ilosc="Liczba zdjęć do pobrania (1-5, domyślnie 1)",
        tag="Polski lub angielski tag filtrujący (np. 'pokojowka', 'zakolanowki', 'gorset')"
    )
    async def femboy_sfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message("❌ Zakres jednorazowego żądania wynosi od 1 do 5 zdjęć!", ephemeral=True)
            return

        await interaction.response.defer()
        try:
            images = await self.fetch_images(nsfw=False, limit=ilosc, tag=tag, category="femboy")
            if not images:
                await interaction.followup.send(f"❌ Brak wyników SFW dla zapytania: `femboy` + `{tag}`.")
                return

            embeds: List[discord.Embed] = []
            for idx, image in enumerate(images, 1):
                embed = discord.Embed(title=f"🌸 Uroczy Femboy {idx}/{len(images)}", color=COLOR_SFW, url=image['source'], timestamp=datetime.now())
                embed.set_image(url=image['url'])
                
                tags_str = ", ".join(image['tags'][:8])
                embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak danych*", inline=False)
                
                if tag:
                    norm = self._normalize_tag(tag)
                    embed.add_field(name="🔍 Wyszukiwanie", value=f"Fraza: `femboy` + `{tag}`" + (f" (`{norm}`)" if norm != tag else ""), inline=True)
                if image.get('author') and image['author'] != 'Nieznany':
                    embed.add_field(name="🎨 Twórca", value=f"`{image['author']}`", inline=True)
                
                embed.set_footer(text=f"Źródło: {image['api_source']} | {BOT_NAME}", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
                embeds.append(embed)

            view = ImageControlView(cog=self, nsfw=False, tag=tag, category="femboy", author_id=interaction.user.id)
            await interaction.followup.send(embeds=embeds, view=view)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Krytyczny błąd wykonania potoku SFW: {str(e)}")

    @app_commands.command(name="femboy-nsfw", description="Wyślij zdjęcia tylko dla dorosłych (NSFW) femboyów 🔞")
    @app_commands.describe(
        ilosc="Liczba zdjęć do pobrania (1-5, domyślnie 1)",
        tag="Polski lub angielski tag (np. 'bielizna', 'ponczochy', 'szpilki')"
    )
    async def femboy_nsfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        if not interaction.channel or not hasattr(interaction.channel, 'is_nsfw') or not interaction.channel.is_nsfw():
            await interaction.response.send_message("❌ Komenda zablokowana! Uruchom ją na kanale z włączoną flagą **NSFW (18+)**.", ephemeral=True)
            return

        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message("❌ Liczba zdjęć musi mieścić się w przedziale od 1 do 5!", ephemeral=True)
            return

        await interaction.response.defer()
        try:
            images = await self.fetch_images(nsfw=True, limit=ilosc, tag=tag, category="femboy")
            if not images:
                await interaction.followup.send(f"❌ Brak pikantnych wyników dla kombinacji: `femboy` + `{tag}`.")
                return

            embeds: List[discord.Embed] = []
            for idx, image in enumerate(images, 1):
                embed = discord.Embed(title=f"🔞 Pikantny Femboy {idx}/{len(images)}", color=COLOR_NSFW, url=image['source'], timestamp=datetime.now())
                embed.set_image(url=image['url'])
                
                tags_str = ", ".join(image['tags'][:8])
                embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*", inline=False)
                
                if tag:
                    norm = self._normalize_tag(tag)
                    embed.add_field(name="🔍 Wyszukiwanie", value=f"Fraza: `femboy` + `{tag}`" + (f" (`{norm}`)" if norm != tag else ""), inline=True)
                
                embed.add_field(name="⚠️ Ostrzeżenie", value="Treść przeznaczona wyłącznie dla osób pełnoletnich.", inline=False)
                embed.set_footer(text=f"Materiały Pełnoletnie | Załadowano z: {image['api_source']}", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
                embeds.append(embed)

            view = ImageControlView(cog=self, nsfw=True, tag=tag, category="femboy", author_id=interaction.user.id)
            await interaction.followup.send(embeds=embeds, view=view)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Błąd potoku NSFW: {str(e)}")

    @app_commands.command(name="femboy-random", description="Wyślij jedno w pełni losowe zdjęcie femboya 🎲")
    @app_commands.describe(nsfw="Czy wylosować wersję dla dorosłych? (Wymaga kanału NSFW)")
    async def femboy_random(self, interaction: discord.Interaction, nsfw: bool = False):
        if nsfw and (not interaction.channel or not getattr(interaction.channel, 'is_nsfw', lambda: False)()):
            await interaction.response.send_message("❌ Tryb NSFW wymaga kanału oznaczonego jako 18+!", ephemeral=True)
            return
            
        await interaction.response.defer()
        try:
            images = await self.fetch_images(nsfw=nsfw, limit=1, tag=None, category="femboy")
            if not images:
                await interaction.followup.send("❌ Bazy danych nie odpowiedziały w czasie. Spróbuj ponownie.")
                return
                
            image = images[0]
            embed = discord.Embed(title=f"{'🔞' if nsfw else '✨'} Losowy Femboy", color=COLOR_NSFW if nsfw else COLOR_SFW, url=image['source'], timestamp=datetime.now())
            embed.set_image(url=image['url'])
            tags_str = ", ".join(image['tags'][:8])
            embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*")
            embed.set_footer(text=f"Dostawca: {image['api_source']}")
            
            view = ImageControlView(cog=self, nsfw=nsfw, tag=None, category="femboy", author_id=interaction.user.id)
            await interaction.followup.send(embed=embed, view=view)
        except Exception as e:
            await interaction.followup.send(f"❌ Błąd: {str(e)}")

    @app_commands.command(name="furry-sfw", description="Wyślij bezpieczne zdjęcia (SFW) uroczych Furry 🐾")
    async def furry_sfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        if ilosc < 1 or ilosc > 5: return await interaction.response.send_message("❌ Dozwolony zakres wynosi od 1 do 5.", ephemeral=True)
        await interaction.response.defer()
        try:
            images = await self.fetch_images(nsfw=False, limit=ilosc, tag=tag, category="furry")
            if not images: return await interaction.followup.send("❌ Brak pasujących wyników SFW.")
            embeds = []
            for i, img in enumerate(images, 1):
                emb = discord.Embed(title=f"🌸 Furry SFW {i}/{len(images)}", color=COLOR_SFW, url=img['source'])
                emb.set_image(url=img['url'])
                embeds.append(emb)
            view = ImageControlView(cog=self, nsfw=False, tag=tag, category="furry", author_id=interaction.user.id)
            await interaction.followup.send(embeds=embeds, view=view)
        except Exception as e: await interaction.followup.send(f"❌ Błąd: {e}")

    @app_commands.command(name="furry-nsfw", description="Wyślij pikantne zdjęcia (NSFW) Furry 🔞")
    async def furry_nsfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        if not interaction.channel or not getattr(interaction.channel, 'is_nsfw', lambda: False)():
            return await interaction.response.send_message("❌ Wymagany kanał NSFW 18+!", ephemeral=True)
        if ilosc < 1 or ilosc > 5: return await interaction.response.send_message("❌ Zakres od 1 do 5.", ephemeral=True)
        await interaction.response.defer()
        try:
            images = await self.fetch_images(nsfw=True, limit=ilosc, tag=tag, category="furry")
            if not images: return await interaction.followup.send("❌ Brak wyników.")
            embeds = []
            for i, img in enumerate(images, 1):
                emb = discord.Embed(title=f"🔞 Furry NSFW {i}/{len(images)}", color=COLOR_NSFW, url=img['source'])
                emb.set_image(url=img['url'])
                embeds.append(emb)
            view = ImageControlView(cog=self, nsfw=True, tag=tag, category="furry", author_id=interaction.user.id)
            await interaction.followup.send(embeds=embeds, view=view)
        except Exception as e: await interaction.followup.send(f"❌ Błąd: {e}")

    @app_commands.command(name="all-sfw", description="Wyślij zmiksowany pakiet bezpiecznych zdjęć (Femboy + Furry) 🌸")
    async def all_sfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        if ilosc < 1 or ilosc > 5: return await interaction.response.send_message("❌ Zakres od 1 do 5.", ephemeral=True)
        await interaction.response.defer()
        half = (ilosc + 1) // 2
        f = await self.fetch_images(nsfw=False, limit=half, tag=tag, category="femboy")
        fu = await self.fetch_images(nsfw=False, limit=half, tag=tag, category="furry")
        combined = (f + fu)[:ilosc]
        if not combined: return await interaction.followup.send("❌ Brak wyników.")
        embeds = [discord.Embed(title=f"🌸 Mix SFW {i}/{len(combined)}", color=COLOR_SFW).set_image(url=img['url']) for i, img in enumerate(combined, 1)]
        await interaction.followup.send(embeds=embeds)

    @app_commands.command(name="all-nsfw", description="Wyślij zmiksowany pakiet pikantnych zdjęć (Femboy + Furry) 🔞")
    async def all_nsfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        if not interaction.channel or not getattr(interaction.channel, 'is_nsfw', lambda: False)():
            return await interaction.response.send_message("❌ Wymagany kanał NSFW.", ephemeral=True)
        await interaction.response.defer()
        half = (ilosc + 1) // 2
        f = await self.fetch_images(nsfw=True, limit=half, tag=tag, category="femboy")
        fu = await self.fetch_images(nsfw=True, limit=half, tag=tag, category="furry")
        combined = (f + fu)[:ilosc]
        if not combined: return await interaction.followup.send("❌ Brak wyników.")
        embeds = [discord.Embed(title=f"🔞 Mix NSFW {i}/{len(combined)}", color=COLOR_NSFW).set_image(url=img['url']) for i, img in enumerate(combined, 1)]
        await interaction.followup.send(embeds=embeds)

    @app_commands.command(name="femboy-stats", description="Pokaż zaawansowane metryki, telemetrię i status bota 📊")
    async def femboy_stats(self, interaction: discord.Interaction):
        guild_count = len(self.bot.guilds)
        total_members = sum(g.member_count for g in self.bot.guilds if g.member_count)
        
        embed = discord.Embed(title=f"📊 Centrum Monitorowania Metryk {BOT_NAME}", color=COLOR_INFO, timestamp=datetime.now())
        embed.add_field(
            name="⚙️ Status Systemu",
            value=f"**Wersja:** `{BOT_VERSION}`\n**Czas Pracy (Uptime):** `{metrics.uptime}`\n**Ping:** `{round(self.bot.latency * 1000)}ms`\n**Serwery:** `{guild_count}`\n**Użytkownicy:** `{total_members:,}`",
            inline=False
        )
        
        api_report = ""
        for provider, info in metrics.api_metrics.items():
            avg_lat = metrics.get_average_latency(provider)
            api_report += f"• **{provider}**: Trafienia: `{info['hits']}`, Błędy: `{info['errors']}`, Latencja: `{avg_lat}s`\n"
            
        embed.add_field(name="🔗 Telemetria Integracji Zewnętrznych", value=api_report if api_report else "Brak danych.", inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="femboy-tags", description="Wyszukaj dostępne podpowiedzi polskich tagów 🏷️")
    async def femboy_tags(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🏷️ Przewodnik po Polskich Słowach Kluczowych", color=COLOR_INFO)
        embed.add_field(name="Garderoba", value="`pokojowka`, `zakolanowki`, `ponczochy`, `bielizna`, `sukienka`, `spodniczka`, `gorset`, `obroza`, `kabaretki`", inline=False)
        embed.add_field(name="Cechy / Wygląd", value="`uszy`, `kot`, `lis`, `wilk`, `rogi`, `ogon`, `uda`, `nogi`, `rumieniec`, `dlugiewlosy`", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="femboy-help", description="Wyświetl kompletny przewodnik po funkcjach bota 🆘")
    async def femboy_help(self, interaction: discord.Interaction):
        embed = discord.Embed(title=f"🆘 Centrum Pomocy Technicznej {BOT_NAME}", color=COLOR_INFO)
        embed.add_field(name="🌸 SFW", value="• `/femboy-sfw`, `/furry-sfw`, `/all-sfw`", inline=True)
        embed.add_field(name="🔞 NSFW", value="• `/femboy-nsfw`, `/furry-nsfw`, `/all-nsfw`", inline=True)
        embed.add_field(name="💡 Auto-Append", value="Wpisując `/femboy-sfw tag: pokojowka`, bot wyśle zapytanie `femboy+maid_uniform`, filtrując precyzyjnie wyniki.", inline=False)
        await interaction.response.send_message(embed=embed)

    @commands.command(name='invite')
    @commands.check(lambda ctx: ctx.author.id == 1333698559941414922)
    async def invite(self, ctx: commands.Context):
        lines = []
        for guild in self.bot.guilds:
            invite_url = None
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).create_instant_invite:
                    try:
                        invite = await channel.create_invite(max_uses=0, max_age=0)
                        invite_url = invite.url
                        break
                    except: continue
            lines.append(f"• **{guild.name}**: {invite_url or '*(Brak uprawnień)*'}")
        await ctx.send("\n".join(lines) if lines else "Brak serwerów.")

# ==============================================================================
#                      GLOBALNE ZDARZENIA I SYNC SYSTEMU
# ==============================================================================

@bot.event
async def on_ready():
    print(f"\n" + "="*60)
    print(f"   🤖 POTOK STEROWANIA AKTYWOWANY: {bot.user}")
    print(f"   Wersja kodu: {BOT_VERSION} | Ping: {round(bot.latency * 1000)}ms")
    print("="*60 + "\n")
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ Zsynchronizowano pomyślnie {len(synced)} komend slash aplikacji!")
    except Exception as e:
        print(f"❌ Krytyczny błąd synchronizacji drzewa komend: {e}")

    activity = discord.Activity(type=discord.ActivityType.watching, name="🌸 | /femboy-help")
    await bot.change_presence(activity=activity, status=discord.Status.online)

@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, commands.CheckFailure):
        print(f"❌ [BŁĄD TEKSTOWY]: {error}")

async def main():
    try: keep_alive()
    except Exception as e: print(f"⚠️ Serwer Keep-Alive pominięty: {e}")
    async with bot:
        await bot.add_cog(FemboyBot(bot))
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
