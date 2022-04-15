import discord
import asyncio

from datetime import datetime
from datetime import timedelta
from discord.ext import commands

class Timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # reminds the user about anything after specified time
    @commands.command(case_insensitive=True, aliases=["remindme", "remind_me"])
    async def remind(self, ctx, time, unit=None, *, reminder=""):
        embed = discord.Embed(color=discord.Colour.random(),
                            timestamp=datetime.utcnow())
        if (unit is None):
            unit = time[-1]
            time = time[:-1]
        if (len(unit) > 1 or time[-1].isalpha() and len(unit) == 1):
            reminder = unit
            unit = time[-1]
            time = time[:-1]
        seconds = 0
        if unit.lower().endswith("d"):
            seconds += int(float(time)) * 60 * 60 * 24
            counter = f"{time} days" if int(float(time)) != 1 else f"{time} day"
        if unit.lower().endswith("h"):
            seconds += int(float(time)) * 60 * 60
            counter = f"{time} hours" if int(float(time)) != 1 else f"{time} hour"
        elif unit.lower().endswith("m"):
            seconds += int(float(time) * 60)
            counter = f"{time} minutes" if int(
                float(time)) != 1 else f"{time} minute"
        elif unit.lower().endswith("s"):
            seconds += int(float(time))
            counter = f"{time} seconds" if int(
                float(time)) != 1 else f"{time} second"
        if seconds == 0:
            embed.add_field(name='Warning', value="What is this, in fact?!")
        elif seconds > 7776000:
            embed.add_field(
                name='Warning', value="We might not survive long enough to do this, in fact! Well, not you, I suppose!")
        else:
            if reminder == '':
                await ctx.send(f"I'll ping you in {counter}, I suppose!")
            else:
                await ctx.send(f"I'll ping you in {counter} about '{reminder}', I suppose!")
            await asyncio.sleep(seconds)
            if reminder == '':
                await ctx.send(f"Hey {ctx.author.mention}, what up, in fact!")
            else:
                await ctx.send(f"Hey {ctx.author.mention}, what up, in fact! You asked me to remind you about '{reminder}' {counter} ago, I suppose!")
            return
        await ctx.send(embed=embed)


    # sets an alarm for the user
    @commands.command()
    async def alarm(self, ctx, time="", *, reminder=""):
        try:
            embed = discord.Embed(color=discord.Colour.random(),
                                timestamp=datetime.utcnow())

            splitter = ":" if ":" in time else "."

            hour_now = datetime.now().hour
            minute_now = datetime.now().minute
            alarm_hour = int(time.split(splitter)[0])
            alarm_minute = int(time.split(splitter)[1])
            alarm = timedelta(hours=alarm_hour, minutes=alarm_minute)
            now = timedelta(hours=hour_now, minutes=minute_now)
            time_left = int((alarm-now).total_seconds())

            if time_left <= 0:
                embed.add_field(
                    name='Warning', value="That's not how this works, in fact?!")
            elif time_left > 7776000:
                embed.add_field(
                    name='Warning', value="We might not survive long enough to do this, in fact! Well, not you, I suppose!")
            else:
                if reminder == '':
                    await ctx.send(f"Your Betty alarm is set for {time}, I suppose!")
                else:
                    await ctx.send(f"Your Betty alarm is set for {time} about '{reminder}', I suppose!")
                await asyncio.sleep(time_left)
                if reminder == '':
                    await ctx.send(f"Hey {ctx.author.mention}, what up, in fact!")
                else:
                    await ctx.send(f"Hey {ctx.author.mention}, what up, in fact! This is your Betty alarm for '{reminder}', I suppose!")
                return
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong, in fact! Check the time format, I suppose!")

async def setup(bot):
    await bot.add_cog(Timer(bot))