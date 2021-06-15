import discord
import os
import requests
import dns
import pymongo
import asyncio

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord.ext import tasks, commands
from datetime import datetime

from commands.r_say import commands_say
from commands.r_remind import commands_remind
from commands.r_kick import commands_kick
from commands.r_ban import commands_ban
from commands.r_unban import commands_unban
from commands.r_clean import commands_clean
from commands.r_avatar import commands_avatar
from commands.r_roll import commands_roll
from commands.r_flip import commands_flip
from commands.r_gif import commands_pat, commands_pout
from commands.db.r_db import commands_add_channel, commands_remove_channel, tasks_check_chapter, tasks_filter_channels

import threading

load_dotenv()

client = pymongo.MongoClient(os.getenv('DB_URL'))

db_channels = client.channel_id

db_chapter = client.chapter

channels = db_channels.data

bot = commands.Bot(command_prefix='r.')

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
async def remind(ctx, time, unit, *, reminder=''):
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
async def clean(ctx, limit: int):
  await commands_clean(ctx, limit)

# beako will repeat what is passed in
@bot.command()
async def say(ctx, *, msg=''):
  await commands_say(ctx, msg)
  
# sends a user's avatar
@bot.command()
async def avatar(ctx, member: discord.Member=None):
  await commands_avatar(ctx, member)

# add channel to database
@bot.command(aliases = ["add"])
async def add_channel(ctx):
  await commands_add_channel(ctx)
  
# remove channel from database
@bot.command(aliases = ["remove"])
async def remove_channel(ctx):
  await commands_remove_channel(ctx)

# task that removes non existing(deleted) channels every 10 seconds
@tasks.loop(seconds=10)
async def filter_channels():
  await tasks_filter_channels(bot)

# task that checks chapter every 10 seconds
@tasks.loop(seconds=10)
async def check_chapter():
  await tasks_check_chapter(bot)

# runs everytime the bot is back online
@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Songstress Liliana!"))
  check_chapter.start()
  filter_channels.start()

bot.run(os.getenv('TOKEN'))
