import discord
from discord.ext import commands
from src.storage import db

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        db.init()

    @commands.hybrid_command(name="leaderboard", description="Top collectors or richest players.")
    async def leaderboard(self, ctx: commands.Context, type: str = "captures"):
        type = type.lower()
        if type not in {"captures", "shards"}:
            await ctx.reply("Type must be 'captures' or 'shards'.")
            return
        rows = db.fetchall(f"SELECT user_id, {type} FROM users ORDER BY {type} DESC LIMIT 10")
        lines = [f"{i}. <@{uid}> — {val}" for i, (uid, val) in enumerate(rows, 1)]
        emb = discord.Embed(title=f"Leaderboard — {type}", description="\n".join(lines) if lines else "No data yet.", color=0x2ecc71)
        await ctx.reply(embed=emb)

async def setup(bot): await bot.add_cog(Leaderboard(bot))
