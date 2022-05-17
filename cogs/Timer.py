import discord
import asyncio
import aiohttp
import json

from datetime import datetime
from datetime import timedelta
from discord import app_commands
from discord.ext import commands
from typing import List


class Timer(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cities_list = []
        self.is_synced = False
        self.sync_url = "https://www.timeapi.io/api/TimeZone/AvailableTimeZones"
        self.base_url = "https://www.timeapi.io/api/Time/current/zone?timeZone="
        self.months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        
    async def sync(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.sync_url) as r:
                if r.status == 200:
                    response = await r.read()
                    self.cities_list = json.loads(response)
                    self.is_synced = True
                else:
                    print("timeapi down!")
                    
    @commands.command()
    @commands.is_owner()
    async def sync_cities(self, ctx):
        try:
            await self.sync()
            await ctx.send("Cities synced, I suppose!")
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong, I suppose!")

    # reminds the user about anything after specified time
    @app_commands.command(name="remind")
    async def remind(self, i: discord.Interaction, time:str, unit:str=None, *, reminder:str=""):
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
            counter = f"{time} days" if int(
                float(time)) != 1 else f"{time} day"
        if unit.lower().endswith("h"):
            seconds += int(float(time)) * 60 * 60
            counter = f"{time} hours" if int(
                float(time)) != 1 else f"{time} hour"
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
                await i.response.send_message(f"I'll ping you in {counter}, I suppose!")
            else:
                await i.response.send_message(f"I'll ping you in {counter} about '{reminder}', I suppose!")
            await asyncio.sleep(seconds)
            if reminder == '':
                await i.channel.send(f"Hey {i.user.mention}, what up, in fact!")
            else:
                await i.channel.send(f"Hey {i.user.mention}, what up, in fact! You asked me to remind you about '{reminder}' {counter} ago, I suppose!")
            return
        await i.response.send_message(embed=embed)

    # sets an alarm for the user
    @app_commands.command(name="alarm")
    async def alarm(self, i: discord.Interaction, time:str="", *, reminder:str=""):
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
            time_left = int((alarm - now).total_seconds())

            if time_left <= 0:
                embed.add_field(
                    name='Warning', value="That's not how this works, in fact?!")
            elif time_left > 7776000:
                embed.add_field(
                    name='Warning', value="We might not survive long enough to do this, in fact! Well, not you, I suppose!")
            else:
                if reminder == '':
                    await i.response.send_message(f"Your Betty alarm is set for {time}, I suppose!")
                else:
                    await i.response.send_message(f"Your Betty alarm is set for {time} about '{reminder}', I suppose!")
                await asyncio.sleep(time_left)
                if reminder == '':
                    await i.channel.send(f"Hey {i.user.mention}, what up, in fact!")
                else:
                    await i.channel.send(f"Hey {i.user.mention}, what up, in fact! This is your Betty alarm for '{reminder}', I suppose!")
                return
            await i.response.send_message(embed=embed)
        except Exception as e:
            print(e)
            await i.response.send_message("Something went wrong, in fact! Check the time format, I suppose!")

    async def city_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        if not self.is_synced:
            await self.sync()
        return [
            app_commands.Choice(name=city, value=city)
            for city in self.cities_list if current.lower() in city.lower()
        ][:25]
    # gets the time at the specified city/timezone
    @app_commands.command(name="time")
    @app_commands.autocomplete(city=city_autocomplete)
    async def get_time(self, i: discord.Interaction, city:str):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url+city) as r:
                if r.status == 200:
                    response = await r.read()
                    time_json = json.loads(response)
                else:
                    print("timeapi down!")
        date = time_json['date'].split('/')
        date[0], date[1] = date[1], date[0]
        month = self.months[int(date[1])-1]
        day = date[0]
        year = date[2]
        date = "/".join(date)
        time = time_json['time'] + " - " + date + " - " + time_json['dayOfWeek']
        time = time_json['dayOfWeek'] + ", " + month + " " + day + ", " + year + " " + time_json['time']
        desc = f"It's {time} in {city}, I suppose!"
        embed = discord.Embed(
            color=discord.Colour.random(),
            title=f"{city}",
            description=f"{desc}",
        )
        await i.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Timer(bot))
