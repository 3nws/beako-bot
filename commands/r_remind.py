import discord
import asyncio

from datetime import datetime

async def commands_remind(ctx, time, unit, reminder):
    embed = discord.Embed(color=discord.Colour.random(), timestamp=datetime.utcnow())
    if (unit is None):
        unit = time[-1]
        time = time[:-1]
    if (len(unit) > 1 or time[-1].isalpha() and len(unit) == 1):
        reminder = unit
        unit = time[-1]
        time = time[:-1]
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
        embed.add_field(name='Warning', value="What is this in fact?")
    elif seconds > 7776000:
        embed.add_field(name='Warning', value="We might not survive long enough to do this, in fact!")
    else:
        if reminder=='':
          await ctx.send(f"I'll ping you in {counter}, I suppose!")
        else:
          await ctx.send(f"I'll ping you in {counter} about '{reminder}', I suppose!")
        await asyncio.sleep(seconds)
        if reminder=='':
          await ctx.send(f"Hey {ctx.author.mention}, what up, in fact!")
        else:
          await ctx.send(f"Hey {ctx.author.mention}, what up, in fact! You asked me to remind you about '{reminder}' {counter} ago, I suppose!")
        return
    await ctx.send(embed=embed)