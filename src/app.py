import os
import discord
from discord.ext import commands

USE_KEEP_ALIVE = os.getenv("KEEP_ALIVE", "false").lower() == "true"
if USE_KEEP_ALIVE:
    from src.keep_alive import keep_alive
    keep_alive()

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

GUILD_ID = os.getenv("GUILD_ID")
OFFICIAL_SERVER_ID = os.getenv("OFFICIAL_SERVER_ID")
PREMIUM_SERVER_IDS = {int(s) for s in os.getenv("PREMIUM_SERVER_IDS", "").split(",") if s.strip().isdigit()}
PREMIUM_USER_IDS = {int(s) for s in os.getenv("PREMIUM_USER_IDS", "").split(",") if s.strip().isdigit()}

@bot.event
async def setup_hook():
    bot.official_server_id = int(OFFICIAL_SERVER_ID) if OFFICIAL_SERVER_ID and OFFICIAL_SERVER_ID.isdigit() else None
    bot.premium_server_ids = PREMIUM_SERVER_IDS
    bot.premium_user_ids = PREMIUM_USER_IDS

    for ext in [
        "src.cogs.help",
        "src.cogs.spawn",
        "src.cogs.economy",
        "src.cogs.profile",
        "src.cogs.leaderboard",
        "src.cogs.admin",
    ]:
        await bot.load_extension(ext)

    try:
        if GUILD_ID and GUILD_ID.isdigit():
            await bot.tree.sync(guild=discord.Object(id=int(GUILD_ID)))
            print(f"Synced commands to guild {GUILD_ID} (instant).")
        else:
            await bot.tree.sync()
            print("Synced commands globally (may take up to 1 hour).")
    except Exception as e:
        print("Slash sync error:", e)

@bot.event
async def on_ready():
    print(f"Ready as {bot.user} ({bot.user.id})")

def main():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is not set.")
    bot.run(token)

if __name__ == "__main__":
    main()
