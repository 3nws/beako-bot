import discord

from Help_Messages import messages
from discord.ui import View
from discord.ext import commands
from typing import TypeVar

T = TypeVar("T")

track_cmds = ["add", "remove", "manga", "last"]
admin_cmds = ["kick", "ban", "unban", "clean", "purge"]
tag_cmds = ["tag show", "tag add", "tag remove"]
fun_cmds = ["say", "roll", "rps", "coinflip", "flip"]
gif_cmds = ["hug", "pout", "pat", "smug"]
osu_cmds = ["osu best", "osu recent", "osu profile"]
timer_cmds = ["remind", "alarm", "time"]
util_cmds = ["sauce", "avatar", "banner", "savatar", "poll", "series"]
warframe_cmds = ["item"]
mode_titles = [
    "Series tracking commands",
    "Admin commands",
    "Tag commands",
    "Fun commands",
    "Gif commands",
    "osu! commands",
    "Timer commands",
    "Util commands",
    "Warframe commands",
]

modes = [
    track_cmds,
    admin_cmds,
    tag_cmds,
    fun_cmds,
    gif_cmds,
    osu_cmds,
    timer_cmds,
    util_cmds,
    warframe_cmds
]
        
class Dropdown(discord.ui.Select):
    def __init__(self, mode: str, bot: commands.Bot):
        cmd_options = [
            discord.SelectOption(value="0", label="Series tracking", emoji="<a:_:459105999618572308>"),
            discord.SelectOption(value="1", label="Admin", emoji="<:_:596577110982918146>"),
            discord.SelectOption(value="2", label="Tag", emoji="<:_:576499016376909854>"),
            discord.SelectOption(value="3", label="Fun", emoji="<:_:586291133059956908>"),
            discord.SelectOption(value="4", label="Gif", emoji="<a:_:662661255278100489>"),
            discord.SelectOption(value="5", label="osu!", emoji="<:_:979258962731995136>"),
            discord.SelectOption(value="6", label="Timer", emoji="⌛"),
            discord.SelectOption(value="7", label="Util", emoji="<:_:979259589633654837>"),
            discord.SelectOption(value="8", label="Warframe", emoji="<:_:979258513429782588>"),
        ]

        self.bot: commands.Bot = bot
        self.mode: str = mode
        
        super().__init__(placeholder="Select a category.", custom_id="persistent_view:help", options=cmd_options)

    
    async def callback(self, i: discord.Interaction) -> None:
        self.mode = (i.data['values'])[0]
        new_desc = ""
        for cmd in modes[int(self.mode)]:
            new_desc += f"**/{cmd}**\n"
            new_desc += f"{messages[cmd]}\n"
        new_embed = discord.Embed(
            colour=discord.Colour.random(),
            title=f"{mode_titles[int(self.mode)]}",
            description=new_desc,
        )
        new_embed.set_thumbnail(url=self.bot.user.avatar.url)
        await i.response.edit_message(embed=new_embed)

class PersistentViewHelp(View):
    def __init__(self, mode: str, bot: commands.Bot):
        super().__init__(timeout=None)
        self.add_item(Dropdown(mode, bot))


class Help:
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def get_help(self, i: discord.Interaction) -> None:
        mode = "0"
        msg: discord.Message = await i.channel.send("Loading, I suppose!")
        try:
            desc = ""
            for cmd in modes[int(mode)]:
                desc += f"**/{cmd}**\n"
                desc += f"{messages[cmd]}\n"
            embed = discord.Embed(
                colour=discord.Colour.random(),
                title=f"{mode_titles[int(mode)]}",
                description=desc,
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)

            selectView = PersistentViewHelp(mode, self.bot)
            await msg.delete()
            await i.response.send_message(content='', embed=embed, view=selectView)
        except Exception as e:
            print(e)
            await i.response.send_message("Something went wrong, in fact!")
