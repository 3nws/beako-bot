import discord
import os
import json

from dotenv import load_dotenv      # type: ignore
from typing import List, Dict, Optional
from aiohttp import ClientSession

from Bot import Bot


load_dotenv()


class OsuAPI:

    __slots__ = (
        "bot",
        "base_url",
        "base_image_url",
        "key_query",
        "base_profile_url",
        "base_beatmap_set_url",
        "game_mode_options",
        "game_modes",
        "stripped_game_modes",
    )

    def __init__(self, bot: Bot):
        _API_KEY: Optional[str] = os.getenv("OSU_API_KEY")
        self.bot: Bot = bot
        self.base_url: str = "https://osu.ppy.sh/api/"
        self.base_image_url: str = "http://s.ppy.sh/a/"
        self.key_query: str = f"?k={_API_KEY}"
        self.base_profile_url: str = "https://osu.ppy.sh/users/"
        self.base_beatmap_set_url: str = "https://osu.ppy.sh/beatmapsets/"
        self.game_mode_options: List[discord.SelectOption] = [
            discord.SelectOption(value="0", label="osu!"),
            discord.SelectOption(value="1", label="osu!taiko"),
            discord.SelectOption(value="2", label="osu!catch"),
            discord.SelectOption(value="3", label="osu!mania"),
        ]
        self.game_modes: Dict[str, str] = {
            "0": "osu!",
            "1": "osu!taiko",
            "2": "osu!catch",
            "3": "osu!mania",
        }
        self.stripped_game_modes: Dict[str, str] = {
            "0": "osu",
            "1": "taiko",
            "2": "catch",
            "3": "mania",
        }

    async def get_user(self, username: str, mode: str) -> Optional[Dict[str, str]]:
        url = f"{self.base_url}get_user{self.key_query}&u={username}&m={mode}"
        session: ClientSession = self.bot.session  
        async with session.get(url) as r:
            if r.status == 200:
                response = await r.read()
                player = json.loads(response)[0]
            else:
                print("osu! down!")
                return
        player['progress'] = player['level'].split('.')[1][:2] + '%'
        player['level'] = player['level'].split('.')[0]
        player['pp'] = player['pp_raw'].split('.')[0]
        player['accuracy'] = player['accuracy'][:5]
        player['playtime'] = str(
            int(player['total_seconds_played']) // 60 // 60)

        player['desc'] = f"Rank: #{player['pp_rank']} (#{player['pp_country_rank']} {player['country']})\n\n"
        player[
            'desc'] += f"{player['pp']} pp, {player['accuracy']}%, {player['playcount']} plays ({player['playtime']})\n\n"
        player['desc'] += f"SSH: {player['count_rank_ssh']}, SH: {player['count_rank_sh']}, SS: {player['count_rank_ss']}, S: {player['count_rank_s']}, A: {player['count_rank_a']}"

        player['avatar_url'] = self.base_image_url + player['user_id']
        return player

    async def _get_beatmap(self, id: str):
        url = f"{self.base_url}get_beatmaps{self.key_query}&b={id}"
        session: ClientSession = self.bot.session  
        async with session.get(url) as r:
            if r.status == 200:
                response = await r.read()
                maps = json.loads(response)
            else:
                print("osu! down!")
                return
        return maps[0]

    async def get_user_recent(self, username: str, mode: str, limit: str):
        url = f"{self.base_url}get_user_recent{self.key_query}&u={username}&m={mode}&limit={limit}"
        session: ClientSession = self.bot.session  
        async with session.get(url) as r:
            if r.status == 200:
                response = await r.read()
                scores = list(json.loads(response))
            else:
                print("osu! down!")
                return
        for score in scores:
            bm_id = score['beatmap_id']
            score['beatmap'] = await self._get_beatmap(bm_id)
        return scores

    async def get_best(self, username: str, mode: str, limit: str):
        url = f"{self.base_url}get_user_best{self.key_query}&u={username}&m={mode}&limit={limit}"
        session: ClientSession = self.bot.session  
        async with session.get(url) as r:
            if r.status == 200:
                response = await r.read()
                scores = list(json.loads(response))
            else:
                print("osu! down!")
                return
        for score in scores:
            bm_id = score['beatmap_id']
            score['beatmap'] = await self._get_beatmap(bm_id)
        return scores
