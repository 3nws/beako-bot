import random
import discord
import os
import json

from ast import literal_eval
from aiohttp import ClientSession
from discord import app_commands
from discord.ext import commands, tasks
from typing import List, Any, Dict, Union, Optional, Tuple, Mapping, cast
from pymongo.collection import Collection
from pymongo.database import Database
from motor.motor_asyncio import AsyncIOMotorClient  # type: ignore

from classes.Re_zero import Re_zero
from classes.Guya_moe import Guya_moe
from classes.Grand_Blue import Grand_Blue
from classes.MangaDex import MangaDex
from classes.Views.Pick import PickView
from classes.Views.Pagination import MangaReader, Source
from Bot import Bot


class DB(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.client = self.bot.client

        # channels db
        self.db_channels: Database[AsyncIOMotorClient] = self.client.channel_id
        # chapter db
        db_chapter: Database[AsyncIOMotorClient] = self.client.chapter  # type: ignore
        # chapters data
        self.data_rz: Collection[Mapping[str, Any]] = db_chapter.data  # type: ignore
        self.data_kaguya: Collection[Mapping[str, Any]] = db_chapter.data_kaguya  # type: ignore
        self.data_onk: Collection[Mapping[str, Any]] = db_chapter.data_onk  # type: ignore
        self.data_gb: Collection[Mapping[str, Any]] = db_chapter.data_gb  # type: ignore

        # flip image urls db
        db_flips: Database[AsyncIOMotorClient] = self.client.flips  # type: ignore
        # flip image urls data
        self.flips_col: Collection[Mapping[str, Any]] = db_flips.data  # type: ignore

        # avatars url db
        self.db_avatars: Database[AsyncIOMotorClient] = self.client.avatars.data
        # avatars path
        self.avatars = os.path.join(os.getcwd(), "avatars")

        # channels data
        self.channels_md: Collection[Mapping[str, Any]] = db_chapter.data_mangadex  # type: ignore
        self.channels_rz: Collection[Mapping[str, Any]] = self.db_channels.data  # type: ignore
        self.channels_kaguya: Collection[
            Mapping[str, Any]
        ] = self.db_channels.data_kaguya  # type: ignore
        self.channels_onk: Collection[Mapping[str, Any]] = self.db_channels.data_onk  # type: ignore
        self.channels_gb: Collection[Mapping[str, Any]] = self.db_channels.data_gb  # type: ignore

        self.collection_aliases: Dict[str, str] = {
            "data": "Re:Zero",
            "data_kaguya": "Kaguya-sama",
            "data_onk": "Oshi No Ko",
            "data_gb": "Grand Blue Dreaming",
        }

        # urls
        self.rz_url = "https://witchculttranslation.com/arc-7/"
        self.kaguya_url = "https://guya.moe/read/manga/Kaguya-Wants-To-Be-Confessed-To/"
        self.onk_url = "https://guya.moe/read/manga/Oshi-no-Ko/"
        self.gb_url = "https://mangareader.to/grand-blue-dreaming-8/"

        self.aliases = {
            "rezero": "rz",
            "re:zero": "rz",
            "guya": "kaguya",
            "kaguya-sama": "kaguya",
            "kaguya_sama": "kaguya",
            "oshi no ko": "onk",
            "oshi": "onk",
            "oshi_no_ko": "onk",
            "grand_blue": "gb",
            "grand blue": "gb",
            "grand-blue": "gb",
            "grand blue dreaming": "gb",
            "grand_blue_dreaming": "gb",
            "grand-blue-dreaming": "gb",
        }

        self.flips: List[Dict[str, str]] = []
        self.avatar_urls: List[str] = []
        self.mangas_list = {}

        self.tasks_change_avatar.start()

    @commands.Cog.listener()
    async def on_ready(self):
        self.tasks_filter_channels.start()
        self.tasks_check_chapter.start()

    async def cog_load(self) -> None:
        self.flips = [flip async for flip in self.flips_col.find()]  # type: ignore

    @app_commands.command(name="flip")
    async def commands_flip(self, i: discord.Interaction):
        """Flip your friends.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
        """
        flip_dict: Dict[str, str] = random.choice(self.flips)
        flip_url: str = flip_dict.get("url", "")
        await i.response.send_message(flip_url)

    async def send_messages(
        self,
        channels: Collection[Mapping[str, Any]],
        title: str,
        data: Collection[Mapping[str, Any]],
        db_rec: Dict[str, str],
        anchor: str,
    ):
        """Sends the notification messages to all the relevant guild channels.

        Args:
            channels (motor.motor_asyncio.AsyncIOMotorCollection): relevant channels collection
            title (str): the scraped or response title to compare with the database
            data (motor.motor_asyncio.AsyncIOMotorCollection): chapter collection of the relevant series to update if necessary
            db_rec (dict): the latest document in the database of the relevant series
            anchor (str): link to the chapter
        """
        if db_rec["title"] != title:
            await data.find_one_and_update(  # type: ignore
                {"title": str(db_rec["title"])}, {"$set": {"title": title}}
            )
            async for channel in channels.find():  # type: ignore
                channel_if_exists = self.bot.get_guild(channel["guild_id"]).get_channel(  # type: ignore
                    (channel["id"])  # type: ignore
                )
                if channel_if_exists:
                    try:
                        await channel_if_exists.send(  # type: ignore
                            f"'{title}' has been translated.\n{anchor}, I suppose!"
                        )
                    except Exception as e:
                        print(
                            f"The channel with id {channel['id']} is private, I suppose!",
                            e,
                        )

    @tasks.loop(seconds=60)
    async def tasks_check_chapter(self):
        """Checks for the newest chapters every minute."""
        try:
            # for re zero
            rz = Re_zero(self.rz_url, self.bot)

            scrapes = await rz.scrape()
            most_recent_post_str = scrapes[0]
            latest_chapter_translated_link = scrapes[1]

            last_chapter: Dict[str, str] = await self.data_rz.find_one()  # type: ignore

            await self.send_messages(
                self.channels_rz,
                most_recent_post_str,
                self.data_rz,
                last_chapter,
                latest_chapter_translated_link,
            )

            # for kaguya-sama
            kaguya = Guya_moe(self.kaguya_url, self.bot)

            scrapes = await kaguya.scrape()
            most_recent_post_str = scrapes[0]
            latest_chapter_translated_link = scrapes[1]

            last_chapter = await self.data_kaguya.find_one()  # type: ignore

            await self.send_messages(
                self.channels_kaguya,
                most_recent_post_str,
                self.data_kaguya,
                last_chapter,
                latest_chapter_translated_link,
            )

            # for oshi no ko
            onk = Guya_moe(self.onk_url, self.bot)

            scrapes = await onk.scrape()
            most_recent_post_str = scrapes[0]
            latest_chapter_translated_link = scrapes[1]

            last_chapter = await self.data_onk.find_one()  # type: ignore

            await self.send_messages(
                self.channels_onk,
                most_recent_post_str,
                self.data_onk,
                last_chapter,
                latest_chapter_translated_link,
            )

            # for grand blue
            gb = Grand_Blue(self.gb_url, self.bot)

            scrapes = await gb.scrape()
            most_recent_post_str = scrapes[0]
            latest_chapter_translated_link = scrapes[1]

            last_chapter = await self.data_gb.find_one()  # type: ignore

            await self.send_messages(
                self.channels_gb,
                most_recent_post_str,
                self.data_gb,
                last_chapter,
                latest_chapter_translated_link,
            )

            # for mangadex
            md = MangaDex(self.bot)
            records_exist: List[
                Mapping[str, Any]
            ] = await self.channels_md.find().to_list(
                None
            )  # type: ignore
            if records_exist:
                for record in records_exist:
                    mangas_on_channel = (record)["mangas"]
                    mangas_dict = literal_eval(mangas_on_channel)
                    for manga_id in mangas_dict:
                        chapter = mangas_dict[manga_id]
                        chapter_response = await md.get_latest(manga_id)
                        title_response = chapter_response.get_title()
                        latest = title_response[0]
                        is_title = title_response[1]
                        chapter_link = chapter_response.get_link()
                        if latest != chapter:
                            mangas_dict.update({f"{manga_id}": str(latest)})
                            await self.channels_md.find_one_and_update(  # type: ignore
                                {
                                    "channel_id": record["channel_id"],
                                    "guild_id": record["guild_id"],
                                },
                                {"$set": {"mangas": str(mangas_dict)}},
                            )
                            channel = record["channel_id"]
                            chp_title = await md.get_manga_title(manga_id)
                            scanlation_group = await md.get_scanlation_group(
                                chapter_response.scanlation
                            )
                            embed = discord.Embed(
                                color=discord.Colour.random(),
                                title=str(latest),
                            )
                            num_of_pages = len(chapter_response.images)
                            if num_of_pages == 0:
                                if is_title:
                                    await self.bot.get_channel(channel).send(  # type: ignore
                                        f"'{chp_title} - {latest}' has been translated, I suppose \n{chapter_link}"
                                    )
                                else:
                                    await self.bot.get_channel(channel).send(  # type: ignore
                                        f"A new chapter of '{chp_title}' has been translated, I suppose \n{chapter_link}"
                                    )
                                continue
                            current_page = 0
                            group: str = scanlation_group["data"]["attributes"]["name"]  # type: ignore
                            embed.set_footer(
                                text=(
                                    f"Page {current_page+1}/{num_of_pages}. Translated by "
                                    + group
                                )
                            )
                            embed.set_image(url=chapter_response.images[current_page])

                            data = chapter_response.images
                            formatter = Source(data, per_page=1)
                            menu = MangaReader(formatter)
                            chnl: Union[
                                discord.abc.GuildChannel,
                                discord.Thread,
                                discord.abc.PrivateChannel,
                            ] = self.bot.get_channel(
                                channel
                            )  # type: ignore

                            if is_title:
                                text, embed = (
                                    f"'{chp_title} - {latest}' has been translated, I suppose \n{chapter_link}",
                                    embed,
                                )
                            else:
                                text, embed = (
                                    f"A new chapter of '{chp_title}' has been translated, I suppose \n{chapter_link}",
                                    embed,
                                )

                            await menu.start(
                                interaction=None,
                                channel=chnl,
                                text=text,
                                embed=embed,
                                group=group,
                            )

        except Exception as e:
            print(e)

    async def last_chapter(self, series: str, i: discord.Interaction) -> None:
        """Sends the latest chapter info or the reader.

        Args:
            series (str): the series to check
            i (discord.Interaction): the interaction that invokes this coroutine
        """
        series = self.aliases[series] if series in self.aliases else series
        if series == "rz":
            await i.response.send_message(
                await Re_zero(self.rz_url, self.bot).latest_chapter()
            )
        elif series == "kaguya":
            await i.response.send_message(
                await Guya_moe(self.kaguya_url, self.bot).latest_chapter()
            )
        elif series == "onk":
            await i.response.send_message(
                await Guya_moe(self.onk_url, self.bot).latest_chapter()
            )
        elif series == "gb":
            await i.response.send_message(
                await Grand_Blue(self.gb_url, self.bot).latest_chapter()
            )
        else:
            md = MangaDex(self.bot)
            search: Optional[List[Any]] = await md.search(series, "1")
            search_query: str = ""
            if search:
                search_query = search[-1][0]
            chapter_response = await md.get_latest(search_query)
            chp_title = await md.get_manga_title(search_query)
            scanlation_group = await md.get_scanlation_group(
                chapter_response.scanlation
            )
            title_response = chapter_response.get_title()
            latest = title_response[0]
            is_title = title_response[1]
            chapter_link = chapter_response.get_link()
            embed = discord.Embed(
                color=discord.Colour.random(),
                title=str(latest),
            )

            num_of_pages = len(chapter_response.images)
            if num_of_pages == 0:
                if is_title:
                    await i.response.send_message(
                        f"'{chp_title} - {latest}' has been translated, I suppose \n{chapter_link}"
                    )
                else:
                    await i.response.send_message(
                        f"A new chapter of '{chp_title}' has been translated, I suppose \n{chapter_link}"
                    )
                return
            current_page = 0
            group: str = scanlation_group["data"]["attributes"]["name"]  # type: ignore
            embed.set_footer(
                text=(f"Page {current_page+1}/{num_of_pages}. Translated by " + group)
            )
            embed.set_image(url=chapter_response.images[current_page])
            await i.response.send_message("Read away, I suppose!")

            data = chapter_response.images
            formatter = Source(data, per_page=1)
            menu = MangaReader(formatter)

            if is_title:
                text, embed = (
                    f"'{chp_title} - {latest}' has been translated, I suppose \n{chapter_link}",
                    embed,
                )
            else:
                text, embed = (
                    f"A new chapter of '{chp_title}' has been translated, I suppose \n{chapter_link}",
                    embed,
                )

            await menu.start(
                interaction=i, channel=i.channel, text=text, embed=embed, group=group
            )

    async def manga_autocomplete(
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
        await self.sync(current)
        return [
            app_commands.Choice(
                name=manga["attributes"]["title"]["en"][:100],  # type: ignore
                value=manga["attributes"]["title"]["en"][:100],  # type: ignore
            )
            for manga in self.mangas_list  # type: ignore
            if "en" in manga["attributes"]["title"].keys()  # type: ignore
            and current.lower() in manga["attributes"]["title"]["en"].lower()  # type: ignore
        ][:25]

    @app_commands.command(name="last")
    @app_commands.autocomplete(series=manga_autocomplete)
    @app_commands.describe(
        series="The series you want to get the latest chapter of, in fact!"
    )
    async def commands_latest_chapter(
        self, i: discord.Interaction, series: Optional[str]
    ):
        """Get the latest chapter of a series.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            series (str, optional): the series to know about. Defaults to "".

        Returns:
            None: None
        """
        if not series:
            message = "What series do you want to know about, in fact!"
        else:
            return await self.last_chapter(series, i)
        await i.response.send_message(message)

    # send manga info
    @app_commands.command(name="manga")
    @app_commands.autocomplete(series=manga_autocomplete)
    @app_commands.describe(
        series="The series you want to get information about, I suppose!"
    )
    async def commands_get_manga_info(self, i: discord.Interaction, series: str):
        """Get info on a manga.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            series (str): the series to know about
        """
        md = MangaDex(self.bot)
        embed = await md.get_info(series)
        if embed:
            await i.response.send_message(embed=embed)

    async def sync(self, query: str):
        """The function called everytime the input on mangadex related autocomplete argument changes.

        Args:
            query (str): query that will be sent to the api
        """
        session: ClientSession = self.bot.session
        async with session.get(
            f"https://api.mangadex.org/manga?limit=25&title={query}&availableTranslatedLanguage%5B%5D=en&order%5BlatestUploadedChapter%5D=desc"
        ) as r:
            if r.status == 200:
                response = await r.read()
                self.mangas_list = json.loads(response)["data"]
            else:
                print("MangaDex down!")

    @app_commands.command(name="add")
    @app_commands.guild_only
    @app_commands.autocomplete(series=manga_autocomplete)
    @app_commands.describe(
        series="The series you want to track in this channel, in fact!"
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def commands_add_channel(self, i: discord.Interaction, series: str):
        """Add a series to track to this channel.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            series (str): the series to add this channel's tracking list
        """
        md = MangaDex(self.bot)
        channel_entry: Dict[str, int] = {  # type: ignore
            "id": i.channel_id,
            "guild_id": i.guild.id,
        }
        series = self.aliases[series] if series in self.aliases else series
        success_msg = "This text channel will receive notifications, I suppose!"
        failure_msg = "This text channel is already on the receiver list, in fact!"
        is_in_list = self.channels_rz.count_documents(channel_entry, limit=1) != 0  # type: ignore
        is_in_kaguya_list = (
            self.channels_kaguya.count_documents(channel_entry, limit=1) != 0  # type: ignore
        )
        is_in_onk_list = self.channels_onk.count_documents(channel_entry, limit=1) != 0  # type: ignore
        is_in_gb_list = self.channels_gb.count_documents(channel_entry, limit=1) != 0  # type: ignore
        if series == "rz":
            if not is_in_list:
                await self.channels_rz.insert_one(channel_entry)  # type: ignore
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "kaguya":
            if not is_in_kaguya_list:
                await self.channels_kaguya.insert_one(channel_entry)  # type: ignore
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "onk":
            if not is_in_onk_list:
                await self.channels_onk.insert_one(channel_entry)  # type: ignore
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "gb":
            if not is_in_gb_list:
                await self.channels_gb.insert_one(channel_entry)  # type: ignore
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "" or series == " ":
            msg = "To what list do you want to add this channel, in fact?!"
        else:
            md = MangaDex(self.bot)
            results = await md.search(series, "5")
            msg = results

        if isinstance(msg, list):
            titles = msg[2]
            manga_ids = msg[3]
            msg = msg[1]
            manga_infos = (titles, manga_ids)
            await i.response.send_message(
                "Pick a series to follow, I suppose!",
                embed=msg,
                view=PickView(i, self.channels_md, manga_infos, self.bot, msg),
            )
        else:
            await i.response.send_message(msg)

    @app_commands.command(name="remove")
    @app_commands.guild_only
    @app_commands.describe(
        series="The series you want to stop tracking in this channel, I suppose!"
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def commands_remove_channel(
        self, i: discord.Interaction, series: Optional[str]
    ):
        """Remove a series this channel is tracking.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
            series (str, optional): the series to remove from this channel's tracking list. Defaults to "".
        """
        md = MangaDex(self.bot)
        channel_entry: Dict[str, int] = {  # type: ignore
            "id": i.channel_id,
            "guild_id": i.guild.id,
        }
        series = self.aliases[series] if series in self.aliases else series
        success_msg = (
            "This text channel will no longer receive notifications, I suppose!"
        )
        failure_msg = "This text channel is not on the receiver list, in fact!"
        is_in_list = self.channels_rz.count_documents(channel_entry, limit=1) != 0  # type: ignore
        is_in_kaguya_list = (
            self.channels_kaguya.count_documents(channel_entry, limit=1) != 0  # type: ignore
        )
        is_in_onk_list = self.channels_onk.count_documents(channel_entry, limit=1) != 0  # type: ignore
        is_in_gb_list = self.channels_gb.count_documents(channel_entry, limit=1) != 0  # type: ignore
        if series == "rz":
            if is_in_list:
                await self.channels_rz.find_one_and_delete(channel_entry)  # type: ignore
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "kaguya":
            if is_in_kaguya_list:
                await self.channels_kaguya.find_one_and_delete(channel_entry)  # type: ignore
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "onk":
            if is_in_onk_list:
                await self.channels_onk.find_one_and_delete(channel_entry)  # type: ignore
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "gb":
            if is_in_gb_list:
                await self.channels_gb.find_one_and_delete(channel_entry)  # type: ignore
                msg = success_msg
            else:
                msg = failure_msg
        else:
            channel_exists: Dict[str, Union[str, int]] = (
                True
                if await self.channels_md.find_one(  # type: ignore
                    {
                        "channel_id": i.channel_id,
                        "guild_id": i.guild.id,
                    }
                )
                else False
            )
            if not channel_exists:
                msg = "This channel is not on any receiver list, in fact!"

            mangas_on_channel: str = (
                await self.channels_md.find_one(  # type: ignore
                    {
                        "channel_id": i.channel_id,
                        "guild_id": i.guild.id,
                    }
                )
            )["mangas"]
            mangas_dict: Dict[str, str] = literal_eval(mangas_on_channel)

            embed = discord.Embed(
                title=f"Pick one of the series you wish to unfollow, I suppose!"
                if len(mangas_dict) > 0
                else "This channel is not following any series, in fact!\n Use `/add <manga_title>` to pick some series to start, I suppose!",
                color=discord.Colour.random(),
            )

            titles: List[str] = []
            manga_ids: List[str] = []
            emojis = md.emojis
            for j, rs in enumerate(mangas_dict):
                manga_ids.append(rs)
                title = await md.get_manga_title(rs)
                if title:
                    titles.append(title)
                    title += f" {emojis[j]}"
                embed.add_field(name=title, value="\u200b", inline=False)

            msg = [embed, manga_ids, titles, emojis]

        if isinstance(msg, list):
            emojis = msg[3]
            manga_ids = msg[1]  # type: ignore
            titles = msg[2]  # type: ignore
            msg = msg[0]
            manga_infos: Tuple[List[str], List[str]] = (titles, manga_ids)
            await i.response.send_message(
                "Pick a series to follow, I suppose!",
                embed=msg,  # type: ignore
                view=PickView(i, self.channels_md, manga_infos, self.bot, msg),  # type: ignore
            )
        else:
            await i.response.send_message(msg)

    @tasks.loop(hours=12)
    async def tasks_change_avatar(self):
        """Task that changes the bot's avatar twice a day."""
        async for image_record in self.db_avatars.find():  # type: ignore
            url: str = image_record["url"]
            if url not in self.avatar_urls:
                self.avatar_urls.append(url)

        url = random.choice(self.avatar_urls)
        session: ClientSession = self.bot.session
        async with session.get(url) as resp:
            if resp.status == 200:
                bytes_image = await resp.read()

        await self.bot.wait_until_ready()
        await self.bot.user.edit(avatar=bytes_image)
        print("Avatar changed successfully!")

    @tasks.loop(seconds=60)
    async def tasks_filter_channels(self):
        """Task that filters out deleted channels from the database every 60 seconds."""
        async for channel in self.channels_rz.find():  # type: ignore
            if (
                self.bot.get_guild(channel["guild_id"]) is None  # type: ignore
                or self.bot.get_guild(channel["guild_id"]).get_channel((channel["id"]))  # type: ignore
                is None
            ):
                channel_entry: Mapping[str, Any] = {
                    "id": channel["id"],
                }
                await self.channels_rz.find_one_and_delete(channel_entry)  # type: ignore
        async for channel in self.channels_kaguya.find():  # type: ignore
            if (
                self.bot.get_guild(channel["guild_id"]) is None  # type: ignore
                or self.bot.get_guild(channel["guild_id"]).get_channel((channel["id"]))  # type: ignore
                is None
            ):
                channel_entry = {
                    "id": channel["id"],
                }
                await self.channels_kaguya.find_one_and_delete(channel_entry)  # type: ignore
        async for channel in self.channels_onk.find():  # type: ignore
            if (
                self.bot.get_guild(channel["guild_id"]) is None  # type: ignore
                or self.bot.get_guild(channel["guild_id"]).get_channel((channel["id"]))  # type: ignore
                is None
            ):
                channel_entry = {
                    "id": channel["id"],
                }
                await self.channels_onk.find_one_and_delete(channel_entry)  # type: ignore
        async for channel in self.channels_gb.find():  # type: ignore
            if (
                self.bot.get_guild(channel["guild_id"]) is None  # type: ignore
                or self.bot.get_guild(channel["guild_id"]).get_channel((channel["id"]))  # type: ignore
                is None
            ):
                channel_entry = {
                    "id": channel["id"],
                }
                await self.channels_gb.find_one_and_delete(channel_entry)  # type: ignore
        async for channel in self.channels_md.find():  # type: ignore
            if (
                self.bot.get_guild(channel["guild_id"]) is None  # type: ignore
                or self.bot.get_guild(channel["guild_id"]).get_channel(  # type: ignore
                    (channel["channel_id"])  # type: ignore
                )
                is None
            ):
                channel_entry = {
                    "channel_id": channel["channel_id"],
                    "guild_id": channel["guild_id"],
                }
                await self.channels_md.find_one_and_delete(channel_entry)  # type: ignore

    @app_commands.command(name="following")
    @app_commands.guild_only
    async def commands_following(self, i: discord.Interaction):
        """Check what series this channel is tracking.

        Args:
            i (discord.Interaction): the interaction that invokes this coroutine
        """
        series: List[str] = []
        all_channels: List[str] = await self.db_channels.list_collection_names()  # type: ignore
        for channels in all_channels:
            async for channel in self.db_channels[channels].find():  # type: ignore
                if self.bot.get_channel(cast(int, channel["id"])) == i.channel:
                    series.append(self.collection_aliases[channels])

        channel_exists: Dict[str, Any] = (
            await self.channels_md.find_one(  # type: ignore
                {
                    "channel_id": i.channel_id,
                    "guild_id": i.guild.id,
                }
            )
            if await self.channels_md.find_one(  # type: ignore
                {
                    "channel_id": i.channel_id,
                    "guild_id": i.guild.id,
                }
            )
            else False
        )
        if channel_exists:
            md = MangaDex(self.bot)
            mangas_on_channel = (channel_exists)["mangas"]
            mangas_dict = literal_eval(mangas_on_channel)
            for manga_id in mangas_dict:
                manga_title = await md.get_manga_title(manga_id)
                if manga_title:
                    series.append(manga_title)

        frame = discord.Embed(
            color=discord.Colour.random(),
            title="This channel is following the series below, in fact!"
            if len(series) > 0
            else "This channel is not following any series, I suppose!",
            description=""
            if len(series) > 0
            else "Use `/add <series>` to start following a series on this channel, in fact!",
        )
        if len(series) > 0:
            counter = 1
            desc = ""
            for s in series:
                desc += f"**{counter}.** {s}\n"
                counter += 1
            frame.description = desc
        await i.response.send_message(embed=frame)


async def setup(bot: Bot):
    await bot.add_cog(DB(bot))
