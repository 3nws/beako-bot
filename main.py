import discord
import os
import asyncio
import logging
import typing

from discord.app_commands.models import AppCommand
from dotenv import load_dotenv  # type: ignore
from discord.ext import commands
from typing import List


from Bot import MyTree, Bot, Help


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
async def on_command_error(ctx: commands.Context[Bot], error: commands.CommandError):
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
async def sync(ctx: commands.Context[Bot], guilds: commands.Greedy[discord.Object], spec: typing.Optional[typing.Literal["~"]] = None) -> None:
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
