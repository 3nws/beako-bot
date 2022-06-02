import discord
import os
import asyncio
import logging
import typing
import motor.motor_asyncio
import traceback
import sys
import aiohttp

from discord.app_commands.models import AppCommand
from dotenv import load_dotenv  # type: ignore
from discord.ext import commands
from typing import Any, List
from discord.app_commands.checks import cooldown as cooldown_decorator
from discord.app_commands import CommandTree
from pymongo.errors import ServerSelectionTimeoutError

# classes import
from Help import Help, PersistentViewHelp

# commands import
from commands.r_help import commands_help

logging.basicConfig(level=logging.INFO)

# logger = logging.getLogger('discord')
# logger.setLevel(logging.DEBUG)
# handler = logging.FileHandler(
#     filename='discord.log', encoding='utf-8', mode='w')
# handler.setFormatter(logging.Formatter(
#     '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
# logger.addHandler(handler)

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True


class MyTree(CommandTree[Any]):

    def __init__(self, client: discord.Client):
        super().__init__(client)
        self._cooldown_predicate: Any = cooldown_decorator(
            1, 5)(lambda: None).__discord_app_commands_checks__[0]  # type: ignore
        

    async def on_error(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"{interaction.user.mention}, slow down, I suppose!\nYou can try again in {round(error.retry_after, 2)} seconds, in fact!")  # type: ignore
            await asyncio.sleep(float(error.retry_after))  # type: ignore
            await interaction.delete_original_message()
        elif isinstance(error, discord.app_commands.MissingPermissions):
            await interaction.response.send_message("You don't have permission to do that, I suppose!")
        else:
            await interaction.response.send_message("What is that, I suppose?!\nTry `/beakohelp`, in fact!")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.type == discord.InteractionType.autocomplete or interaction.user.id == 442715989310832650:  # type: ignore
            return True
        return await self._cooldown_predicate(interaction)


class Bot(commands.Bot):
    def __init__(self, *args: List[Any], **kwargs: List[Any]):
        super().__init__(*args, **kwargs)
        self.client = None
        self.session = None


    async def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
            else:
                print(f'Unable to load {filename[:-3]}')


    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        try:
            self.client: Any = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017, serverSelectionTimeoutMS=5000)  # type: ignore
            print(await self.client.server_info())
        except ServerSelectionTimeoutError:  # type: ignore
            print("Local not available!")
            self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DB_URL"))  # type: ignore
            
        self.add_view(PersistentViewHelp("0", self))
        
        await self.load_cogs()
        
    async def close(self):
        await super().close()
        await self.session.close()  # type: ignore


    def get_client(self) -> Any:
        return self.client

client = discord.Client(intents=intents)
tree = MyTree(client)
bot = Bot(command_prefix="r.", intents=intents, tree_cls=MyTree, help_command=None,    # type: ignore
          activity=discord.Activity(
              type=discord.ActivityType.listening, name="/beakohelp and Songstress Liliana!" 
          ))  # type: ignore


@bot.tree.command(name='beakohelp', guild=None)
async def help(interaction: discord.Interaction):
    await commands_help(interaction, Help(bot))


@bot.event
async def on_command_error(ctx: commands.Context[Any], error: commands.CommandError):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("What is that, I suppose?!\nTry `/beakohelp`, in fact!")
    else:
        print(error)


@bot.event
async def on_guild_join(guild: discord.Guild):
    msg = f"Just joined {guild.name} with {guild.member_count} members, in fact!"  # type: ignore
    user = bot.get_user(442715989310832650)
    await user.send(msg)  # type: ignore
    print(msg)


@bot.event
async def on_guild_remove(guild: discord.Guild):
    msg = f"Just left {guild.name}, in fact!\nThey didn't like Betty, I suppose!"  # type: ignore
    user = bot.get_user(442715989310832650)
    await user.send(msg)  # type: ignore
    print(msg)


@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context[Any], guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~"]] = None) -> None:
    if not guilds:
        if spec == "~":
            fmt: List[AppCommand] = await ctx.bot.tree.sync(guild=ctx.guild)  # type: ignore
        else:
            fmt: List[AppCommand] = await ctx.bot.tree.sync()  # type: ignore

        await ctx.send(
            f"Synced {len(fmt)} commands {'globally' if spec is None else 'to the current guild.'}"  # type: ignore
        )
        return

    fmt: int = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)  # type: ignore
        except discord.HTTPException:
            pass
        else:
            fmt += 1

    await ctx.send(f"Synced the tree to {fmt}/{len(guilds)} guilds.")
  

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}\n')  # type: ignore


async def main():
    async with bot:
        await bot.start(os.getenv("TOKEN", "no"))

asyncio.run(main())
