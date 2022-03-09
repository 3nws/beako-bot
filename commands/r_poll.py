import discord
import asyncio

from datetime import datetime

async def commands_poll(ctx, c1, c2, question):
  embed = discord.Embed(
    color = discord.Colour.random()
  )
  
  embed.add_field(name=f"{question.upper()}", value=f":one: {c1}\n\n:two: {c2}\n")
  embed.set_footer(text=f"Poll created by {ctx.author.nick}", icon_url=ctx.author.avatar_url)
  
  msg = await ctx.send(embed=embed)
  
  emojis = ['1️⃣', '2️⃣']
  
  for emoji in emojis:
        await msg.add_reaction(emoji)
  
  await asyncio.sleep(180)
  
  results = discord.Embed(
    color = discord.Colour.random()
  )
  
  message_1 = await ctx.channel.fetch_message(msg.id)
  
  reactions = {react.emoji: react.count for react in message_1.reactions}
  
  results.add_field(name=f"Results", value=f"{c1}: {reactions[emojis[0]]}\n\n{c2}: {reactions[emojis[1]]}")
  results.set_footer(text=f"For the poll '{question}'", icon_url=ctx.author.avatar_url)
  
  await ctx.send(embed=results)