import discord
import os
import aiohttp
import asyncio
import json

from Help_Messages import messages, aliases
from discord.ui import View, Select
from discord.ext import commands


class Help:
    def __init__(self, bot):
        self.bot = bot
        self.track_cmds = ["add", "remove", "manga", "last"]
        self.admin_cmds = ["kick", "ban", "unban", "clean", "purge"]
        self.fun_cmds = ["say", "roll", "rps", "coinflip", "flip"]
        self.gif_cmds = ["hug", "pout", "pat", "smug"]
        self.osu_cmds = ["best", "recent", "osu"]
        self.timer_cmds = ["remind", "alarm", "time"]
        self.util_cmds = ["sauce", "avatar", "banner", "savatar", "poll", "series"]
        self.warframe_cmds = ["item"]
        self.mode_titles = [
            "Series tracking commands",
            "Admin commands",
            "Fun commands",
            "Gif commands",
            "osu! commands",
            "Timer commands",
            "Util commands",
            "Warframe commands",
        ]
        self.modes = [
            self.track_cmds,
            self.admin_cmds,
            self.fun_cmds,
            self.gif_cmds,
            self.osu_cmds,
            self.timer_cmds,
            self.util_cmds,
            self.warframe_cmds
        ]
        self.cmd_options = [
            discord.SelectOption(value=0, label="Series tracking"),
            discord.SelectOption(value=1, label="Admin"),
            discord.SelectOption(value=2, label="Fun"),
            discord.SelectOption(value=3, label="Gif"),
            discord.SelectOption(value=4, label="osu!"),
            discord.SelectOption(value=5, label="Timer"),
            discord.SelectOption(value=6, label="Util"),
            discord.SelectOption(value=7, label="Warframe"),
        ]

    async def get_help(self, i: discord.Interaction, bot):
        mode = 0
        msg = await i.channel.send("Loading, I suppose!")
        try:
            desc = ""
            for cmd in self.modes[int(mode)]:
                desc += f"**/{cmd}**\n"
                desc += f"{messages[cmd]}\n"
            embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"{self.mode_titles[int(mode)]}",
                description=desc,
            )
            embed.set_thumbnail(url=bot.user.avatar.url)

            select = Select(options=self.cmd_options,
                            placeholder="Select a category.",
                            custom_id="persistent_view:help")

            async def select_callback(i):
                mode = (i.data['values'])[0]
                new_desc = ""
                for cmd in self.modes[int(mode)]:
                    new_desc += f"**/{cmd}**\n"
                    new_desc += f"{messages[cmd]}\n"
                new_embed = discord.Embed(
                    colour=discord.Colour.random(),
                    title=f"{self.mode_titles[int(mode)]}",
                    description=new_desc,
                )
                new_embed.set_thumbnail(url=bot.user.avatar.url)
                await i.response.edit_message(embed=new_embed)

            select.callback = select_callback
            view = View(timeout=None).add_item(select)
            await msg.delete()
            await i.response.send_message(content='', embed=embed, view=view)
        except Exception as e:
            print(e)
            await i.response.send_message("Something went wrong, in fact!")
