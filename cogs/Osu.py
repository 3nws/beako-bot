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
        self.game_modes = {
            "0": "osu!",
            "1": "osu!taiko",
            "2": "osu!catch",
            "3": "osu!mania",
        }
        
    async def get_user(self, username, mode):
        url = f"{self.base_url}get_user{self.key_query}&u={username}&m={mode}"
        s = requests.session()
        r = s.get(url).json()[0]
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
        options = [
                discord.SelectOption(value=0, label="osu!"),
                discord.SelectOption(value=1, label="osu!taiko"),
                discord.SelectOption(value=2, label="osu!catch"),
                discord.SelectOption(value=3, label="osu!mania"),
        ]
        select = Select(options=options, placeholder="Select a game mode.")
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
        
    # @commands.command(aliases=['rc', 'rs'])
    # async def recent(self, ctx, player=None):
    #     mode = "0"
    #     if player is None:
    #         return await ctx.send("Who, in fact?!")
    #     url = f"{self.base_url}get_user_recent{self.key_query}&u={player}&m={mode}&limit=5"



async def setup(bot):
    await bot.add_cog(Osu(bot))
