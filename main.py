import discord
import os
import dns
import asyncio
import logging
import threading
import typing
import pymongo
import motor.motor_asyncio
import traceback
import sys

from dotenv import load_dotenv
from discord.ext import tasks, commands
from discord import app_commands
from typing import Callable, Awaitable
from discord.app_commands.checks import cooldown as cooldown_decorator
from discord.app_commands import CommandTree

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


class MyTree(CommandTree):

    def __init__(self, client):
        super().__init__(client)
        self._cooldown_predicate: CooldownPredicate = cooldown_decorator(
            1, 5)(lambda: None).__discord_app_commands_checks__[0]

    async def on_error(self, interaction, error):
        if isinstance(error, discord.app_commands.errors.CommandOnCooldown):
            await interaction.response.send_message(f"{interaction.user.mention}, slow down, I suppose!\nYou can try again in {round(error.retry_after, 2)} seconds, in fact!")
            await asyncio.sleep(float(error.retry_after))
            await interaction.delete_original_message()
        else:
            await interaction.response.send_message("What is that, I suppose?!\nTry `/beakohelp`, in fact!")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.type == discord.InteractionType.autocomplete:
            return True
        return await self._cooldown_predicate(interaction)


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.client = None

    async def load_cogs(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.load_extension(f'cogs.{filename[:-3]}')
            else:
                print(f'Unable to load {filename[:-3]}')

    async def setup_hook(self) -> None:
        
        # self.client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
        
        self.client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("DB_URL"))
            
        self.add_view(PersistentViewHelp(0, self))
        
        await self.load_cogs()

    def get_client(self):
        return self.client


client = discord.Client(intents=intents)
tree = MyTree(client)
bot = Bot(command_prefix="r.", intents=intents, tree_cls=MyTree, help_command=None,
          activity=discord.Activity(
              type=discord.ActivityType.listening, name="/beakohelp and Songstress Liliana!"
          ))


@bot.tree.command(name='beakohelp', guild=None)
async def help(interaction: discord.Interaction):
    await commands_help(bot, interaction, Help(bot))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("What is that, I suppose?!\nTry `/beakohelp`, in fact!")
    else:
        print(error)


@bot.event
async def on_guild_join(guild):
    msg = f"Just joined {guild.name} with {guild.member_count} members, in fact!"
    user = bot.get_user(442715989310832650)
    await user.send(msg)
    print(msg)


@bot.event
async def on_guild_remove(guild):
    msg = f"Just left {guild.name}, in fact!\n\
            They didn't like Betty, I suppose!"
    user = bot.get_user(442715989310832650)
    await user.send(msg)
    print(msg)


@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context, guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~"]] = None) -> None:
    if not guilds:
        if spec == "~":
            fmt = await ctx.bot.tree.sync(guild=ctx.guild)
        else:
            fmt = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(fmt)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    fmt = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            fmt += 1

    await ctx.send(f"Synced the tree to {fmt}/{len(guilds)} guilds.")


@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}\n')


async def main():
    async with bot:
        await bot.start(os.getenv("TOKEN"))

asyncio.run(main())
