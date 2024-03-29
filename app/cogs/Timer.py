import discord
import asyncio
import json

from datetime import datetime
from datetime import timedelta
from discord import app_commands
from discord.ext import commands
from typing import List, Literal, Optional
from aiohttp import ClientSession

from Bot import Bot


class Timer(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.cities_list = []
        self.is_synced = False
        self.sync_url = "https://www.timeapi.io/api/TimeZone/AvailableTimeZones"
        self.base_url = "https://www.timeapi.io/api/Time/current/zone?timeZone="
        self.months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

    async def sync(self):
        """Syncs the timezones information."""
        session: ClientSession = self.bot.session
        async with session.get(self.sync_url) as r:
            if r.status == 200:
                response = await r.read()
                self.cities_list = json.loads(response)
                self.is_synced = True
            else:
                print("timeapi down!")

    async def cog_load(self) -> None:
        try:
            await self.sync()
        except Exception as e:
            print(e)

    @app_commands.command(name="remind")
    @app_commands.describe(
        time="After how long should I ping you, in fact?!",
        unit="Seconds? Hours? Cows? Give me a unit, in fact! You can concatenate this with the previous argument, I suppose!",
        reminder="What is this timer about, in fact?!",
    )
    async def remind(
        self,
        i: discord.Interaction,
        time: str,
        unit: Optional[Literal["s", "m", "h", "d"]],
        *,
        reminder: Optional[str],
    ):
        """Set up a timer to remind you of something with a ping.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            time (str): magnitude of time
            unit (Literal['s', 'h', 'd'], optional): unit of time. Defaults to None.
            reminder (str, optional): what this timer is about. Defaults to "".
        """
        embed = discord.Embed(
            color=discord.Colour.random(), timestamp=datetime.utcnow()
        )
        if unit is None:
            unit = time[-1]  # type: ignore
            time = time[:-1]
        if unit:
            if len(unit) > 1 or time[-1].isalpha() and len(unit) == 1:
                reminder = unit
                unit = time[-1]  # type: ignore
                time = time[:-1]
        seconds = 0
        counter: str = ""
        if unit.lower().endswith("d"):
            seconds += int(float(time)) * 60 * 60 * 24
            counter = f"{time} days" if int(float(time)) != 1 else f"{time} day"
        if unit.lower().endswith("h"):
            seconds += int(float(time)) * 60 * 60
            counter = f"{time} hours" if int(float(time)) != 1 else f"{time} hour"
        elif unit.lower().endswith("m"):
            seconds += int(float(time) * 60)
            counter = f"{time} minutes" if int(float(time)) != 1 else f"{time} minute"
        elif unit.lower().endswith("s"):
            seconds += int(float(time))
            counter = f"{time} seconds" if int(float(time)) != 1 else f"{time} second"
        if seconds == 0:
            embed.add_field(name="Warning", value="What is this, in fact?!")
        elif seconds > 7776000:
            embed.add_field(
                name="Warning",
                value="We might not survive long enough to do this, in fact! Well, not you, I suppose!",
            )
        else:
            counter = f"<t:{int(datetime.now().timestamp())+seconds}:R>"
            if not reminder:
                await i.response.send_message(f"I'll ping you in {counter}, I suppose!")
            else:
                await i.response.send_message(
                    f"I'll ping you in {counter} about '{reminder}', I suppose!"
                )
            await asyncio.sleep(seconds)
            if not reminder:
                await i.channel.send(f"Hey {i.user.mention}, what up, in fact!")  # type: ignore
            else:
                await i.channel.send(  # type: ignore
                    f"Hey {i.user.mention}, what up, in fact! You asked me to remind you about '{reminder}' {counter} ago, I suppose!"
                )
            return await i.delete_original_response()
        await i.response.send_message(embed=embed)

    @app_commands.command(name="alarm")
    @app_commands.describe(
        time="The time you want betty to ping you, in fact! You can use either '.' or ':' to seperate hours and minutes, I suppose!",
        reminder="What is this alarm about, in fact?!",
    )
    async def alarm(
        self, i: discord.Interaction, time: str, *, reminder: Optional[str]
    ):
        """Set up an alarm at given time.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            time (str, optional): hours and minutes seperated by a '.' or a ':'. Defaults to "".
            reminder (str, optional): what this alarm is about. Defaults to "".
        """
        try:
            embed = discord.Embed(
                color=discord.Colour.random(), timestamp=datetime.utcnow()
            )

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
                    name="Warning", value="That's not how this works, in fact?!"
                )
            elif time_left > 7776000:
                embed.add_field(
                    name="Warning",
                    value="We might not survive long enough to do this, in fact! Well, not you, I suppose!",
                )
            else:
                if not reminder:
                    await i.response.send_message(
                        f"Your Betty alarm is set for {time}, I suppose!"
                    )
                else:
                    await i.response.send_message(
                        f"Your Betty alarm is set for {time} about '{reminder}', I suppose!"
                    )
                await asyncio.sleep(time_left)
                if not reminder:
                    await i.channel.send(f"Hey {i.user.mention}, what up, in fact!")  # type: ignore
                else:
                    await i.channel.send(  # type: ignore
                        f"Hey {i.user.mention}, what up, in fact! This is your Betty alarm for '{reminder}', I suppose!"
                    )
                return
            await i.response.send_message(embed=embed)
        except Exception as e:
            print(e)
            await i.response.send_message(
                "Something went wrong, in fact! Check the time format, I suppose!"
            )

    async def timezone_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """An autocomplete function

        Args:
            interaction (discord.Interaction): the interaction that invokes this coroutine
            current (str): whatever the user has typed as the input

        Returns:
            List[app_commands.Choice[str]]: The list of choices matching the input
        """
        if not self.is_synced:
            await self.sync()
        return [
            app_commands.Choice(name=city, value=city)  # type: ignore
            for city in self.cities_list  # type: ignore
            if current.lower() in city.lower()  # type: ignore
        ][:25]

    @app_commands.command(name="time")
    @app_commands.autocomplete(timezone=timezone_autocomplete)
    @app_commands.describe(timezone="The timezone you want to look for, in fact!")
    async def get_time(self, i: discord.Interaction, timezone: str):
        """Get the current time in a timezone.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            timezone (str): timezone to look up
        """
        session: ClientSession = self.bot.session
        async with session.get(self.base_url + timezone) as r:
            if r.status == 200:
                response = await r.read()
                time_json = json.loads(response)
            else:
                print("timeapi down!")
        date = time_json["date"].split("/")  # type: ignore
        date[0], date[1] = date[1], date[0]
        month = self.months[int(date[1]) - 1]  # type: ignore
        day = date[0]  # type: ignore
        year = date[2]  # type: ignore
        date = "/".join(date)  # type: ignore
        time = time_json["time"] + " - " + date + " - " + time_json["dayOfWeek"]  # type: ignore
        time = (  # type: ignore
            time_json["dayOfWeek"]  # type: ignore
            + ", "
            + month
            + " "
            + day
            + ", "
            + year
            + " "
            + time_json["time"]  # type: ignore
        )
        desc = f"It's {time} in {timezone}, I suppose!"
        embed = discord.Embed(
            color=discord.Colour.random(),
            title=f"{timezone}",
            description=f"{desc}",
        )
        await i.response.send_message(embed=embed)


async def setup(bot: Bot):
    await bot.add_cog(Timer(bot))
