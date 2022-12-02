import asyncio
import os
import motor.motor_asyncio
import traceback
import sys
import aiohttp
import discord
import socket
import json

from discord.app_commands.checks import cooldown as cooldown_decorator
from discord.app_commands import CommandTree
from pymongo.errors import ServerSelectionTimeoutError
from typing import Any, List, Tuple, Dict
from discord.ext import commands
from aiohttp import ClientSession
from discord.ui import View
from dotenv import load_dotenv

from Help_Messages import messages

load_dotenv()

track_cmds = ["add", "remove", "manga", "last"]
admin_cmds = ["kick", "ban", "unban", "clean", "purge"]
tag_cmds = ["tag show", "tag add", "tag remove"]
fun_cmds = [
    "wordle start",
    "wordle guess",
    "say",
    "roll",
    "rps",
    "coinflip",
    "flip",
    "imagesearch",
]
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
    warframe_cmds,
]


class Bot(commands.Bot):
    def __init__(self, *args: List[Any], **kwargs: List[Any]):
        super().__init__(*args, **kwargs)
        self._client = None
        self.session: ClientSession

        self.no_client: bool = True

        self.stats = {}

        # self.avatar_task_on: bool = not True
        # self.chapter_task_on: bool = True

    async def load_cogs(self):
        await self.load_extension("jishaku")
        for filename in os.listdir("./app/cogs"):
            if filename.endswith(".py"):
                await self.load_extension(f"cogs.{filename[:-3]}")
            else:
                print(f"Unable to load {filename[:-3]}")

    async def handle_client(self, client):
        try:
            message = (await self.loop.sock_recv(client, 255)).decode("utf8")
        except ConnectionResetError:
            self.no_client = True

    async def send_stats(self, client):
        stats_: Dict[str, int] = {}
        for tup in self.tree.app_command_invokes_namespaces:  # type: ignore
            command_name = tup[0]
            if stats_.get(command_name, None):
                stats_[command_name] += 1
            else:
                stats_[command_name] = 1
        stats_ = dict(sorted(stats_.items(), key=lambda item: item[1], reverse=True))
        num_members: int = 0
        for guild in set(self.guilds):
            num_members += guild.member_count if guild.member_count is not None else 0

        self.stats = {
            "total": self.tree.app_commands_invoked,  # type: ignore
            "namespaces": self.tree.app_command_invokes_namespaces,  # type: ignore
            "stats": stats_,
            "servers": len(self.guilds),
            "members": num_members,
        }
        try:
            await self.loop.sock_sendall(client, json.dumps(self.stats).encode("utf8"))
        except (BrokenPipeError, ConnectionResetError):
            self.no_client = True
            try:
                client.close()
            except Exception:
                pass

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        try:
            self._client: Any = motor.motor_asyncio.AsyncIOMotorClient(  # type: ignore
                "localhost", 27017, serverSelectionTimeoutMS=5000
            )
            print(await self._client.server_info())
        except ServerSelectionTimeoutError:
            print("Local not available!")
            self._client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DB_URL"))  # type: ignore

        self.add_view(PersistentViewHelp("0", self))

        await self.load_cogs()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", 5555))
        self.server.listen(1)
        self.server.setblocking(False)

    async def close(self):
        await self.session.close()
        for view in self.persistent_views:
            await view.on_timeout()
        await super().close()

    @property
    def client(self) -> Any:
        return self._client


class PersistentViewHelp(View):
    def __init__(self, mode: str, bot: Bot):
        super().__init__(timeout=None)
        self.add_item(Dropdown(mode, bot))


