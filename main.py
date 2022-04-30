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
    commands_get_manga_info
)
from commands.db.r_add_channel import commands_add_channel
from commands.db.r_remove_channel import commands_remove_channel

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
bot = commands.Bot(command_prefix="r.", intents=intents)
bot.remove_command("help")


async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
        else:
            print(f'Unable to load {filename[:-3]}')


# get manga info
@bot.tree.command(name='manga', guild = None)
async def manga(interaction: discord.Interaction, *, series:str=""):
    await commands_get_manga_info(interaction, series)


# adds the channel to the notifications list
@bot.tree.command(name='add', guild = None)
@commands.has_permissions(manage_channels=True)
async def add_channel(interaction: discord.Interaction, *, series:str=""):
    await commands_add_channel(bot, interaction, ChannelList(series, interaction.channel_id))


# removes the channel from the notifications list
@bot.tree.command(name='remove', guild = None)
@commands.has_permissions(manage_channels=True)
async def remove_channel(interaction: discord.Interaction, *, series:str=""):
    await commands_remove_channel(bot, interaction, ChannelList(series, interaction.channel_id))


# sends a message with the list of series a channel is following
@bot.tree.command(name='following', guild = None)
async def following(interaction: discord.Interaction):
    await commands_following(interaction, bot)


# sends the latest english translated chapter
@bot.tree.command(name='last', guild = None)
async def latest_chapter(interaction: discord.Interaction, *, series:str=""):
    await commands_latest_chapter(bot, interaction, series)


# flip your friends off
@bot.tree.command(name='flip', guild = None)
async def flip(interaction: discord.Interaction):
    await commands_flip(interaction)


# help command
@bot.tree.command(name='help', guild = None)
async def help(interaction: discord.Interaction, *, cmd:str=""):
    await commands_help(interaction, Help(cmd))


# task sets a random avatar every day
@tasks.loop(hours=24)
async def change_avatar():
    await tasks_change_avatar(bot)


# task that removes non existing(deleted) channels every 60 seconds
@tasks.loop(seconds=60)
async def filter_channels():
    await tasks_filter_channels(bot)


# task that checks chapter every 60 seconds
@tasks.loop(seconds=60)
async def check_chapter():
    await tasks_check_chapter(bot)


# catch command errors
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        await ctx.send("What is that, I suppose?!\nTry `/help`, in fact!")

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
async def sync(ctx, guild=None):
    if guild is None:
        print(await bot.tree.sync(guild=discord.Object(658947832392187906)))
    else:
        print(await bot.tree.sync())

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
    check_chapter.start()
    filter_channels.start()


async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("TOKEN"))

asyncio.run(main())
