import discord
import os
import requests
import asyncio

from discord.ui import View, Select
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()


class Osu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.API_KEY = os.getenv("OSU_API_KEY")
        self.base_url = "https://osu.ppy.sh/api/"
        self.base_image_url = "http://s.ppy.sh/a/"
        self.key_query = f"?k={self.API_KEY}"
        self.base_profile_url = "https://osu.ppy.sh/users/"
        self.game_modes = {
            "0": "osu!",
            "1": "osu!taiko",
            "2": "osu!catch",
            "3": "osu!mania",
        }

    @commands.command(aliases=['u', 'user'])
    async def osu(self, ctx, player=None):
        mode = "0"
        if player is None:
            return await ctx.send("Who, in fact?!")
        url = f"{self.base_url}get_user{self.key_query}&u={player}&m={mode}"
        s = requests.session()
        r = s.get(url).json()[0]
        username = r['username']
        lvl = r['level'].split('.')[0]
        progress = r['level'].split('.')[1][:2]+'%'
        global_rank = r['pp_rank']
        country_rank = r['pp_country_rank']
        country = r['country']
        pp = r['pp_raw'].split('.')[0]
        acc = r['accuracy'][:5]
        p_count = r['playcount']
        p_time = str(int(r['total_seconds_played']) // 60 // 60)
        ssh = r['count_rank_ssh']
        sh = r['count_rank_sh']
        ss = r['count_rank_ss']
        s = r['count_rank_s']
        a = r['count_rank_a']
        game_mode = self.game_modes[mode]

        desc = f"Rank: #{global_rank} (#{country_rank} {country})\n\n"
        desc += f"{pp} pp, {acc}%, {p_count} plays ({p_time})\n\n"
        desc += f"SSH: {ssh}, SH: {sh}, SS: {ss}, S: {s}, A: {a}"
        
        embed = discord.Embed(
            colour=discord.Colour.random(),
            title=f"**{username} Lvl. {lvl} ({progress}) {game_mode}**",
            url=f"{self.base_profile_url}{r['user_id']}",
            description=desc,
        )
        avatar_url = self.base_image_url+r['user_id']
        embed.set_thumbnail(url=avatar_url)
        options = [
                discord.SelectOption(value=0, label="osu!"),
                discord.SelectOption(value=1, label="osu!taiko"),
                discord.SelectOption(value=2, label="osu!catch"),
                discord.SelectOption(value=3, label="osu!mania"),
        ]
        select = Select(options=options, placeholder="Select a game mode.")
        async def select_callback(i):
            mode = (i.data['values'])[0]
            new_url = self.base_url+"get_user" + \
                self.key_query+f"&u={player}&m="+mode
            r = requests.get(new_url).json()[0]
            lvl = r['level'].split('.')[0]
            progress = r['level'].split('.')[1][:2]+'%'
            global_rank = r['pp_rank']
            country_rank = r['pp_country_rank']
            country = r['country']
            pp = r['pp_raw'].split('.')[0]
            acc = r['accuracy'][:5]
            p_count = r['playcount']
            p_time = str(int(r['total_seconds_played']) // 60 // 60)
            ssh = r['count_rank_ssh']
            sh = r['count_rank_sh']
            ss = r['count_rank_ss']
            s = r['count_rank_s']
            a = r['count_rank_a']
            game_mode = self.game_modes[mode]

            desc = f"Rank: #{global_rank} (#{country_rank} {country})\n\n"
            desc += f"{pp} pp, {acc}%, {p_count} plays ({p_time})\n\n"
            desc += f"SSH: {ssh}, SH: {sh}, SS: {ss}, S: {s}, A: {a}"
            new_embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"**{username} Lvl. {lvl} ({progress}) {game_mode}**",
                url=f"{self.base_profile_url}{r['user_id']}",
                description=desc,
            )
            new_embed.set_thumbnail(url=avatar_url)
            await i.response.edit_message(embed=new_embed)
        
        select.callback = select_callback
        view = View().add_item(select)
        msg = await ctx.send(embed=embed, view=view)

    @osu.error
    async def osu_error(self, error, ctx):
        print(error.cog)


async def setup(bot):
    await bot.add_cog(Osu(bot))
