import discord
from discord.ext import commands
from src.storage import db

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        db.init()

    @commands.hybrid_command(name="profile", description="View your collection and stats.", with_app_command=True)
    async def profile(self, ctx: commands.Context, user: discord.User = None):
        user = user or ctx.author
        shards, captures, badges = db.get_user(user.id)
        premium_badge = "✨" if user.id in self.bot.premium_user_ids else ""
        emb = discord.Embed(
            title=f"{premium_badge} {user.name} — Profile",
            description=f"Shards: {shards} • Captures: {captures}",
            color=0x5865F2
        )
        emb.set_thumbnail(url=user.display_avatar.url)
        await ctx.reply(embed=emb)

async def setup(bot): await bot.add_cog(Profile(bot))
