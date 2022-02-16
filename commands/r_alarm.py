import discord
import asyncio

from datetime import datetime
from datetime import timedelta

async def commands_alarm(ctx, time, reminder):
    try:
        embed = discord.Embed(color=discord.Colour.random(), timestamp=datetime.utcnow())

        splitter = ":" if ":" in time else "."

        hour_now = datetime.now().hour
        minute_now = datetime.now().minute
        alarm_hour = int(time.split(splitter)[0])
        alarm_minute = int(time.split(splitter)[1])
        alarm = timedelta(hours=alarm_hour, minutes=alarm_minute)
        now = timedelta(hours=hour_now, minutes=minute_now)
        time_left = int((alarm-now).total_seconds())

        if time_left <= 0:
            embed.add_field(name='Warning', value="That's not how this works, in fact?!")
        elif time_left > 7776000:
            embed.add_field(name='Warning', value="We might not survive long enough to do this, in fact! Well, not you, I suppose!")
        else:
            if reminder=='':
              await ctx.send(f"Your Betty alarm is set for {time}, I suppose!")
            else:
              await ctx.send(f"Your Betty alarm is set for {time} about '{reminder}', I suppose!")
            await asyncio.sleep(time_left)
            if reminder=='':
              await ctx.send(f"Hey {ctx.author.mention}, what up, in fact!")
            else:
              await ctx.send(f"Hey {ctx.author.mention}, what up, in fact! This is your Betty alarm for '{reminder}', I suppose!")
            return
        await ctx.send(embed=embed)
    except Exception as e:
        print(e)
        await ctx.send("Something went wrong, in fact! Check the time format, I suppose!")