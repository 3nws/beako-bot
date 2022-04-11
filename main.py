import discord
import os
import dns
import asyncio
import logging
import threading

from dotenv import load_dotenv
from discord.ext import tasks, commands

# classes import
from ChannelList import ChannelList
from Help import Help

# commands import
from commands.r_help import commands_help
from commands.db.r_db import (
    tasks_check_chapter,
    tasks_filter_channels,
    tasks_change_avatar,
    commands_flip,
    commands_following,
    commands_latest_chapter,
)
from commands.db.r_add_channel import commands_add_channel
from commands.db.r_remove_channel import commands_remove_channel

# logging.basicConfig(level=logging.DEBUG)

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
bot = commands.Bot(command_prefix="r.", intents=intents)
bot.remove_command("help")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')
    else:
        print(f'Unable to load {filename[:-3]}')

# adds the channel to the notifications list
@bot.command(aliases=["add"])
async def add_channel(ctx, *, series=""):
    await commands_add_channel(bot, ctx, ChannelList(series, ctx.channel.id))

# removes the channel from the notifications list
@bot.command(aliases=["remove"])
async def remove_channel(ctx, *, series=""):
    await commands_remove_channel(bot, ctx, ChannelList(series, ctx.channel.id))

# sends a message with the list of series a channel is following
@bot.command(aliases=["watching", "fol", "follow"])
async def following(ctx):
    await commands_following(ctx, bot)

# sends the latest english translated chapter
@bot.command(aliases=["latest", "last", "chp"])
async def latest_chapter(ctx, *, series=""):
    await commands_latest_chapter(ctx, series)
    
# flip your friends off
@bot.command()
async def flip(ctx):
    await commands_flip(ctx)

# help command
@bot.command()
async def help(ctx, *, cmd=""):
    await commands_help(ctx, Help(cmd))


# task sets a random avatar every day
@tasks.loop(hours=24)
async def change_avatar():
    await tasks_change_avatar(bot)


# task that removes non existing(deleted) channels every 60 seconds
@tasks.loop(seconds=60)
async def filter_channels():
    await tasks_filter_channels(bot)


# task that checks chapter every 60 seconds
@tasks.loop(seconds=10)
async def check_chapter():
    await tasks_check_chapter(bot)


# catch command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("What is that, I suppose?!\nTry `r.help`, in fact!")


# runs everytime the bot comes online
@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}\n')
    print(f'Server List ({len(bot.guilds)})\n')
    server_counter = 1
    for guild in set(bot.guilds):
        print(
            f"{server_counter}. {guild.name}, owned by {guild.owner} with {guild.member_count} members")
        server_counter += 1
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.listening, name="r.help and Songstress Liliana!"
        )
    )
    change_avatar.start()
    await asyncio.sleep(60)
    check_chapter.start()
    filter_channels.start()


bot.run(os.getenv("TOKEN"))
