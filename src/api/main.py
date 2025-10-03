from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path
import sqlite3, time

app = FastAPI(title="OmniVerse API", version="1.0.0")
DATA_PATH = Path(__file__).resolve().parent.parent / "src" / "data" / "characters.json"
DB_PATH = Path(__file__).resolve().parent.parent / "omniverse.db"

class Character(BaseModel):
    name: str
    series: str
    image: str
    rarity: str

def load_characters() -> List[Character]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [Character(**c) for c in raw]

@app.get("/characters", response_model=List[Character])
def characters(series: Optional[str] = Query(None), rarity: Optional[str] = Query(None)):
    data = load_characters()
    if series:
        data = [c for c in data if c.series.lower() == series.lower()]
    if rarity:
        data = [c for c in data if c.rarity.lower() == rarity.lower()]
    return data

@app.get("/images/{name}")
def image(name: str):
    for c in load_characters():
        if c.name.lower() == name.lower():
            return {"name": c.name, "image": c.image, "series": c.series, "rarity": c.rarity}
    return {"error": "not_found"}

@app.get("/stats/server/{guild_id}")
def server_stats(guild_id: int):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        captures_today = cur.execute("SELECT COUNT(*) FROM captures WHERE guild_id=? AND ts > ?", (guild_id, int(time.time()) - 86400)).fetchone()[0]
        top = cur.execute("SELECT user_id, COUNT(*) FROM captures WHERE guild_id=? GROUP BY user_id ORDER BY COUNT(*) DESC LIMIT 1", (guild_id,)).fetchone()
        top_out = {"user_id": top[0], "captures": top[1]} if top else None
    return {"guild_id": guild_id, "captures_today": captures_today, "top_collector": top_out, "updated": int(time.time())}
