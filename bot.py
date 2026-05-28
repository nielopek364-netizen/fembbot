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
BOT_VERSION = "2.1"

bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Color constants for embeds
COLOR_SFW = 0xFF69B4      # Hot pink
COLOR_NSFW = 0x9D00FF     # Purple
COLOR_AVATAR = 0xFF1493   # Deep pink
COLOR_INFO = 0x00D4FF     # Cyan

# Working APIs
AVATAR_APIS = [
    "https://api.waifu.pics/sfw/waifu",
    "https://api.waifu.pics/sfw/neko",
]

class FemboyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
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
        """Fetch random avatar from APIs"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        for api_url in AVATAR_APIS:
            try:
                async with self.session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if 'url' in data:
                            return data['url']
            except Exception as e:
                print(f"❌ Błąd API {api_url}: {e}")
                continue
        
        return None

    async def fetch_from_waifu_api(self, category: str) -> Optional[dict]:
        """Fetch image from api.waifu.pics"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            url = f"https://api.waifu.pics/sfw/{category}"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'url' in data:
                        return {
                            'url': data['url'],
                            'tags': [category],
                            'source': 'api.waifu.pics'
                        }
        except Exception as e:
            print(f"❌ Błąd Waifu API ({category}): {e}")
        
        return None

    async def fetch_from_nekos_api(self, action: str = "tickle") -> Optional[dict]:
        """Fetch image from api.nekos.life"""
        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            url = f"https://api.nekos.life/v2/img/{action}"
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'url' in data:
                        return {
                            'url': data['url'],
                            'tags': [action, 'anime'],
                            'source': 'api.nekos.life'
                        }
        except Exception as e:
            print(f"❌ Błąd Nekos API ({action}): {e}")
        
        return None

    async def fetch_random_image(self, nsfw: bool = False, tag: Optional[str] = None) -> Optional[dict]:
        """Fetch random image from working APIs"""
        # SFW categories
        sfw_categories = ["waifu", "neko", "shinobu", "mitsuri", "mitsuri"]
        
        # NSFW categories (with fallback to SFW)
        nsfw_actions = ["tickle", "slap", "waifu"]
        
        # Wybierz kategorię
        if nsfw:
            category = random.choice(nsfw_actions)
            # Spróbuj Nekos API dla NSFW
            result = await self.fetch_from_nekos_api(category)
            if result:
                return result
        
        # Fallback: Waifu API (zawsze dostępne)
        category = random.choice(sfw_categories)
        result = await self.fetch_from_waifu_api(category)
        
        if result:
            # Filtruj po tagu jeśli podano
            if tag:
                tag_lower = tag.lower()
                if tag_lower in result['url'].lower() or tag_lower in [t.lower() for t in result['tags']]:
                    return result
                # Jeśli tag nie pasuje, zwróć i tak (bo API ma limit)
                return result
            return result
        
        return None

    @app_commands.command(name="femboy-sfw", description="Wyślij bezpieczne zdjęcia 🌸")
    @app_commands.describe(
        ilosc="Liczba zdjęć (1-5)",
        tag="Opcjonalny tag/temat (np. 'cosplay', 'maid')"
    )
    async def femboy_sfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """Send SFW images"""
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message(
                "❌ Liczba zdjęć musi być od 1 do 5!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            images = []
            attempts = 0
            max_attempts = ilosc * 5
            
            while len(images) < ilosc and attempts < max_attempts:
                attempts += 1
                image = await self.fetch_random_image(nsfw=False, tag=tag)
                
                if image and image['url']:
                    images.append(image)

            if not images:
                await interaction.followup.send(
                    f"❌ Nie znaleziono zdjęć. Spróbuj ponownie!" + 
                    (f" (tag: {tag})" if tag else "")
                )
                return

            for idx, image in enumerate(images, 1):
                embed = discord.Embed(
                    title=f"✨ Zdjęcie {idx}/{len(images)}",
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
            await interaction.followup.send(f"❌ Błąd: {str(e)}")

    @app_commands.command(name="femboy-nsfw", description="Wyślij zdjęcia dla dorosłych 🔞")
    @app_commands.describe(
        ilosc="Liczba zdjęć (1-5)",
        tag="Opcjonalny tag/temat"
    )
    async def femboy_nsfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """Send NSFW images - only in NSFW channels"""
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
            images = []
            attempts = 0
            max_attempts = ilosc * 5
            
            while len(images) < ilosc and attempts < max_attempts:
                attempts += 1
                image = await self.fetch_random_image(nsfw=True, tag=tag)
                
                if image and image['url']:
                    images.append(image)

            if not images:
                await interaction.followup.send(
                    f"❌ Nie znaleziono zdjęć." +
                    (f" (tag: {tag})" if tag else "") +
                    "\nSpróbuj ponownie!"
                )
                return

            for idx, image in enumerate(images, 1):
                embed = discord.Embed(
                    title=f"🔞 Zdjęcie NSFW {idx}/{len(images)}",
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
            await interaction.followup.send(f"❌ Błąd: {str(e)}")

    @app_commands.command(name="femboy-random", description="Wyślij losowe zdjęcie 🎲")
    @app_commands.describe(
        nsfw="Czy wyślijemy NSFW? (wymaga kanału NSFW)"
    )
    async def femboy_random(self, interaction: discord.Interaction, nsfw: bool = False):
        """Send a random image"""
        if nsfw and not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ NSFW dostępne tylko na kanałach z włączonym NSFW!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            image = await self.fetch_random_image(nsfw=nsfw)
            
            if not image or not image['url']:
                await interaction.followup.send("❌ Nie można pobrać zdjęcia. Spróbuj później!")
                return

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
            value=f"**Nazwa:** {BOT_NAME}\n**Wersja:** {BOT_VERSION}\n**Ping:** {round(self.bot.latency * 1000)}ms",
            inline=False
        )
        
        embed.add_field(
            name="📈 Statystyki",
            value=f"**Serwery:** {guild_count}\n**Użytkownicy:** {user_count:,}",
            inline=False
        )
        
        embed.add_field(
            name="🔗 API",
            value="Korzystamy z:\n• `api.waifu.pics`\n• `api.nekos.life`",
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
            value="Wyślij bezpieczne zdjęcia\n"
                  "`ilosc:` liczba (1-5)\n"
                  "`tag:` opcjonalny filtr",
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
            name="💡 Tipy",
            value="• Bot zmienia avatar co godzinę 🎨\n"
                  "• Wszystkie API są darmowe i bezpieczne\n"
                  "• Używaj komend bez tagu, aby było szybciej",
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

    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="✨ zdjęcia | /femboy-help 🎀"
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
