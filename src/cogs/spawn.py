import time, random, json
from pathlib import Path
import discord
from discord.ext import commands
from src.storage import db

COOLDOWN = 90                     # seconds between spawns per channel
BASE_CHANCE = 0.08                # per eligible message
INCENSE_MULT = 2.0                # chance multiplier
PREMIUM_SERVER_MULT = 1.3         # premium servers boost baseline
OFFICIAL_SERVER_MULT = 1.25       # slight boost for official

RARITY_REWARD = {"Common": 5, "Rare": 10, "Epic": 15, "Legendary": 25}

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "characters.json"

def norm(s): return ''.join(c.lower() for c in s if c.isalnum())

def levenshtein(a: str, b: str) -> int:
    # lightweight edit distance for premium leniency
    if a == b: return 0
    if not a: return len(b)
    if not b: return len(a)
    dp = range(len(b) + 1)
    for i, ca in enumerate(a, 1):
        ndp = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            ndp.append(min(dp[j] + 1, ndp[j - 1] + 1, dp[j - 1] + cost))
        dp = ndp
    return dp[-1]

class Spawn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.state = {}            # channel_id -> {last, active, guess_rate}
        self.series_filter = {}    # guild_id -> set(series)
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            self.pool = json.load(f)
        db.init()

    def incense_active(self, guild_id: int, channel_id: int) -> bool:
        row = db.exec("SELECT expires_ts FROM incense WHERE guild_id=? AND channel_id=?", (guild_id, channel_id)).fetchone()
        return bool(row and row[0] > int(time.time()))

    def pool_for_guild(self, gid: int):
        s = self.series_filter.get(gid)
        return [c for c in self.pool if (not s or c["series"] in s)]

    async def maybe_spawn(self, message: discord.Message):
        if not isinstance(message.channel, discord.TextChannel) or message.author.bot:
            return
        gid, cid = message.guild.id, message.channel.id
        st = self.state.get(cid, {"last": 0, "active": None, "guess_rate": {}})
        now = time.time()
        if now - st["last"] < COOLDOWN:
            return

        mult = 1.0
        if gid in self.bot.premium_server_ids:
            mult *= PREMIUM_SERVER_MULT
        if self.bot.official_server_id and gid == self.bot.official_server_id:
            mult *= OFFICIAL_SERVER_MULT
        if self.incense_active(gid, cid):
            mult *= INCENSE_MULT

        chance = BASE_CHANCE * mult
        if random.random() > chance:
            return

        pool = self.pool_for_guild(gid)
        if not pool:
            return
        char = random.choice(pool)

        emb = discord.Embed(
            title="A wild character appears!",
            description="Type the full name to capture.",
            color=0x2ecc71
        )
        emb.set_image(url=char["image"])
        emb.set_footer(text=f"Series: {char['series']} • Rarity: {char['rarity']}")
        msg = await message.channel.send(embed=emb)

        st["active"] = {
            "msg_id": msg.id,
            "answer_norm": norm(char["name"]),
            "answer_full": char["name"],
            "series": char["series"],
            "rarity": char["rarity"],
            "ts": int(now)
        }
        st["last"] = now
        self.state[cid] = st

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not isinstance(message.channel, discord.TextChannel):
            return

        await self.maybe_spawn(message)

        cid = message.channel.id
        st = self.state.get(cid)
        if not st or not st.get("active"):
            return

        # per-user guess rate limit (anti-spam): 1 guess per 2 seconds
        gr = st["guess_rate"]
        uid = message.author.id
        now = time.time()
        last_guess = gr.get(uid, 0)
        if now - last_guess < 2.0:
            return
        gr[uid] = now

        guess = norm(message.content)
        if not guess:
            return

        target = st["active"]["answer_norm"]
        correct = guess == target

        # Premium leniency: small edit distance allowance for names >= 6 chars
        if not correct and uid in self.bot.premium_user_ids and len(target) >= 6:
            correct = levenshtein(guess, target) <= 1

        if correct:
            rarity = st["active"]["rarity"]
            reward = RARITY_REWARD.get(rarity, 8)
            if uid in self.bot.premium_user_ids:
                reward = int(reward * 1.5)

            emb = discord.Embed(
                title="Captured!",
                description=f"{message.author.mention} guessed correctly: {st['active']['answer_full']}",
                color=0x3498db
            )
            emb.add_field(name="Reward", value=f"+{reward} shards • Rarity: {rarity}", inline=False)
            await message.channel.send(embed=emb)

            db.add_shards(uid, reward)
            db.inc_captures(uid, 1)
            db.record_capture(uid, message.guild.id, st["active"]["answer_full"], st["active"]["series"], rarity)
            st["active"] = None

    @commands.hybrid_command(name="incense", description="Boost spawns in this channel.")
    @commands.has_permissions(manage_messages=True)
    async def incense(self, ctx: commands.Context, minutes: int = 15):
        max_minutes = 45 if ctx.guild.id in self.bot.premium_server_ids else 20
        if self.bot.official_server_id and ctx.guild.id == self.bot.official_server_id:
            max_minutes = 120
        minutes = max(1, min(minutes, max_minutes))
        expires = int(time.time()) + minutes * 60
        db.exec("INSERT OR REPLACE INTO incense (guild_id, channel_id, expires_ts) VALUES (?, ?, ?)",
                (ctx.guild.id, ctx.channel.id, expires))
        await ctx.reply(f"Incense lit for {minutes} minutes. Spawns boosted.")

    @commands.hybrid_command(name="set_series", description="Restrict spawn pool to series (comma-separated).")
    @commands.has_permissions(administrator=True)
    async def set_series(self, ctx: commands.Context, series_csv: str):
        series = {s.strip() for s in series_csv.split(",") if s.strip()}
        self.series_filter[ctx.guild.id] = series
        await ctx.reply(f"Spawns now restricted to: {', '.join(series)}")

async def setup(bot): await bot.add_cog(Spawn(bot))
