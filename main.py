import discord
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord.ext import tasks, commands
import threading

load_dotenv()
bot = commands.Bot(command_prefix='r.')

channels = [] # keep these on a database later

@bot.command()
async def add_channel(ctx):
    channels.append(ctx.channel.id)
    await ctx.send("This text channel has been added to the list.")

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

    text_channel = bot.get_channel(int(os.getenv('CHANNEL_ID')))

    last_message = (await text_channel.history(limit=1).flatten())[0].content
    last_message_array = last_message.split()
    last_chapter = ""

    if (len(last_message_array)>3):
        for i in range(0, 4):
            last_chapter += last_message_array[i] + " "

    last_chapter = last_chapter.strip()
    if last_chapter != most_recent_post_str:
        for channel in channels:
            await (bot.get_channel(int(channel))).send(f'{most_recent_post} has been translated {time_posted}.\n{latest_chapter_translated_link}')
            
@bot.event
async def on_ready():
    check_chapter.start()
    

bot.run(os.getenv('TOKEN'))
