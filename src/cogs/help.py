import discord
from discord.ext import commands

USER_PREMIUM = [
    "Shard multiplier on captures",
    "Daily bonus boost",
    "Lenient name matching",
    "Cosmetic highlight on leaderboards"
]
SERVER_PREMIUM = [
    "Higher base spawn rate",
    "Longer incense and more slots",
    "Featured series rotations and events",
    "Custom server branding in embeds"
]

class PremiumView(discord.ui.View):
    def __init__(self): super().__init__(timeout=120)
    @discord.ui.button(label="User perks", style=discord.ButtonStyle.green, emoji="✨")
    async def user_btn(self, i, b): await i.response.send_message("• " + "\n• ".join(USER_PREMIUM), ephemeral=True)
    @discord.ui.button(label="Server perks", style=discord.ButtonStyle.blurple, emoji="🏰")
    async def server_btn(self, i, b): await i.response.send_message("• " + "\n• ".join(SERVER_PREMIUM), ephemeral=True)

class Help(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.hybrid_command(name="help", description="How to play OmniVerse")
    async def help(self, ctx: commands.Context):
        emb = discord.Embed(
            title="OmniVerse — How to play",
            description="Chat to trigger spawns. Type the character’s full name to capture.",
            color=0x5865F2
        )
        emb.add_field(
            name="Play",
            value="• Chat → spawn may appear\n• Type full name to capture\n• Incense boosts rate\n• Use /profile and /leaderboard",
            inline=False
        )
        emb.add_field(
            name="Controls",
            value="• `/incense [minutes]` (mods)\n• `/set_series Series1, Series2` (admin)\n• `/official_status`",
            inline=False
        )
        await ctx.send(embed=emb, view=PremiumView())

async def setup(bot): await bot.add_cog(Help(bot))
