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

# re zero
channels = db_channels.data

# kaguya-sama
channels_kaguya = db_channels.data_kaguya

# oshi no ko
channels_onk = db_channels.data_onk

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

# add channel to re zero notification list
async def commands_add_channel(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels.count_documents(channel_entry, limit = 1) != 0:
        await ctx.send("This text channel is already on the receiver list, in fact!")
        return
  channels.insert_one(channel_entry)
  await ctx.send("This text channel will receive notifications, I suppose!")
  
# add channel to kaguya-sama notification list
async def commands_add_channel_kaguya(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels_kaguya.count_documents(channel_entry, limit = 1) != 0:
        await ctx.send("This text channel is already on the receiver list, in fact!")
        return
  channels_kaguya.insert_one(channel_entry)
  await ctx.send("This text channel will receive notifications, I suppose!")
  
# add channel to oshi no ko notification list
async def commands_add_channel_onk(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels_onk.count_documents(channel_entry, limit = 1) != 0:
        await ctx.send("This text channel is already on the receiver list, in fact!")
        return
  channels_onk.insert_one(channel_entry)
  await ctx.send("This text channel will receive notifications, I suppose!")
  
# remove channel from re zero notification list
async def commands_remove_channel(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels.count_documents(channel_entry, limit = 1) == 0:
        await ctx.send("This text channel is not on the receiver list, in fact!")
        return
  channels.find_one_and_delete(channel_entry)
  await ctx.send("This text channel will no longer receive notifications, I suppose!")
  
# remove channel from kaguya-sama notification list
async def commands_remove_channel_kaguya(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels_kaguya.count_documents(channel_entry, limit = 1) == 0:
        await ctx.send("This text channel is not on the receiver list, in fact!")
        return
  channels_kaguya.find_one_and_delete(channel_entry)
  await ctx.send("This text channel will no longer receive notifications, I suppose!")
  
# remove channel from oshi no ko notification list
async def commands_remove_channel_onk(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels_onk.count_documents(channel_entry, limit = 1) == 0:
        await ctx.send("This text channel is not on the receiver list, in fact!")
        return
  channels_onk.find_one_and_delete(channel_entry)
  await ctx.send("This text channel will no longer receive notifications, I suppose!")
  
# task that removes non existing(deleted) channels every 10 seconds
async def tasks_filter_channels(bot):
  for channel in channels.find():
    if not bot.get_channel((channel['id'])):
      channel_entry = {
        'id': channel['id'],
      }
      channels.find_one_and_delete(channel_entry)
  for channel in channels_kaguya.find():
    if not bot.get_channel((channel['id'])):
      channel_entry = {
        'id': channel['id'],
      }
      channels_kaguya.find_one_and_delete(channel_entry)
  for channel in channels_onk.find():
    if not bot.get_channel((channel['id'])):
      channel_entry = {
        'id': channel['id'],
      }
      channels_onk.find_one_and_delete(channel_entry)

# task that checks chapter every 10 seconds
async def tasks_check_chapter(bot):
  page = requests.get('https://witchculttranslation.com/arc-7/')
  page_kaguya = requests.get('https://guya.moe/read/manga/Kaguya-Wants-To-Be-Confessed-To/')
  page_onk = requests.get('https://guya.moe/read/manga/Oshi-no-Ko/')

  soup = BeautifulSoup(page.content, 'html.parser')
  soup_kaguya = BeautifulSoup(page_kaguya.content, 'html.parser')
  soup_onk = BeautifulSoup(page_onk.content, 'html.parser')

  # web scraping for re zero
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
  
  try:
    if last_chapter['title'] != most_recent_post_str:
        db_chapter.data.find_one_and_update({'title':str(last_chapter['title'])}, { '$set': { "title" : most_recent_post_str} })
        for channel in channels.find():
            if bot.get_channel((channel['id'])):
              await (bot.get_channel(int(channel['id']))).send(f'{most_recent_post} has been translated {time_posted}.\n{latest_chapter_translated_link}, I suppose!')
  except:
      pass
          
  # web scraping for kaguya-sama
  most_recent_kaguya_chapter = soup_kaguya.find_all('td', 'chapter-title')[0]
  
  kaguya_chapter_link = most_recent_kaguya_chapter.find('a')
  
  try:
      if 'href' in post_link.attrs:
        kaguya_chapter_anchor = 'https://guya.moe'
        kaguya_chapter_anchor += kaguya_chapter_link.get('href')
  except:
      pass
  
  most_recent_kaguya_chapter_title = kaguya_chapter_link.text
  
  most_recent_kaguya_chapter_array = most_recent_kaguya_chapter_title.split()
  
  most_recent_kaguya_chapter_str = ""
  
  for i in range(0, len(most_recent_kaguya_chapter_array)):
    most_recent_kaguya_chapter_str += most_recent_kaguya_chapter_array[i] + " "
    
  most_recent_kaguya_chapter_str = most_recent_kaguya_chapter_str.strip()
  
  last_kaguya_chapter = db_chapter.data_kaguya.find_one()
  
  try:
    if last_kaguya_chapter['title'] != most_recent_kaguya_chapter_str:
        db_chapter.data_kaguya.find_one_and_update({'title':str(last_kaguya_chapter['title'])}, { '$set': { "title" : most_recent_kaguya_chapter_str} })
        for channel in channels_kaguya.find():
            if bot.get_channel((channel['id'])):
              await (bot.get_channel(int(channel['id']))).send(f'Chapter {most_recent_kaguya_chapter_str} has been translated.\n{kaguya_chapter_anchor}, I suppose!')
  except:
    pass
            
  # web scraping for oshi no ko
  most_recent_onk_chapter = soup_onk.find_all('td', 'chapter-title')[0]
  
  onk_chapter_link = most_recent_onk_chapter.find('a')
  
  try:
      if 'href' in post_link.attrs:
        onk_chapter_anchor = 'https://guya.moe'
        onk_chapter_anchor += onk_chapter_link.get('href')
  except:
      pass
  
  most_recent_onk_chapter_title = onk_chapter_link.text
  
  most_recent_onk_chapter_array = most_recent_onk_chapter_title.split()
  
  most_recent_onk_chapter_str = ""
  
  for i in range(0, len(most_recent_onk_chapter_array)):
    most_recent_onk_chapter_str += most_recent_onk_chapter_array[i] + " "
    
  most_recent_onk_chapter_str = most_recent_onk_chapter_str.strip()
  
  last_onk_chapter = db_chapter.data_onk.find_one()
  
  try:
    if last_onk_chapter['title'] != most_recent_onk_chapter_str:
        db_chapter.data_onk.find_one_and_update({'title':str(last_onk_chapter['title'])}, { '$set': { "title" : most_recent_onk_chapter_str} })
        for channel in channels_onk.find():
            if bot.get_channel((channel['id'])):
              await (bot.get_channel(int(channel['id']))).send(f'Chapter {most_recent_onk_chapter_str} has been translated.\n{onk_chapter_anchor}, I suppose!')
  except:
      pass
  
            
# flip command        
async def commands_flip(ctx):
  pipe = [{ '$sample': { 'size': 1 } }]
  flip = list(flips.aggregate(pipeline=pipe))[0]['url']
  await ctx.send(flip)