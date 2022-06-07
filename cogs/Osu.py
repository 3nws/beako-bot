import discord

from discord.ui import View, Select
from discord.ext import commands
from discord import app_commands
from typing import Dict, Optional

from Bot import Bot
from OsuMods import num_to_mod
from classes.OsuAPI import OsuAPI


class Osu(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.osu: OsuAPI = OsuAPI(self.bot)

    group = app_commands.Group(name="osu", description="osu! command group...")


    @group.command(name="profile")
    @app_commands.describe(player_name="The player you want to get info on, in fact!")
    async def osu_profile(self, i: discord.Interaction, player_name: str):
        """Get this player's profile.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            player_name (str): the player name to look up

        Returns:
            None: None
        """
        await i.response.defer()
        mode = "0"
        if player_name is None:
            return await i.followup.send("Who, in fact?!\nUse `/help osu` for more information, I suppose!")
        try:
            player: Optional[Dict[str, str]] = await self.osu.get_user(player_name, mode)
            game_mode = self.osu.game_modes[mode]
            embed = discord.Embed()
            if player is not None:
                embed = discord.Embed(
                    colour=discord.Colour.random(),
                    title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                    url=f"{self.osu.base_profile_url}{player['user_id']}",
                    description=player['desc'],
                )
                embed.set_thumbnail(url=player['avatar_url'])
                
            select: Select[View] = Select(options=self.osu.game_mode_options,
                            placeholder="Select a game mode.",
                            custom_id="persistent_view:osu")

            async def select_callback(interaction: discord.Interaction):
                mode: str = (interaction.data['values'])[0]      # type: ignore
                player: Optional[Dict[str, str]] = await self.osu.get_user(player_name, mode)
                if player is not None:
                    game_mode = self.osu.game_modes[mode]
                    new_embed = discord.Embed(
                        colour=discord.Colour.random(),
                        title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                        url=f"{self.osu.base_profile_url}{player['user_id']}",
                        description=player['desc'],
                    )
                    new_embed.set_thumbnail(url=player['avatar_url'])
                    await interaction.response.edit_message(embed=new_embed)

            select.callback = select_callback
            view = View(timeout=None).add_item(select)
            await i.followup.send(content='', embed=embed, view=view)
        except Exception as e:
            print(e)
            await i.followup.send("Something went wrong, in fact!")


    @group.command(name="recent")
    @app_commands.describe(player_name="The player you want to get the recent plays of, in fact!")
    async def recent(self, i: discord.Interaction, player_name:str):
        """Get the recent plays of a player.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            player_name (str): the player name

        Returns:
            None: None
        """
        await i.response.defer()
        mode = "0"
        if player_name is None:
            return await i.followup.send("Who, in fact?!\nUse `/help recent` for more information, I suppose!")
        try:
            scores = await self.osu.get_user_recent(player_name, mode, "5")
            player = await self.osu.get_user(player_name, mode)
            game_mode = self.osu.game_modes[mode]
            stripped_game_mode = self.osu.stripped_game_modes[mode]
            embed = discord.Embed()
            desc = ""
            if scores is not None:
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
            if player is not None:
                embed = discord.Embed(
                    colour=discord.Colour.random(),
                    title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                    url=f"{self.osu.base_profile_url}{player['user_id']}",
                    description=desc,
                )
                embed.set_thumbnail(url=player['avatar_url'])

            select: Select[View] = Select(options=self.osu.game_mode_options,
                            placeholder="Select a game mode.",
                            custom_id="persistent_view:recent")

            async def select_callback(interaction: discord.Interaction):
                mode: str = (interaction.data['values'])[0]      # type: ignore
                scores = await self.osu.get_user_recent(player_name, mode, "5")
                player = await self.osu.get_user(player_name, mode)
                game_mode = self.osu.game_modes[mode]
                new_desc = ""
                if scores is not None:
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
                if player is not None:
                    new_embed = discord.Embed(
                        colour=discord.Colour.random(),
                        title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                        url=f"{self.osu.base_profile_url}{player['user_id']}",
                        description=new_desc,
                    )
                    new_embed.set_thumbnail(url=player['avatar_url'])
                    await interaction.response.edit_message(embed=new_embed)

            select.callback = select_callback
            view = View(timeout=None).add_item(select)
            await i.followup.send(content='', embed=embed, view=view)
        except Exception as e:
            print(e)
            await i.followup.send("Something went wrong, in fact!")


    @group.command(name="best")
    @app_commands.describe(player_name="The player you want to get the best plays of, in fact!")
    async def osutop(self, i: discord.Interaction, player_name:str):
        """Get the best plays of a player.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            player_name (str): the player name

        Returns:
            None: None
        """
        await i.response.defer()
        mode = "0"
        if player_name is None:
            return await i.followup.send("Who, in fact?!\nUse `/help osutop` for more information, I suppose!")
        try:
            player = await self.osu.get_user(player_name, mode)
            best_scores = await self.osu.get_best(player_name, mode, "5")
            game_mode = self.osu.game_modes[mode]
            stripped_game_mode = self.osu.stripped_game_modes[mode]
            desc = ""
            embed = discord.Embed()
            if best_scores is not None:
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
            if player is not None:
                embed = discord.Embed(
                    colour=discord.Colour.random(),
                    title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                    url=f"{self.osu.base_profile_url}{player['user_id']}",
                    description=desc,
                )
                embed.set_thumbnail(url=player['avatar_url'])

            select: Select[View] = Select(options=self.osu.game_mode_options,
                            placeholder="Select a game mode.",
                            custom_id="persistent_view:best")

            async def select_callback(interaction: discord.Interaction):
                mode: str = (interaction.data['values'])[0]      # type: ignore
                player = await self.osu.get_user(player_name, mode)
                best_scores = await self.osu.get_best(player_name, mode, "5")
                game_mode = self.osu.game_modes[mode]
                new_desc = ""
                if best_scores is not None:
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
                if player is not None:
                    new_embed = discord.Embed(
                        colour=discord.Colour.random(),
                        title=f"**{player['username']} Lvl. {player['level']} ({player['progress']}) {game_mode}**",
                        url=f"{self.osu.base_profile_url}{player['user_id']}",
                        description=new_desc,
                    )
                    new_embed.set_thumbnail(url=player['avatar_url'])
                    await interaction.response.edit_message(embed=new_embed)

            select.callback = select_callback
            view = View(timeout=None).add_item(select)
            await i.followup.send(content='', embed=embed, view=view)
        except Exception as e:
            print(e)
            await i.followup.send("Something went wrong, in fact!")


async def setup(bot: Bot):
    await bot.add_cog(Osu(bot))
