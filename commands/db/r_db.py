import pymongo
import os

from dotenv import load_dotenv

load_dotenv()

client = pymongo.MongoClient(os.getenv('DB_URL'))

db_channels = client.channel_id

db_chapter = client.chapter

channels = db_channels.data

# add channel
async def commands_add_channel(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels.count_documents(channel_entry, limit = 1) != 0:
        await ctx.send("This text channel is already on the receiver list!")
        return
  channels.insert_one(channel_entry)
  await ctx.send("This text channel will receive notifications.")
  
# remove channel
async def commands_remove_channel(ctx):
  channel_entry = {
    'id': ctx.channel.id,
  }
  if channels.count_documents(channel_entry, limit = 1) == 0:
        await ctx.send("This text channel is not on the receiver list!")
        return
  channels.find_one_and_delete(channel_entry)
  await ctx.send("This text channel will no longer receive notifications.")