class Dropdown(discord.ui.Select[PersistentViewHelp]):
    def __init__(self, mode: str, bot: Bot):
        cmd_options = [
            discord.SelectOption(
                value="0", label="Series tracking", emoji="<a:_:459105999618572308>"
            ),
            discord.SelectOption(
                value="1", label="Admin", emoji="<:_:596577110982918146>"
            ),
            discord.SelectOption(
                value="2", label="Tag", emoji="<:_:576499016376909854>"
            ),
            discord.SelectOption(
                value="3", label="Fun", emoji="<:_:586291133059956908>"
            ),
            discord.SelectOption(
                value="4", label="Gif", emoji="<a:_:662661255278100489>"
            ),
            discord.SelectOption(
                value="5", label="osu!", emoji="<:_:979258962731995136>"
            ),
            discord.SelectOption(value="6", label="Timer", emoji="⌛"),
            discord.SelectOption(
                value="7", label="Util", emoji="<:_:979259589633654837>"
            ),
            discord.SelectOption(
                value="8", label="Warframe", emoji="<:_:979258513429782588>"
            ),
        ]

        self.bot: Bot = bot
        self.mode: str = mode

        super().__init__(
            placeholder="Select a category.",
            custom_id="persistent_view:help",
            options=cmd_options,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        self.mode = self.values[0]
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
        await interaction.response.edit_message(embed=new_embed)


class Help:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def get_help(self, i: discord.Interaction) -> None:
        mode = "0"
        await i.response.defer()
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
            await i.followup.send(content="", embed=embed, view=selectView)
        except Exception as e:
            print(e)
            await i.followup.send("Something went wrong, in fact!")


class MyTree(CommandTree[discord.Client]):
    def __init__(self, client: discord.Client):
        super().__init__(client)
        self._cooldown_predicate: Any = cooldown_decorator(1, 5)(
            lambda: None
        ).__discord_app_commands_checks__[  # type: ignore
            0
        ]
        self.app_commands_invoked: int = 0
        self.app_command_invokes_namespaces: List[
            Tuple[str, str, List[Tuple[Any, Any]]]
        ] = []

    async def on_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError,
    ):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"{interaction.user.mention}, slow down, I suppose!\nYou can try again in {round(error.retry_after, 2)} seconds, in fact!"
            )
            await asyncio.sleep(float(error.retry_after))
            await interaction.delete_original_response()
        elif isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message(
                "You don't have permission to do that, I suppose!"
            )
        else:
            # This next segment is stupid. You have been warned!
            if " ".join(str(error).split()[-2:]) == "Server disconnected":
                callback = interaction.command.callback
                data = interaction.data["options"][0]  # type: ignore
                args = {data["name"]: data["value"], "repeat": False}  # type: ignore
                self.session = aiohttp.ClientSession()
                fake_self = type("self", (object,), {"bot": self})
                await callback(fake_self, interaction, **args)  # type: ignore
                return
            await interaction.response.send_message(
                "What is that, I suppose?!\nTry `/beakohelp`, in fact!"
            )
            traceback_ = error.__traceback__
            traceback.print_exception(type(error), error, traceback_, file=sys.stderr)
            user = interaction.client.get_user(442715989310832650)
            await user.send(
                f"```py\n{''.join(traceback.format_exception(None, error, traceback_))}```"
            )
            await user.send(
                f"{interaction.user.name} used {interaction.command.name or 'unknown'} which resulted with the error above!\
                            \nNamespace: {interaction.namespace}"
            )

    async def send_info(self, interaction: discord.Interaction):
        self.app_commands_invoked += 1
        temp = []
        l = list(interaction.namespace.__dict__.items())
        for a in l:
            if isinstance(a, (list, tuple, set)):
                try:
                    if isinstance(a[-1], (discord.User, discord.Member)):
                        temp.append(a[-1].name)
                    else:
                        temp.append(a[-1])
                except IndexError:
                    pass
        self.app_command_invokes_namespaces.append(
            (interaction.command.name, interaction.user.name, temp)
        )
        if self.app_commands_invoked % 10 == 0:
            user = interaction.client.get_user(442715989310832650)
            await user.send(
                f"{self.app_commands_invoked} application commands have been invoked this session!\
                    \nUse `r.getcount` to see them."
            )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.type is not discord.InteractionType.autocomplete:
            await self.send_info(interaction)
        if (
            interaction.type is discord.InteractionType.autocomplete
            or interaction.user.id == 442715989310832650
        ):
            return True
        return await self._cooldown_predicate(interaction)
