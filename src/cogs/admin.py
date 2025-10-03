import discord
from discord.ext import commands

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_owner(self, uid: int) -> bool:
        app = self.bot.application
        return bool(app and app.owner and app.owner.id == uid)

    @commands.hybrid_command(name="official_status", description="Show official and premium status.")
    async def official_status(self, ctx: commands.Context):
        gid = ctx.guild.id
        is_official = (self.bot.official_server_id and gid == self.bot.official_server_id)
        is_premium = gid in self.bot.premium_server_ids
        await ctx.reply(f"Official: {bool(is_official)} • Premium server: {bool(is_premium)}")

    @commands.hybrid_command(name="premium_add_server", description="Add this server to premium (owner only).")
    async def premium_add_server(self, ctx: commands.Context):
        if not self.is_owner(ctx.author.id):
            await ctx.reply("Owner only.")
            return
        self.bot.premium_server_ids.add(ctx.guild.id)
        await ctx.reply("Server added to premium.")

    @commands.hybrid_command(name="premium_remove_server", description="Remove this server from premium (owner only).")
    async def premium_remove_server(self, ctx: commands.Context):
        if not self.is_owner(ctx.author.id):
            await ctx.reply("Owner only.")
            return
        self.bot.premium_server_ids.discard(ctx.guild.id)
        await ctx.reply("Server removed from premium.")

    @commands.hybrid_command(name="premium_add_user", description="Add a user to premium (owner only).")
    async def premium_add_user(self, ctx: commands.Context, user: discord.User):
        if not self.is_owner(ctx.author.id):
            await ctx.reply("Owner only.")
            return
        self.bot.premium_user_ids.add(user.id)
        await ctx.reply(f"{user.mention} added to premium.")

    @commands.hybrid_command(name="premium_remove_user", description="Remove a user from premium (owner only).")
    async def premium_remove_user(self, ctx: commands.Context, user: discord.User):
        if not self.is_owner(ctx.author.id):
            await ctx.reply("Owner only.")
            return
        self.bot.premium_user_ids.discard(user.id)
        await ctx.reply(f"{user.mention} removed from premium.")

async def setup(bot): await bot.add_cog(Admin(bot))
