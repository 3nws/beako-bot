import discord
import os
import requests
import asyncio

from discord.ui import View, Select
from discord.ext import commands
from dotenv import load_dotenv
from cogs.classes.Player import Player

load_dotenv()


class Osu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
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
        player = Player()
        player.userid = r['user_id']
        player.username = r['username']
        player.lvl = r['level'].split('.')[0]
        player.progress = r['level'].split('.')[1][:2]+'%'
        player.global_rank = r['pp_rank']
        player.country_rank = r['pp_country_rank']
        player.country = r['country']
        player.pp = r['pp_raw'].split('.')[0]
        player.acc = r['accuracy'][:5]
        player.p_count = r['playcount']
        player.p_time = str(int(r['total_seconds_played']) // 60 // 60)
        player.ssh = r['count_rank_ssh']
        player.sh = r['count_rank_sh']
        player.ss = r['count_rank_ss']
        player.s = r['count_rank_s']
        player.a = r['count_rank_a']
        
        player.desc = f"Rank: #{player.global_rank} (#{player.country_rank} {player.country})\n\n"
        player.desc += f"{player.pp} pp, {player.acc}%, {player.p_count} plays ({player.p_time})\n\n"
        player.desc += f"SSH: {player.ssh}, SH: {player.sh}, SS: {player.ss}, S: {player.s}, A: {player.a}"
        
        player.avatar_url = self.base_image_url+player.userid
        return player

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
        
    @commands.command(aliases=['u', 'user'])
    async def osu(self, ctx, player_name=None):
        mode = "0"
        if player_name is None:
            return await ctx.send("Who, in fact?!")
        player = await self.get_user(player_name, mode)
        game_mode = self.game_modes[mode]
        embed = discord.Embed(
            colour=discord.Colour.random(),
            title=f"**{player.username} Lvl. {player.lvl} ({player.progress}) {game_mode}**",
            url=f"{self.base_profile_url}{player.userid}",
            description=player.desc,
        )
        embed.set_thumbnail(url=player.avatar_url)
        select = Select(options=self.game_mode_options,
                        placeholder="Select a game mode.")
        async def select_callback(i):
            mode = (i.data['values'])[0]
            player = await self.get_user(player_name, mode)
            game_mode = self.game_modes[mode]
            new_embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"**{player.username} Lvl. {player.lvl} ({player.progress}) {game_mode}**",
                url=f"{self.base_profile_url}{player.userid}",
                description=player.desc,
            )
            new_embed.set_thumbnail(url=player.avatar_url)
            await i.response.edit_message(embed=new_embed)
        
        select.callback = select_callback
        view = View().add_item(select)
        msg = await ctx.send(embed=embed, view=view)
        
    @commands.command(aliases=['rc', 'rs'])
    async def recent(self, ctx, player_name=None):
        mode = "0"
        if player_name is None:
            return await ctx.send("Who, in fact?!")
        scores = await self.get_user_recent(player_name, mode, 5)
        player = await self.get_user(player_name, mode)
        game_mode = self.game_modes[mode]
        stripped_game_mode = self.stripped_game_modes[mode]
        
        desc = ""
        for score in scores:
            map_info = score['beatmap']
            set_id = map_info['beatmapset_id']
            bm_id = map_info['beatmap_id']
            points = score['score']
            m_combo = score['maxcombo']
            c_50 = score['count50']
            c_100 = score['count100']
            c_300 = score['count300']
            c_miss = score['countmiss']
            mods = score['enabled_mods']
            date = score['date']
            rank = score['rank']
            link = f"{self.base_beatmap_set_url}{set_id}#{stripped_game_mode}/{bm_id}"
            desc += f"[{map_info['title']}]({link})\n\
                                {points}, {c_300}/{c_100}/{c_50}/{c_miss} :redTick:, {m_combo}x {rank}\n\
                                {mods}\n\
                                {date}\n\
                                \n"
        
        embed = discord.Embed(
            colour=discord.Colour.random(),
            title=f"**{player.username} Lvl. {player.lvl} ({player.progress}) {game_mode}**",
            url=f"{self.base_profile_url}{player.userid}",
            description=desc,
        )
        embed.set_thumbnail(url=player.avatar_url)
        
        select = Select(options=self.game_mode_options,
                        placeholder="Select a game mode.")

        async def select_callback(i):
            mode = (i.data['values'])[0]
            scores = await self.get_user_recent(player_name, mode, 5)
            player = await self.get_user(player_name, mode)
            game_mode = self.game_modes[mode]
            new_desc = ""
            for score in scores:
                map_info = score['beatmap']
                set_id = map_info['beatmapset_id']
                bm_id = map_info['beatmap_id']
                points = score['score']
                m_combo = score['maxcombo']
                c_50 = score['count50']
                c_100 = score['count100']
                c_300 = score['count300']
                c_miss = score['countmiss']
                mods = score['enabled_mods']
                date = score['date']
                rank = score['rank']
                link = f"{self.base_beatmap_set_url}{set_id}#{stripped_game_mode}/{bm_id}"
                new_desc += f"[{map_info['title']}]({link})\n\
                                {points}, {c_300}/{c_100}/{c_50}/{c_miss} :redTick:, {m_combo}x {rank}\n\
                                {mods}\n\
                                {date}\n\
                                \n"
            new_embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"**{player.username} Lvl. {player.lvl} ({player.progress}) {game_mode}**",
                url=f"{self.base_profile_url}{player.userid}",
                description=new_desc,
            )
            new_embed.set_thumbnail(url=player.avatar_url)
            await i.response.edit_message(embed=new_embed)

        select.callback = select_callback
        view = View().add_item(select)
        msg = await ctx.send(embed=embed, view=view)
        
    @commands.command(aliases=['top', 'best'])
    async def osutop(self, ctx, player_name=None):
        mode = "0"
        if player_name is None:
            return await ctx.send("Who, in fact?!")
        player = await self.get_user(player_name, mode)
        best_scores = await self.get_best(player_name, mode, 5)
        game_mode = self.game_modes[mode]
        stripped_game_mode = self.stripped_game_modes[mode]
        desc = ""
        for score in best_scores:
            map_info = score['beatmap']
            set_id = map_info['beatmapset_id']
            bm_id = map_info['beatmap_id']
            points = score['score']
            m_combo = score['maxcombo']
            c_50 = score['count50']
            c_100 = score['count100']
            c_300 = score['count300']
            c_miss = score['countmiss']
            mods = score['enabled_mods']
            date = score['date']
            rank = score['rank']
            pp = score['pp'].split('.')[0]
            link = f"{self.base_beatmap_set_url}{set_id}#{stripped_game_mode}/{bm_id}"
            desc += f"[{map_info['title']}]({link})\n\
                        {points}, {c_300}/{c_100}/{c_50}/{c_miss} :redTick:, {m_combo}x {rank}\n\
                        {mods}, {pp} PP\n\
                        {date}\n\
                        \n"
        embed = discord.Embed(
            colour=discord.Colour.random(),
            title=f"**{player.username} Lvl. {player.lvl} ({player.progress}) {game_mode}**",
            url=f"{self.base_profile_url}{player.userid}",
            description=desc,
        )
        embed.set_thumbnail(url=player.avatar_url)
        
        select = Select(options=self.game_mode_options,
                        placeholder="Select a game mode.")

        async def select_callback(i):
            mode = (i.data['values'])[0]
            player = await self.get_user(player_name, mode)
            game_mode = self.game_modes[mode]
            new_desc = ""
            for score in best_scores:
                map_info = score['beatmap']
                set_id = map_info['beatmapset_id']
                bm_id = map_info['beatmap_id']
                points = score['score']
                m_combo = score['maxcombo']
                c_50 = score['count50']
                c_100 = score['count100']
                c_300 = score['count300']
                c_miss = score['countmiss']
                mods = score['enabled_mods']
                date = score['date']
                rank = score['rank']
                pp = score['pp'].split('.')[0]
                link = f"{self.base_beatmap_set_url}{set_id}#{stripped_game_mode}/{bm_id}"
                new_desc += f"[{map_info['title']}]({link})\n\
                                {points}, {c_300}/{c_100}/{c_50}/{c_miss} :redTick:, {m_combo}x {rank}\n\
                                {mods}, {pp} PP\n\
                                {date}\n\
                                \n"
            new_embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"**{player.username} Lvl. {player.lvl} ({player.progress}) {game_mode}**",
                url=f"{self.base_profile_url}{player.userid}",
                description=new_desc,
            )
            new_embed.set_thumbnail(url=player.avatar_url)
            await i.response.edit_message(embed=new_embed)

        select.callback = select_callback
        view = View().add_item(select)
        msg = await ctx.send(embed=embed, view=view)
        
        

async def setup(bot):
    await bot.add_cog(Osu(bot))
