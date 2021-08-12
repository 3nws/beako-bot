import pymongo
import requests
import os
import random

from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

client = pymongo.MongoClient(os.getenv('DB_URL'))

db_channels = client.channel_id

db_chapter = client.chapter

db_flips = client.flips

flips = db_flips.data

channels = db_channels.data

# sends the latest english translated chapter
async def commands_latest_chapter(ctx):
  page = requests.get('https://witchculttranslation.com/arc-7/')

  soup = BeautifulSoup(page.content, 'html.parser')

  most_recent_post = soup.find_all('h3', 'rpwe-title')[0]

  post_link = most_recent_post.find('a')

  try:
      if 'href' in post_link.attrs:
          latest_chapter_translated_link = post_link.get('href')
  except:
      pass

  title = most_recent_post.text
  await ctx.send(f'Latest translated chapter is {title}, I suppose!\n{latest_chapter_translated_link}')

# add channel
async def commands_add_channel(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels.count_documents(channel_entry, limit = 1) != 0:
        await ctx.send("This text channel is already on the receiver list, in fact!")
        return
  channels.insert_one(channel_entry)
  await ctx.send("This text channel will receive notifications, I suppose!")
  
# remove channel
async def commands_remove_channel(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels.count_documents(channel_entry, limit = 1) == 0:
        await ctx.send("This text channel is not on the receiver list, in fact!")
        return
  channels.find_one_and_delete(channel_entry)
  await ctx.send("This text channel will no longer receive notifications, I suppose!")
  
# task that removes non existing(deleted) channels every 10 seconds
async def tasks_filter_channels(bot):
  for channel in channels.find():
    if not bot.get_channel((channel['id'])):
      channel_entry = {
        'id': channel['id'],
      }
      channels.find_one_and_delete(channel_entry)

# task that checks chapter every 10 seconds
async def tasks_check_chapter(bot):
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
            await (bot.get_channel(int(channel['id']))).send(f'{most_recent_post} has been translated {time_posted}.\n{latest_chapter_translated_link}, I suppose!')
            
# flip command        
async def commands_flip(ctx):
  pipe = [{ '$sample': { 'size': 1 } }]
  flip = list(flips.aggregate(pipeline=pipe))[0]['url']
  await ctx.send(flip)