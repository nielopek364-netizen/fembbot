import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import random
from typing import Optional, List
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKEN not set in environment variables")

# Initialize bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Color constants for embeds
COLOR_SFW = 0xFF69B4  # Hot pink
COLOR_NSFW = 0x9D00FF  # Purple

class FemboyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = None

    async def cog_load(self):
        """Initialize HTTP session when cog loads"""
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        """Close HTTP session when cog unloads"""
        if self.session:
            await self.session.close()

    async def fetch_femboy_images(self, nsfw: bool = False, count: int = 1, tag: Optional[str] = None) -> List[dict]:
        """
        Fetch femboy images from api.femboy.pics
        
        Args:
            nsfw: Whether to fetch NSFW content
            count: Number of images to fetch (1-5)
            tag: Optional tag/theme to filter results
            
        Returns:
            List of image dictionaries with url and info
        """
        if not self.session:
            self.session = aiohttp.ClientSession()

        images = []
        endpoint = "https://api.femboy.pics/v2/femboy"
        
        try:
            for _ in range(count):
                params = {
                    "type": "nsfw" if nsfw else "sfw"
                }
                
                async with self.session.get(endpoint, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        # Check if image has the requested tag (if provided)
                        if tag:
                            image_data = data
                            tags = image_data.get('tags', [])
                            url = image_data.get('image', '')
                            
                            # Simple tag filtering based on tags list or URL
                            tag_lower = tag.lower()
                            tags_lower = [t.lower() for t in tags]
                            url_lower = url.lower()
                            
                            if tag_lower in tags_lower or tag_lower in url_lower:
                                images.append({
                                    'url': url,
                                    'tags': tags,
                                    'source': image_data.get('source', 'Unknown')
                                })
                            else:
                                # If tag doesn't match, still add it but we'll note it wasn't filtered
                                images.append({
                                    'url': url,
                                    'tags': tags,
                                    'source': image_data.get('source', 'Unknown'),
                                    'tag_filtered': False
                                })
                        else:
                            images.append({
                                'url': data.get('image', ''),
                                'tags': data.get('tags', []),
                                'source': data.get('source', 'Unknown')
                            })
                    else:
                        print(f"API Error: {resp.status}")
                        
        except asyncio.TimeoutError:
            print("API request timeout")
        except Exception as e:
            print(f"Error fetching images: {e}")

        return images

    @app_commands.command(name="femboy-sfw", description="Send SFW femboy images")
    @app_commands.describe(
        ilosc="Number of images (1-5)",
        tag="Optional tag/theme to filter (e.g., 'cosplay', 'maid', 'catgirl')"
    )
    async def femboy_sfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """
        Send SFW femboy images
        """
        # Validate ilosc parameter
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message(
                "❌ Liczba zdjęć musi być od 1 do 5!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            # Fetch images
            images = await self.fetch_femboy_images(nsfw=False, count=ilosc, tag=tag)
            
            if not images or not any(img['url'] for img in images):
                await interaction.followup.send(
                    "❌ Nie znaleziono zdjęć pasujących do Twojego zapytania. Spróbuj ponownie!"
                )
                return

            # Send images as embeds
            for idx, image in enumerate(images, 1):
                if not image['url']:
                    continue
                    
                embed = discord.Embed(
                    title=f"Femboy {idx}/{len(images)}",
                    color=COLOR_SFW
                )
                embed.set_image(url=image['url'])
                
                if image.get('tags'):
                    tags_str = ", ".join(image['tags'][:5])  # Show first 5 tags
                    embed.add_field(name="🏷️ Tagi", value=tags_str, inline=False)
                
                embed.set_footer(text=f"Źródło: {image.get('source', 'api.femboy.pics')}")
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            print(f"Error in femboy_sfw: {e}")
            await interaction.followup.send(
                f"❌ Błąd podczas pobierania zdjęć: {str(e)}"
            )

    @app_commands.command(name="femboy-nsfw", description="Send NSFW femboy images (18+ only)")
    @app_commands.describe(
        ilosc="Number of images (1-5)",
        tag="Optional tag/theme to filter (e.g., 'cosplay', 'maid')"
    )
    async def femboy_nsfw(self, interaction: discord.Interaction, ilosc: int = 1, tag: Optional[str] = None):
        """
        Send NSFW femboy images - only works in NSFW channels
        """
        # Check if channel is NSFW
        if not interaction.channel.is_nsfw():
            await interaction.response.send_message(
                "❌ Ta komenda dostępna jest tylko na kanałach z włączonym NSFW!\n"
                "🔞 Użyj jej na kanale oznaczonym jako NSFW.",
                ephemeral=True
            )
            return

        # Validate ilosc parameter
        if ilosc < 1 or ilosc > 5:
            await interaction.response.send_message(
                "❌ Liczba zdjęć musi być od 1 do 5!",
                ephemeral=True
            )
            return

        await interaction.response.defer()
        
        try:
            # Fetch NSFW images
            images = await self.fetch_femboy_images(nsfw=True, count=ilosc, tag=tag)
            
            if not images or not any(img['url'] for img in images):
                await interaction.followup.send(
                    "❌ Nie znaleziono zdjęć pasujących do Twojego zapytania. Spróbuj ponownie!"
                )
                return

            # Send images as embeds
            for idx, image in enumerate(images, 1):
                if not image['url']:
                    continue
                    
                embed = discord.Embed(
                    title=f"🔞 Femboy NSFW {idx}/{len(images)}",
                    color=COLOR_NSFW
                )
                embed.set_image(url=image['url'])
                
                if image.get('tags'):
                    tags_str = ", ".join(image['tags'][:5])  # Show first 5 tags
                    embed.add_field(name="🏷️ Tagi", value=tags_str, inline=False)
                
                embed.set_footer(text=f"Źródło: {image.get('source', 'api.femboy.pics')} | Tylko dla dorosłych")
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            print(f"Error in femboy_nsfw: {e}")
            await interaction.followup.send(
                f"❌ Błąd podczas pobierania zdjęć: {str(e)}"
            )


@bot.event
async def on_ready():
    print(f"✅ Bot zalogowany jako {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synchronizacja {len(synced)} komend slash")
    except Exception as e:
        print(f"❌ Błąd synchronizacji komend: {e}")


async def main():
    async with bot:
        # Add cog
        await bot.add_cog(FemboyBot(bot))
        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
