import discord
import os
import requests
import asyncio

from discord.ui import View, Select
from discord.ext import commands
from cogs.classes.OsuAPI import OsuAPI
from OsuMods import num_to_mod



class Osu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.osu = OsuAPI()
        
    @commands.command(aliases=['u', 'user'])
    async def osu(self, ctx, player_name=None):
        mode = "0"
        if player_name is None:
            return await ctx.send("Who, in fact?!\nUse `r.help osu` for more information, I suppose!")
        msg = await ctx.send("Loading, I suppose")
        try:
            player = await self.osu.get_user(player_name, mode)
            game_mode = self.osu.game_modes[mode]
            embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                url=f"{self.osu.base_profile_url}{player['user_id']}",
                description=player['desc'],
            )
            embed.set_thumbnail(url=player['avatar_url'])
            select = Select(options=self.osu.game_mode_options,
                            placeholder="Select a game mode.")
            async def select_callback(i):
                mode = (i.data['values'])[0]
                player = await self.osu.get_user(player_name, mode)
                game_mode = self.osu.game_modes[mode]
                new_embed = discord.Embed(
                    colour=discord.Colour.random(),
                    title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                    url=f"{self.osu.base_profile_url}{player['user_id']}",
                    description=player['desc'],
                )
                new_embed.set_thumbnail(url=player['avatar_url'])
                await i.response.edit_message(embed=new_embed)
            
            select.callback = select_callback
            view = View().add_item(select)
            msg = await msg.edit(content='', embed=embed, view=view)
        except Exception as e:
            print(e)
            await msg.edit("Something went wrong, in fact!")
        
    @commands.command(aliases=['rc', 'rs'])
    async def recent(self, ctx, player_name=None):
        mode = "0"
        if player_name is None:
            return await ctx.send("Who, in fact?!\nUse `r.help recent` for more information, I suppose!")
        msg = await ctx.send("Loading, I suppose")
        try:
            scores = await self.osu.get_user_recent(player_name, mode, 5)
            player = await self.osu.get_user(player_name, mode)
            game_mode = self.osu.game_modes[mode]
            stripped_game_mode = self.osu.stripped_game_modes[mode]
            
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
                mods = num_to_mod(int(mods))
                mods_str = ""
                for mod in mods:
                    mods_str += mod
                mods_str = mods_str if len(mods) > 0 else "NO MOD"
                date = score['date']
                rank = score['rank']
                link = f"{self.osu.base_beatmap_set_url}{set_id}#{stripped_game_mode}/{bm_id}"
                desc += f"[{map_info['title']}]({link})\n\
                                    {points}, {c_300}/{c_100}/{c_50}/{c_miss} :redTick:, {m_combo}x {rank}\n\
                                    {mods_str}\n\
                                    {date}\n\
                                    \n"
            
            embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                url=f"{self.osu.base_profile_url}{player['user_id']}",
                description=desc,
            )
            embed.set_thumbnail(url=player['avatar_url'])
            
            select = Select(options=self.osu.game_mode_options,
                            placeholder="Select a game mode.")

            async def select_callback(i):
                mode = (i.data['values'])[0]
                scores = await self.osu.get_user_recent(player_name, mode, 5)
                player = await self.osu.get_user(player_name, mode)
                game_mode = self.osu.game_modes[mode]
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
                    mods = num_to_mod(int(mods))
                    mods_str = ""
                    for mod in mods:
                        mods_str += mod
                    mods_str = mods_str if len(mods) > 0 else "NO MOD"
                    date = score['date']
                    rank = score['rank']
                    link = f"{self.osu.base_beatmap_set_url}{set_id}#{stripped_game_mode}/{bm_id}"
                    new_desc += f"[{map_info['title']}]({link})\n\
                                    {points}, {c_300}/{c_100}/{c_50}/{c_miss} :redTick:, {m_combo}x {rank}\n\
                                    {mods_str}\n\
                                    {date}\n\
                                    \n"
                new_embed = discord.Embed(
                    colour=discord.Colour.random(),
                    title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                    url=f"{self.osu.base_profile_url}{player['user_id']}",
                    description=new_desc,
                )
                new_embed.set_thumbnail(url=player['avatar_url'])
                await i.response.edit_message(embed=new_embed)

            select.callback = select_callback
            view = View().add_item(select)
            msg = await msg.edit(content='', embed=embed, view=view)
        except Exception as e:
            print(e)
            await msg.edit("Something went wrong, in fact!")
        
    @commands.command(aliases=['top', 'best'])
    async def osutop(self, ctx, player_name=None):
        mode = "0"
        if player_name is None:
            return await ctx.send("Who, in fact?!\nUse `r.help osutop` for more information, I suppose!")
        msg = await ctx.send("Loading, I suppose")
        try:
            player = await self.osu.get_user(player_name, mode)
            best_scores = await self.osu.get_best(player_name, mode, 5)
            game_mode = self.osu.game_modes[mode]
            stripped_game_mode = self.osu.stripped_game_modes[mode]
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
                mods = num_to_mod(int(mods))
                mods_str = ""
                for mod in mods:
                    mods_str += mod
                mods_str = mods_str if len(mods) > 0 else "NO MOD"
                date = score['date']
                rank = score['rank']
                pp = score['pp'].split('.')[0]
                link = f"{self.osu.base_beatmap_set_url}{set_id}#{stripped_game_mode}/{bm_id}"
                desc += f"[{map_info['title']}]({link})\n\
                            {points}, {c_300}/{c_100}/{c_50}/{c_miss} :redTick:, {m_combo}x {rank}\n\
                            {mods_str}, {pp} PP\n\
                            {date}\n\
                            \n"
            embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                url=f"{self.osu.base_profile_url}{player['user_id']}",
                description=desc,
            )
            embed.set_thumbnail(url=player['avatar_url'])
            
            select = Select(options=self.osu.game_mode_options,
                            placeholder="Select a game mode.")

            async def select_callback(i):
                mode = (i.data['values'])[0]
                player = await self.osu.get_user(player_name, mode)
                best_scores = await self.osu.get_best(player_name, mode, 5)
                game_mode = self.osu.game_modes[mode]
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
                    mods = num_to_mod(int(mods))
                    mods_str = ""
                    for mod in mods:
                        mods_str += mod
                    mods_str = mods_str if len(mods) > 0 else "NO MOD"
                    date = score['date']
                    rank = score['rank']
                    pp = score['pp'].split('.')[0]
                    link = f"{self.osu.base_beatmap_set_url}{set_id}#{stripped_game_mode}/{bm_id}"
                    new_desc += f"[{map_info['title']}]({link})\n\
                                    {points}, {c_300}/{c_100}/{c_50}/{c_miss} :redTick:, {m_combo}x {rank}\n\
                                    {mods_str}, {pp} PP\n\
                                    {date}\n\
                                    \n"
                new_embed = discord.Embed(
                    colour=discord.Colour.random(),
                    title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                    url=f"{self.osu.base_profile_url}{player['user_id']}",
                    description=new_desc,
                )
                new_embed.set_thumbnail(url=player['avatar_url'])
                await i.response.edit_message(embed=new_embed)

            select.callback = select_callback
            view = View().add_item(select)
            msg = await msg.edit(content='', embed=embed, view=view)
        except Exception as e:
            print(e)
            await msg.edit("Something went wrong, in fact!")
        
        

async def setup(bot):
    await bot.add_cog(Osu(bot))
