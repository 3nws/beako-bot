import discord
import os
import requests
import asyncio

from discord.ui import View, Select
from discord.ext import commands
from dotenv import load_dotenv
from OsuMods import num_to_mod

load_dotenv()

class OsuAPI:
    def __init__(self):
        self.API_KEY = os.getenv("OSU_API_KEY")
        self.base_url = "https://osu.ppy.sh/api/"
        self.base_image_url = "http://s.ppy.sh/a/"
        self.key_query = f"?k={self.API_KEY}"
        self.base_profile_url = "https://osu.ppy.sh/users/"
        self.base_beatmap_set_url = "https://osu.ppy.sh/beatmapsets/"
        self.game_mode_options = [
            discord.SelectOption(value=0, label="osu!"),
            discord.SelectOption(value=1, label="osu!taiko"),
            discord.SelectOption(value=2, label="osu!catch"),
            discord.SelectOption(value=3, label="osu!mania"),
        ]
        self.game_modes = {
            "0": "osu!",
            "1": "osu!taiko",
            "2": "osu!catch",
            "3": "osu!mania",
        }
        self.stripped_game_modes = {
            "0": "osu",
            "1": "taiko",
            "2": "catch",
            "3": "mania",
        }

    async def get_user(self, username, mode):
        url = f"{self.base_url}get_user{self.key_query}&u={username}&m={mode}"
        r = requests.get(url).json()[0]
        r['progress'] = r['level'].split('.')[1][:2]+'%'
        r['level'] = r['level'].split('.')[0]
        r['pp'] = r['pp_raw'].split('.')[0]
        r['accuracy'] = r['accuracy'][:5]
        r['playtime'] = str(int(r['total_seconds_played']) // 60 // 60)

        r['desc'] = f"Rank: #{r['pp_rank']} (#{r['pp_country_rank']} {r['country']})\n\n"
        r['desc'] += f"{r['pp']} pp, {r['accuracy']}%, {r['playcount']} plays ({r['playtime']})\n\n"
        r['desc'] += f"SSH: {r['count_rank_ssh']}, SH: {r['count_rank_sh']}, SS: {r['count_rank_ss']}, S: {r['count_rank_s']}, A: {r['count_rank_a']}"

        r['avatar_url'] = self.base_image_url+r['user_id']
        return r
    
    async def get_beatmap(self, id):
        url = f"{self.base_url}get_beatmaps{self.key_query}&b={id}"
        r = requests.get(url).json()[0]
        return r

    async def get_user_recent(self, username, mode, limit):
        url = f"{self.base_url}get_user_recent{self.key_query}&u={username}&m={mode}&limit={limit}"
        r = requests.get(url).json()
        r = list(r)
        for score in r:
            bm_id = score['beatmap_id']
            score['beatmap'] = await self.get_beatmap(bm_id)
        return r

    async def get_best(self, username, mode, limit):
        url = f"{self.base_url}get_user_best{self.key_query}&u={username}&m={mode}&limit={limit}"
        r = requests.get(url).json()
        r = list(r)
        for score in r:
            bm_id = score['beatmap_id']
            score['beatmap'] = await self.get_beatmap(bm_id)
        return r
