# OmniVerse

Pokétwo-style Discord bot with automatic spawns, premium perks, official features, and a public API.

## Deploy

1. Set env vars:
   - DISCORD_TOKEN
   - GUILD_ID (optional for instant slash sync)
   - OFFICIAL_SERVER_ID
   - PREMIUM_SERVER_IDS (comma-separated)
   - PREMIUM_USER_IDS (comma-separated)
   - KEEP_ALIVE (true/false)

2. Bot service:
   - Build: `pip install -r requirements.txt`
   - Start: `python -m src.app`

3. API service:
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn api.main:app --host 0.0.0.0 --port 8080`

## Invite

Scopes: `bot`, `applications.commands`  
Permissions: `268823622`

`https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=268823622&scope=bot%20applications.commands`

## Use

- Chat in a text channel → spawns appear.
- Type the full name to capture.
- `/help`, `/profile`, `/leaderboard`, `/balance`, `/daily`, `/incense`, `/set_series`, `/official_status`.

## API

- `GET /characters?series=Naruto&rarity=Epic`
- `GET /images/Goku`
- `GET /stats/server/{guild_id}`
