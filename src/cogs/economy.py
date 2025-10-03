import time
import discord
from discord.ext import commands
from src.storage import db

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        db.init()
        self.daily_cache = {}  # user_id -> last_claim_ts

    @commands.hybrid_command(name="balance", description="Check your shard balance.")
    async def balance(self, ctx: commands.Context, user: discord.User = None):
        user = user or ctx.author
        shards, captures, badges = db.get_user(user.id)
        await ctx.reply(f"{user.mention} — Shards: {shards} • Captures: {captures}")

    @commands.hybrid_command(name="daily", description="Claim your daily shards.")
    async def daily(self, ctx: commands.Context):
        uid = ctx.author.id
        now = int(time.time())
        last = self.daily_cache.get(uid, 0)
        cooldown = 20 * 60 * 60
        if now - last < cooldown:
            remaining = cooldown - (now - last)
            await ctx.reply(f"Daily already claimed. Try again in {remaining // 3600}h {(remaining % 3600) // 60}m.")
            return
        shards, captures, badges = db.get_user(uid)
        base = 50
        if uid in self.bot.premium_user_ids:
            base = int(base * 1.5)
        db.exec("UPDATE users SET shards=? WHERE user_id=?", (shards + base, uid))
        self.daily_cache[uid] = now
        await ctx.reply(f"Daily claimed: +{base} shards!")

async def setup(bot): await bot.add_cog(Economy(bot))
