import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiohttp
import random
import asyncio
from typing import Optional, List
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
BOT_VERSION = "2.0"

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Color constants for embeds
COLOR_SFW = 0xFF69B4      # Hot pink
COLOR_NSFW = 0x9D00FF     # Purple
COLOR_AVATAR = 0xFF1493   # Deep pink
COLOR_INFO = 0x00D4FF     # Cyan

# Avatar APIs that return femboy images
AVATAR_APIS = [
    "https://api.femboy.pics/v2/femboy?type=sfw",
    "https://api.waifu.pics/sfw/trap",  # Alternative API
]

class FemboyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.last_avatar_update = None
        self.avatar_change_interval = 3600  # Change avatar every hour (3600 seconds)
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
        """Periodically change bot avatar from API"""
        try:
            print(f"🎨 Próba zmiany avatara bota...")
            avatar_url = await self.fetch_random_avatar()
            if avatar_url:
                async with self.session.get(avatar_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        avatar_data = await resp.read()
                        await self.bot.user.edit(avatar=avatar_data)
                        self.last_avatar_update = datetime.now()
                        print(f"✅ Avatar zmieniony pomyślnie!")
                        return
        except Exception as e:
            print(f"⚠️ Nie można zmienić avatara: {e}")

    @change_avatar_task.before_loop
    async def before_avatar_task(self):
        """Wait for bot to be ready before starting avatar task"""
        await self.bot.wait_until_ready()
        await asyncio.sleep(5)

    async def fetch_random_avatar(self) -> Optional[str]:
        """Fetch random femboy avatar from APIs"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        for api_url in AVATAR_APIS:
            try:
                async with self.session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if 'image' in data:
                            return data['image']
                        elif 'url' in data:
                            return data['url']
            except Exception as e:
                print(f"❌ Błąd API {api_url}: {e}")
                continue
        
        return None

    async def fetch_femboy_images_from_api(self, api_url: str, nsfw: bool = False, tag: Optional[str] = None) -> Optional[dict]:
        """Fetch image from specific API"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            params = {}
            if "femboy.pics" in api_url and nsfw:
                params["type"] = "nsfw"
            elif "femboy.pics" in api_url:
                params["type"] = "sfw"
            
            async with self.session.get(api_url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Normalize different API response formats
                    image_url = data.get('image') or data.get('url') or data.get('images', [None])[0]
                    tags = data.get('tags', [])
                    source = data.get('source', api_url)
                    
                    if not image_url:
                        return None
                    
                    # Filter by tag if provided
                    if tag:
                        tag_lower = tag.lower()
                        if not any(tag_lower in t.lower() for t in tags) and tag_lower not in image_url.lower():
                            return None
                    
                    return {
                        'url': image_url,
                        'tags': tags,
                        'source': source
                    }
        except Exception as e:
            print(f"❌ Błąd pobierania z {api_url}: {e}")
            return None

        return None

    async def fetch_femboy_images(self, nsfw: bool = False, count: int = 1, tag: Optional[str] = None) -> List[dict]:
        """
        Fetch femboy images from multiple APIs with fallback
        
        Args:
            nsfw: Whether to fetch NSFW content
            count: Number of images to fetch (1-5)
            tag: Optional tag/theme to filter results
            
        Returns:
            List of image dictionaries with url and info
        """
        # List of APIs (in priority order)
        apis = [
            "https://api.femboy.pics/v2/femboy",
            "https://api.waifu.pics/sfw/trap",
            "https://api.waifu.pics/nsfw/trap" if nsfw else "https://api.waifu.pics/sfw/trap",
        ]
        
        images = []
        attempts = 0
        max_attempts = count * 3  # Try up to 3 times per image
        
        while len(images) < count and attempts < max_attempts:
            attempts += 1
            api = random.choice(apis)
            
            result = await self.fetch_femboy_images_from_api(api, nsfw=nsfw, tag=tag)
            if result and result['url']:
                images.append(result)
        
        return images

    @app_commands.command(name="femboy-sfw", description="Wyślij bezpieczne zdjęcia femboyów 🌸")
    @app_commands.describe(
        ilosc="Liczba zdjęć (1-5)",
        tag="Opcjonalny tag/temat (np. 'cosplay', 'maid', 'catgirl')"
    )
    async def femboy_sfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """
        Send SFW femboy images
        """
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message(
                "❌ Liczba zdjęć musi być od 1 do 5!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            images = await self.fetch_femboy_images(nsfw=False, count=ilosc, tag=tag)
            
            if not images or not any(img['url'] for img in images):
                await interaction.followup.send(
                    f"❌ Nie znaleziono zdjęć pasujących do zapytania." + 
                    (f" (tag: {tag})" if tag else "") + 
                    "\nSpróbuj ponownie!"
                )
                return

            for idx, image in enumerate(images, 1):
                if not image['url']:
                    continue
                    
                embed = discord.Embed(
                    title=f"✨ Femboy {idx}/{len(images)}",
                    color=COLOR_SFW,
                    timestamp=datetime.now()
                )
                embed.set_image(url=image['url'])
                
                if image.get('tags'):
                    tags_str = ", ".join(image['tags'][:6])
                    embed.add_field(name="🏷️ Tagi", value=tags_str, inline=False)
                
                if tag:
                    embed.add_field(name="🔍 Szukane", value=f"`{tag}`", inline=True)
                
                embed.set_footer(
                    text=f"Źródło: {image.get('source', 'API')} | Powered by {BOT_NAME}",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            print(f"Error in femboy_sfw: {e}")
            await interaction.followup.send(
                f"❌ Błąd podczas pobierania zdjęć: {str(e)}"
            )

    @app_commands.command(name="femboy-nsfw", description="Wyślij zdjęcia dla dorosłych 🔞")
    @app_commands.describe(
        ilosc="Liczba zdjęć (1-5)",
        tag="Opcjonalny tag/temat"
    )
    async def femboy_nsfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """
        Send NSFW femboy images - only works in NSFW channels
        """
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Ta komenda dostępna jest tylko na kanałach z włączonym NSFW!\n"
                "🔞 Oznacz kanał jako NSFW w ustawieniach.",
                ephemeral=True
            )
            return

        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message(
                "❌ Liczba zdjęć musi być od 1 do 5!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            images = await self.fetch_femboy_images(nsfw=True, count=ilosc, tag=tag)
            
            if not images or not any(img['url'] for img in images):
                await interaction.followup.send(
                    f"❌ Nie znaleziono zdjęć pasujących do zapytania." +
                    (f" (tag: {tag})" if tag else "") +
                    "\nSpróbuj ponownie!"
                )
                return

            for idx, image in enumerate(images, 1):
                if not image['url']:
                    continue
                    
                embed = discord.Embed(
                    title=f"🔞 Femboy NSFW {idx}/{len(images)}",
                    color=COLOR_NSFW,
                    timestamp=datetime.now()
                )
                embed.set_image(url=image['url'])
                
                if image.get('tags'):
                    tags_str = ", ".join(image['tags'][:6])
                    embed.add_field(name="🏷️ Tagi", value=tags_str, inline=False)
                
                if tag:
                    embed.add_field(name="🔍 Szukane", value=f"`{tag}`", inline=True)
                
                embed.add_field(name="⚠️ Uwaga", value="Treść tylko dla dorosłych", inline=True)
                
                embed.set_footer(
                    text=f"Źródło: {image.get('source', 'API')} | Powered by {BOT_NAME}",
                    icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
                )
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            print(f"Error in femboy_nsfw: {e}")
            await interaction.followup.send(
                f"❌ Błąd podczas pobierania zdjęć: {str(e)}"
            )

    @app_commands.command(name="femboy-random", description="Wyślij losowe zdjęcie 🎲")
    @app_commands.describe(
        nsfw="Czy wyślijemy NSFW? (wymaga kanału NSFW)"
    )
    async def femboy_random(self, interaction: discord.Interaction, nsfw: bool = False):
        """Send a random femboy image"""
        if nsfw and not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ NSFW dostępne tylko na kanałach z włączonym NSFW!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            images = await self.fetch_femboy_images(nsfw=nsfw, count=1)
            
            if not images or not images[0]['url']:
                await interaction.followup.send("❌ Nie można pobrać zdjęcia. Spróbuj później!")
                return

            image = images[0]
            prefix = "🔞 " if nsfw else "✨ "
            
            embed = discord.Embed(
                title=f"{prefix}Losowe zdjęcie",
                color=COLOR_NSFW if nsfw else COLOR_SFW,
                timestamp=datetime.now()
            )
            embed.set_image(url=image['url'])
            
            if image.get('tags'):
                tags_str = ", ".join(image['tags'][:6])
                embed.add_field(name="🏷️ Tagi", value=tags_str, inline=False)
            
            embed.set_footer(text=f"🎲 Powered by {BOT_NAME}")
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Error in femboy_random: {e}")
            await interaction.followup.send(f"❌ Błąd: {str(e)}")

    @app_commands.command(name="femboy-stats", description="Pokaż informacje o bocie 📊")
    async def femboy_stats(self, interaction: discord.Interaction):
        """Show bot statistics and info"""
        
        guild_count = len(self.bot.guilds)
        user_count = sum(g.member_count for g in self.bot.guilds if g.member_count)
        
        embed = discord.Embed(
            title=f"📊 Statystyki {BOT_NAME}",
            color=COLOR_INFO,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="ℹ️ Informacje",
            value=f"**Nazwa:** {BOT_NAME}\n**Wersja:** {BOT_VERSION}\n**Ping:** {round(self.bot.latency * 1000)}ms",
            inline=False
        )
        
        embed.add_field(
            name="📈 Statystyki",
            value=f"**Serwery:** {guild_count}\n**Użytkownicy:** {user_count:,}",
            inline=False
        )
        
        if self.last_avatar_update:
            embed.add_field(
                name="🎨 Avatar",
                value=f"Ostatnia zmiana: <t:{int(self.last_avatar_update.timestamp())}:R>",
                inline=False
            )
        
        embed.add_field(
            name="🔗 API",
            value="Korzystamy z:\n• `api.femboy.pics`\n• `api.waifu.pics`",
            inline=False
        )
        
        embed.add_field(
            name="📖 Komendy",
            value="• `/femboy-sfw` - Bezpieczne zdjęcia\n• `/femboy-nsfw` - Dla dorosłych\n• `/femboy-random` - Losowe\n• `/femboy-stats` - Ta komenda",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text=f"Powered by {BOT_NAME} v{BOT_VERSION}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="femboy-help", description="Pokaż pomoc 🆘")
    async def femboy_help(self, interaction: discord.Interaction):
        """Show help message"""
        
        embed = discord.Embed(
            title=f"🆘 Pomoc {BOT_NAME}",
            color=COLOR_INFO,
            description="Kompletny przewodnik po wszystkich komendach",
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="📸 /femboy-sfw",
            value="Wyślij bezpieczne zdjęcia femboyów\n"
                  "`ilosc:` liczba (1-5)\n"
                  "`tag:` opcjonalny filtr (cosplay, maid, itd.)",
            inline=False
        )
        
        embed.add_field(
            name="🔞 /femboy-nsfw",
            value="Wyślij zdjęcia dla dorosłych (tylko kanały NSFW)\n"
                  "`ilosc:` liczba (1-5)\n"
                  "`tag:` opcjonalny filtr",
            inline=False
        )
        
        embed.add_field(
            name="🎲 /femboy-random",
            value="Wyślij jedno losowe zdjęcie\n"
                  "`nsfw:` czy NSFW? (tak/nie)",
            inline=False
        )
        
        embed.add_field(
            name="📊 /femboy-stats",
            value="Pokaż statystyki bota",
            inline=False
        )
        
        embed.add_field(
            name="🆘 /femboy-help",
            value="Pokaż tę wiadomość",
            inline=False
        )
        
        embed.add_field(
            name="💡 Tipy",
            value="• Bot zmienia avatar co godzinę 🎨\n"
                  "• Wszystkie API są darmowe i bezpieczne\n"
                  "• Użyj tagów do filtrowania wyników",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        embed.set_footer(text=f"Powered by {BOT_NAME} v{BOT_VERSION}")
        
        await interaction.response.send_message(embed=embed)


@bot.event
async def on_ready():
    print(f"\n{'='*50}")
    print(f"✅ {BOT_NAME} v{BOT_VERSION} zalogowany pomyślnie!")
    print(f"✅ Bot: {bot.user}")
    print(f"✅ Ping: {round(bot.latency * 1000)}ms")
    print(f"{'='*50}\n")
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ Zsynchronizowano {len(synced)} komend slash")
        print(f"✅ Serwery: {len(bot.guilds)}")
        print(f"{'='*50}\n")
    except Exception as e:
        print(f"❌ Błąd synchronizacji komend: {e}")

    # Set presence/status
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="✨ femboyów | /femboy-help 🎀"
    )
    await bot.change_presence(activity=activity, status=discord.Status.online)


@bot.event
async def on_command_error(ctx, error):
    print(f"❌ Command error: {error}")


async def main():
    async with bot:
        await bot.add_cog(FemboyBot(bot))
        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
