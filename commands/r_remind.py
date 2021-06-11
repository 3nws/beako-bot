import discord
import asyncio

from datetime import datetime

async def commands_remind(ctx, time, unit, reminder):
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
          await ctx.send(f"Yo {ctx.author.mention}, what up! You asked me to remind you about '{reminder}' {counter} ago.")
        return
    await ctx.send(embed=embed)