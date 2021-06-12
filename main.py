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
from commands.db.r_db import commands_add_channel, commands_remove_channel

import threading

load_dotenv()

client = pymongo.MongoClient(os.getenv('DB_URL'))

db_channels = client.channel_id

db_chapter = client.chapter

channels = db_channels.data

bot = commands.Bot(command_prefix='r.')

@bot.command(case_insensitive = True, aliases = ["remindme", "remind_me"])
async def remind(ctx, time, unit, *, reminder=''):
  await commands_remind(ctx, time, unit, reminder)

@bot.command(aliases = ["yeet", "yeeto"])
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason=None):
  await commands_kick(ctx, user, reason)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, *, reason=None):
  await commands_ban(ctx, user, reason)

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
  await commands_unban(ctx, member)

@bot.command(aliases = ["clear"])
@commands.has_permissions(administrator=True)
async def clean(ctx, limit: int):
  await commands_clean(ctx, limit)

@bot.command()
async def say(ctx, *, msg=''):
  await commands_say(ctx, msg)
  
@bot.command()
async def avatar(ctx, member: discord.Member=None):
  await commands_avatar(ctx, member)

# Unholy commands

@bot.command(aliases = ["add"])
async def add_channel(ctx):
  await commands_add_channel(ctx)
  
@bot.command(aliases = ["remove"])
async def remove_channel(ctx):
  await commands_remove_channel(ctx)


# task that checks chapter every 10 seconds
@tasks.loop(seconds=10)
async def check_chapter():
  page = requests.get('https://witchculttranslation.com/arc-7/')

  soup = BeautifulSoup(page.content, 'html.parser')

  most_recent_post = soup.find_all('h3', 'rpwe-title')[0]

  post_link = most_recent_post.find('a')

  most_recent_post = most_recent_post.text
  most_recent_post_array = most_recent_post.split()

  most_recent_post_str = ""

  for i in range(0, 4):
      most_recent_post_str += most_recent_post_array[i] + " "

  most_recent_post_str = most_recent_post_str.strip()

  li_element = soup.find_all('li', 'rpwe-li rpwe-clearfix')[0]

  try:
      if 'href' in post_link.attrs:
          latest_chapter_translated_link = post_link.get('href')
  except:
      pass

  time_posted = li_element.find('time').text
  
  last_chapter = db_chapter.data.find_one()
  
  if last_chapter['title'] != most_recent_post_str:
      db_chapter.data.find_one_and_update({'title':str(last_chapter['title'])}, { '$set': { "title" : most_recent_post_str} })
      for channel in channels.find():
          if bot.get_channel((channel['id'])):
            await (bot.get_channel(int(channel['id']))).send(f'{most_recent_post} has been translated {time_posted}.\n{latest_chapter_translated_link}')
            
@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Songstress Liliana!"))
  check_chapter.start()
    

bot.run(os.getenv('TOKEN'))
