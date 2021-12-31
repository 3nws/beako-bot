import discord
import os
import dns
import asyncio

from dotenv import load_dotenv
from discord.ext import tasks, commands

# classes import
from ChannelList import ChannelList
from Help import Help

# commands import
from commands.r_help import commands_help
from commands.r_servers import commands_servers
from commands.r_say import commands_say
from commands.r_remind import commands_remind
from commands.r_kick import commands_kick
from commands.r_ban import commands_ban
from commands.r_unban import commands_unban
from commands.r_clean import commands_clean
from commands.r_avatar import commands_avatar
from commands.r_roll import commands_roll
from commands.r_rps import commands_rps
from commands.r_coinflip import commands_coinflip
from commands.r_reverse_image_search import commands_reverse_image_search
from commands.r_gif import commands_pat, commands_pout, commands_smug
from commands.db.r_db import tasks_check_chapter, tasks_filter_channels, commands_flip, commands_latest_chapter
from commands.db.r_add_channel import commands_add_channel
from commands.db.r_remove_channel import commands_remove_channel

import threading

load_dotenv()


intents = discord.Intents.default()
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='r.', intents=intents)
bot.remove_command('help')

# reverse search image
@bot.command(aliases= ["ris", "sauce", "source"])
async def reverse_image_search(ctx, url=""):
  await commands_reverse_image_search(ctx, url)

# play rock paper scissors
@bot.command()
async def rps(ctx, choice):
  await commands_rps(ctx, choice)

# sends the latest english translated chapter
@bot.command(aliases = ["latest", "last", "chp"])
async def latest_chapter(ctx):
  await commands_latest_chapter(ctx)

# coin flip
@bot.command(aliases = ["coin"])
async def coinflip(ctx, heads=None, tails=None):
  await commands_coinflip(ctx, heads, tails)

# smug uwu
@bot.command()
async def smug(ctx):
  await commands_smug(ctx)

# pat uwu
@bot.command()
async def pat(ctx, user : discord.Member=None):
  await commands_pat(ctx, user)

# pout uwu
@bot.command()
async def pout(ctx):
  await commands_pout(ctx)

# flip your friends off
@bot.command()
async def flip(ctx):
  await commands_flip(ctx)

# roll iq
@bot.command()
async def roll(ctx, num=""):
  await commands_roll(ctx, num)

# reminds the user about anything after specified time 
@bot.command(case_insensitive = True, aliases = ["remindme", "remind_me"])
async def remind(ctx, time, unit=None, *, reminder=''):
  await commands_remind(ctx, time, unit, reminder)

# kicks user
@bot.command(aliases = ["yeet", "yeeto"])
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason=None):
  await commands_kick(ctx, user, reason)

# bans user
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, *, reason=None):
  await commands_ban(ctx, user, reason)

# unbans user
@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
  await commands_unban(ctx, member)

# clears chat
@bot.command(aliases = ["clear"])
@commands.has_permissions(administrator=True)
async def clean(ctx, limit: int, msg_id=None):
  await commands_clean(ctx, limit, msg_id)

# beako will repeat what is passed in
@bot.command()
async def say(ctx, *, msg=''):
  await commands_say(ctx, msg)
  
# print the joined servers in the logs
@bot.command()
async def servers(ctx):
  await commands_servers(ctx, bot)
  
# sends a user's avatar
@bot.command()
async def avatar(ctx, member: discord.Member=None):
  await commands_avatar(ctx, member)

@bot.command(aliases = ["add"])
async def add_channel(ctx, *, series=''):
  await commands_add_channel(ctx, ChannelList(series, ctx.channel.id))
  
@bot.command(aliases = ["remove"])
async def remove_channel(ctx, *, series=''):
  await commands_remove_channel(ctx, ChannelList(series, ctx.channel.id))
  
# help command
@bot.command()
async def help(ctx, *,  cmd=''):
  await commands_help(ctx, Help(cmd))

# task that removes non existing(deleted) channels every 10 seconds
@tasks.loop(seconds=10)
async def filter_channels():
  await tasks_filter_channels(bot)

# task that checks chapter every 10 seconds
@tasks.loop(seconds=10)
async def check_chapter():
  await tasks_check_chapter(bot)

# runs everytime the bot comes online
@bot.event
async def on_ready():
  print(f'Logged in as: {bot.user.name}\n')
  print(f'Server List ({len(bot.guilds)})\n')
  server_counter = 1
  for guild in bot.guilds:
    print(f"{server_counter}. {guild.name}")
    server_counter += 1
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="r.help and Songstress Liliana!"))
  check_chapter.start()
  filter_channels.start()

bot.run(os.getenv('TOKEN'))
