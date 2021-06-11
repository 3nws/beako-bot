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

import threading

load_dotenv()
bot = commands.Bot(command_prefix='r.')

client = pymongo.MongoClient(os.getenv('DB_URL'))

db_channels = client.channel_id

db_chapter = client.chapter

channels = db_channels.data

@bot.command(case_insensitive = True, aliases = ["remindme", "remind_me"])
async def remind(ctx, time, unit, *, reminder=''):
    embed = discord.Embed(color=discord.Colour.random(), timestamp=datetime.utcnow())
    seconds = 0
    if unit.lower().endswith("d"):
        seconds += int(time) * 60 * 60 * 24
        counter = f"{seconds // 60 // 60 // 24} days"
    if unit.lower().endswith("h"):
        seconds += int(time) * 60 * 60
        counter = f"{seconds // 60 // 60} hours"
    elif unit.lower().endswith("m"):
        seconds += int(time) * 60
        counter = f"{seconds // 60} minutes"
    elif unit.lower().endswith("s"):
        seconds += int(time)
        counter = f"{seconds} seconds"
    if seconds == 0:
        embed.add_field(name='Warning', value="ERROR IT IS!")
    elif seconds > 7776000:
        embed.add_field(name='Warning', value="We might not survive long enough to do this!")
    else:
        if reminder=='':
          await ctx.send(f"I'll ping you in {counter}.")
        else:
          await ctx.send(f"I'll ping you in {counter} about '{reminder}'.")
        await asyncio.sleep(seconds)
        if reminder=='':
          await ctx.send(f"Yo {ctx.author.mention}, what up!")
        else:
          await ctx.send(f"Yo {ctx.author.mention}, what up! Time about '{reminder}'!")
        return
    await ctx.send(embed=embed)

@bot.command(aliases = ["yeet", "yeeto"])
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason=None):
  await user.kick(reason=reason)
  await ctx.send(f"{user} has been yeeted.")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, *, reason=None):
  await user.ban(reason=reason)
  await ctx.send(f"{user} has been yeeted forever.")

@bot.command()
@commands.has_permissions(administrator=True)
async def unban(ctx, *, member):
  banned_users = await ctx.guild.bans()
  member_name, member_discriminator = member.split('#')

  for ban_entry in banned_users:
    user = ban_entry.user
  
  if (user.name, user.discriminator) == (member_name, member_discriminator):
    await ctx.guild.unban(user)
    await ctx.send(f"{user} has been unbanned.")
    return

@bot.command(aliases = ["clear"])
@commands.has_permissions(administrator=True)
async def clean(ctx, limit: int):
  await ctx.channel.purge(limit=limit+1)
  await ctx.send('Cleared by {}'.format(ctx.author.mention))
  await ctx.message.delete()

@bot.command()
async def say(ctx, *, msg=''):
  await ctx.message.delete()
  await ctx.send(msg)

@bot.command(aliases = ["add"])
async def add_channel(ctx):
    channel_entry = {
      'id': ctx.channel.id,
    }
    if channels.count_documents(channel_entry, limit = 1) != 0:
          await ctx.send("This text channel is already on the receiver list!")
          return
    channels.insert_one(channel_entry)
    await ctx.send("This text channel will receive notifications.")
    
@bot.command(aliases = ["remove"])
async def remove_channel(ctx):
    channel_entry = {
      'id': ctx.channel.id,
    }
    if channels.count_documents(channel_entry, limit = 1) == 0:
          await ctx.send("This text channel is not on the receiver list!")
          return
    channels.find_one_and_delete(channel_entry)
    await ctx.send("This text channel will no longer receive notifications.")

@bot.command()
async def avatar(ctx, member: discord.Member=None):
  avatar_frame = discord.Embed(
    color = discord.Colour.random()
  )
  if member:
    avatar_frame.add_field(name=str(ctx.author)+" requested", value=member.mention+"'s avatar.")
    avatar_frame.set_image(url=f'{member.avatar_url}')
  else:
    avatar_frame.add_field(name=str(ctx.author), value=ctx.author.mention+"'s avatar.")
    avatar_frame.set_image(url=f'{ctx.author.avatar_url}')
    
  await ctx.send(embed=avatar_frame)


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
