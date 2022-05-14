import requests
import random
import shutil
import discord
import asyncio
import pymongo
import os

from bs4 import BeautifulSoup

from commands.db.classes.Re_zero import Re_zero
from commands.db.classes.Guya_moe import Guya_moe
from commands.db.classes.Grand_Blue import Grand_Blue
from commands.db.classes.MangaDex import MangaDex
from discord import app_commands
from discord.ext import commands


class DB(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.client = self.bot.get_client()
        
        # channels db
        self.db_channels = self.client.channel_id
        # chapter db
        db_chapter = self.client.chapter
        # chapters data
        self.data_rz = db_chapter.data
        self.data_kaguya = db_chapter.data_kaguya
        self.data_onk = db_chapter.data_onk
        self.data_gb = db_chapter.data_gb
        
        # flip image urls db
        db_flips = self.client.flips
        # flip image urls data
        self.flips = db_flips.data
        
        # avatars url db
        self.db_avatars = self.client.avatars.data
        # avatars path
        self.avatars = os.path.join(os.getcwd(), "avatars")
        
        # channels data
        self.channels_md = db_chapter.data_mangadex
        self.channels_rz = self.db_channels.data
        self.channels_kaguya = self.db_channels.data_kaguya
        self.channels_onk = self.db_channels.data_onk
        self.channels_gb = self.db_channels.data_gb
        
        self.all_channels = [collection['name']
                for collection in self.db_channels.list_collections()]

        self.collection_aliases = {
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
            "grand-blue-dreaming": "gb"
        }
        
        self.tasks_change_avatar.start()
        self.tasks_filter_channels.start()
        self.tasks_check_chapter.start()
        
    
    # flip command
    @app_commands.command(name="flip")
    async def commands_flip(self, i: discord.Interaction):
        pipe = [{"$sample": {"size": 1}}]
        flip = list(self.flips.aggregate(pipeline=pipe))[0]["url"]
        await i.response.send_message(flip)
    
    
    async def send_messages(self, bot, channels, title, data, db_rec, anchor):
        if db_rec["title"] != title:
            data.find_one_and_update(
                {"title": str(db_rec["title"])}, {"$set": {"title": title}}
            )
            for channel in channels.find():
                if bot.get_channel((channel["id"])):
                    try:
                        await (bot.get_channel(int(channel["id"]))).send(
                            f"'{title}' has been translated.\n{anchor}, I suppose!"
                        )
                    except Exception as e:
                        print(
                            f"The channel with id {channel['id']} is private, I suppose!")
    
    # task that checks chapter every 60 seconds
    @discord.ext.tasks.loop(seconds=10)
    async def tasks_check_chapter(self):
        try:
            # for re zero
            rz = Re_zero(self.rz_url)

            scrapes = await rz.scrape()
            most_recent_post_str = scrapes[0]
            latest_chapter_translated_link = scrapes[1]

            last_chapter = self.data_rz.find_one()

            await self.send_messages(
                self.bot,
                self.channels_rz,
                most_recent_post_str,
                self.data_rz,
                last_chapter,
                latest_chapter_translated_link,
            )

            # for kaguya-sama
            kaguya = Guya_moe(self.kaguya_url)

            scrapes = await kaguya.scrape()
            most_recent_post_str = scrapes[0]
            latest_chapter_translated_link = scrapes[1]

            last_chapter = self.data_kaguya.find_one()

            await self.send_messages(
                self.bot,
                self.channels_kaguya,
                most_recent_post_str,
                self.data_kaguya,
                last_chapter,
                latest_chapter_translated_link,
            )

            # for oshi no ko
            onk = Guya_moe(self.onk_url)

            scrapes = await onk.scrape()
            most_recent_post_str = scrapes[0]
            latest_chapter_translated_link = scrapes[1]

            last_chapter = self.data_onk.find_one()

            await self.send_messages(
                self.bot,
                self.channels_onk,
                most_recent_post_str,
                self.data_onk,
                last_chapter,
                latest_chapter_translated_link,
            )

            # for grand blue
            gb = Grand_Blue(self.gb_url)

            scrapes = await gb.scrape()
            most_recent_post_str = scrapes[0]
            latest_chapter_translated_link = scrapes[1]

            last_chapter = self.data_gb.find_one()

            await self.send_messages(
                self.bot,
                self.channels_gb,
                most_recent_post_str,
                self.data_gb,
                last_chapter,
                latest_chapter_translated_link,
            )

            # for mangadex
            md = MangaDex()
            records_exist = self.channels_md.find()
            if records_exist:
                for record in records_exist:
                    mangas_on_channel = (record)['mangas']
                    mangas_dict = eval(mangas_on_channel)
                    for manga_id in mangas_dict:
                        chapter = mangas_dict[manga_id]
                        chapter_response = await md.get_latest(manga_id)
                        title_response = chapter_response.get_title()
                        latest = title_response[0]
                        is_title = title_response[1]
                        chapter_link = chapter_response.get_link()
                        if latest != chapter:
                            mangas_dict.update({f"{manga_id}": str(latest)})
                            new_doc = self.channels_md.find_one_and_update(
                                {'channel_id': str(record['channel_id'])},
                                {
                                    '$set': {
                                        'mangas': str(mangas_dict)
                                    }
                                },
                                return_document=pymongo.ReturnDocument.AFTER
                            )
                            channel = int(record['channel_id'])
                            chp_title = await md.get_manga_title(manga_id)
                            scanlation_group = await md.get_scanlation_group(chapter_response.scanlation)
                            embed = discord.Embed(
                                color=discord.Colour.random(),
                                title=str(latest),
                            )
                            directions = ['⬅️', '➡️']
                            num_of_pages = len(chapter_response.images)
                            if num_of_pages==0:
                                if is_title:
                                    msg = await self.bot.get_channel(channel).send(f"'{chp_title} - {latest}' has been translated, I suppose \n{chapter_link}")
                                else:
                                    msg = await self.bot.get_channel(channel).send(f"A new chapter of '{chp_title}' has been translated, I suppose \n{chapter_link}")
                                return
                            current_page = 0
                            embed.set_footer(text=(f"Page {current_page+1}/{num_of_pages}. Translated by " + scanlation_group['data']['attributes']['name']))
                            embed.set_image(
                                url=chapter_response.images[current_page])
                            if is_title:
                                msg = await self.bot.get_channel(channel).send(f"'{chp_title} - {latest}' has been translated, I suppose \n{chapter_link}", embed=embed)
                            else:
                                msg = await self.bot.get_channel(channel).send(f"A new chapter of '{chp_title}' has been translated, I suppose \n{chapter_link}", embed=embed)
                                
                            await msg.add_reaction(directions[0])
                            await msg.add_reaction(directions[1])
                            def check(reaction, user):
                                return reaction.message == msg and not user.bot

                            time_out = None
                            while True:
                                try:
                                    reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=time_out)
                                    if str(reaction.emoji) == directions[0]:
                                        current_page -= 1 if current_page > 0 else 0
                                        time_out = 180.0
                                    elif str(reaction.emoji) == directions[1]:
                                        if current_page < num_of_pages:
                                            current_page += 1
                                            time_out = 180.0
                                            if current_page==num_of_pages:
                                                await msg.clear_reactions()
                                                await msg.reply("I assume you've finished reading, in fact!")
                                                break
                                    new_embed = discord.Embed(
                                        color=discord.Colour.random(),
                                        title=str(latest),
                                    )
                                    new_embed.set_footer(
                                        text=(
                                            f"Page {current_page+1}/{num_of_pages}. Translated by " +
                                            scanlation_group['data']['attributes']['name']))
                                    new_embed.set_image(
                                        url=chapter_response.images[current_page])
                                    await msg.edit(embed=new_embed)
                                    await reaction.remove(user)
                                except asyncio.TimeoutError:
                                    await msg.clear_reactions()
                                    await msg.reply("You are not even reading! I'm done, in fact!")
                                    break

        except Exception as e:
            print(e)
            
        
    async def last_chapter(self, bot, series, channel, i):
        series = self.aliases[series] if series in self.aliases else series
        if series == "rz":
            await i.response.send_message(await Re_zero(self.rz_url).latest_chapter())
        elif series == "kaguya":
            await i.response.send_message(await Guya_moe(self.kaguya_url).latest_chapter())
        elif series == "onk":
            await i.response.send_message(await Guya_moe(self.onk_url).latest_chapter())
        elif series == "gb":
            await i.response.send_message(await Grand_Blue(self.gb_url).latest_chapter())
        else:
            md = MangaDex()
            search = (await md.search(series, 1))[-1][0]
            chapter_response = await md.get_latest(search)
            chp_title = await md.get_manga_title(search)
            scanlation_group = await md.get_scanlation_group(chapter_response.scanlation)
            title_response = chapter_response.get_title()
            latest = title_response[0]
            is_title = title_response[1]
            chapter_link = chapter_response.get_link()
            embed = discord.Embed(
                color=discord.Colour.random(),
                title=str(latest),
            )
            directions = ['⬅️', '➡️']
            num_of_pages = len(chapter_response.images)
            if num_of_pages==0:
                if is_title:
                    await i.response.send_message(f"'{chp_title} - {latest}' has been translated, I suppose \n{chapter_link}")
                else:
                    await i.response.send_message(f"A new chapter of '{chp_title}' has been translated, I suppose \n{chapter_link}")
                return
            current_page = 0
            embed.set_footer(text=(f"Page {current_page+1}/{num_of_pages}. Translated by " + scanlation_group['data']['attributes']['name']))
            embed.set_image(
                url=chapter_response.images[current_page])
            await i.response.send_message("Read away, I suppose!")
            if is_title:
                msg = await self.bot.get_channel(channel).send(f"'{chp_title} - {latest}' has been translated, I suppose \n{chapter_link}", embed=embed)
            else:
                msg = await self.bot.get_channel(channel).send(f"A new chapter of '{chp_title}' has been translated, I suppose \n{chapter_link}", embed=embed)
                
            await msg.add_reaction(directions[0])
            await msg.add_reaction(directions[1])
            def check(reaction, user):
                return reaction.message == msg and not user.bot

            time_out = None
            while True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=time_out)
                    if str(reaction.emoji) == directions[0]:
                        current_page -= 1 if current_page > 0 else 0
                        time_out = 180.0
                    elif str(reaction.emoji) == directions[1]:
                        if current_page < num_of_pages:
                            current_page += 1
                            time_out = 180.0
                            if current_page==num_of_pages:
                                await msg.clear_reactions()
                                await msg.reply("I assume you've finished reading, in fact!")
                                break
                    new_embed = discord.Embed(
                        color=discord.Colour.random(),
                        title=str(latest),
                    )
                    new_embed.set_footer(
                        text=(
                            f"Page {current_page+1}/{num_of_pages}. Translated by " +
                            scanlation_group['data']['attributes']['name']))
                    new_embed.set_image(
                                url=chapter_response.images[current_page])
                    await msg.edit(embed=new_embed)
                    await reaction.remove(user)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    await msg.reply("You are not even reading! I'm done, in fact!")
                    break
                
        
    def select_random_image_path(self):
        return os.path.join(self.avatars, random.choice(os.listdir(self.avatars)))
    
    
    # sends the latest english translated chapter
    @app_commands.command(name="last")
    async def commands_latest_chapter(self, i: discord.Interaction, series: str=""):
        if series == "":
            message = "What series do you want to know about, in fact!"
        else:
            return await self.last_chapter(self.bot, series, i.channel_id, i)

        await i.response.send_message(message)


    # send manga info
    @app_commands.command(name="manga")
    async def commands_get_manga_info(self, i: discord.Interaction, series: str):
        md = MangaDex()
        embed = await md.get_info(series)
        await i.channel.send(embed=embed)
        
    
    # add the channel to the receiver list
    @app_commands.command(name="add")
    async def commands_add_channel(self, i: discord.Interaction, series: str):
        md = MangaDex()
        channel_entry = {
            "id": i.channel_id,
        }
        series = self.aliases[series] if series in self.aliases else series
        success_msg = "This text channel will receive notifications, I suppose!"
        failure_msg = "This text channel is already on the receiver list, in fact!"
        is_in_list = self.channels_rz.count_documents(channel_entry, limit=1) != 0
        is_in_kaguya_list = self.channels_kaguya.count_documents(
            channel_entry, limit=1) != 0
        is_in_onk_list = self.channels_onk.count_documents(channel_entry, limit=1) != 0
        is_in_gb_list = self.channels_gb.count_documents(channel_entry, limit=1) != 0
        if series == "rz":
            if not is_in_list:
                self.channels_rz.insert_one(channel_entry)
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "kaguya":
            if not is_in_kaguya_list:
                self.channels_kaguya.insert_one(channel_entry)
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "onk":
            if not is_in_onk_list:
                self.channels_onk.insert_one(channel_entry)
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "gb":
            if not is_in_gb_list:
                self.channels_gb.insert_one(channel_entry)
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "" or series == " ":
            msg = "To what list do you want to add this channel, in fact?!"
        else:
            md = MangaDex()
            results = await md.search(series, 5)
            msg = results
            
        if isinstance(msg, list):
            emojis = msg[0]
            titles = msg[2]
            manga_ids = msg[3]
            msg = msg[1]
            msg = await i.channel.send(embed=msg)
            await i.response.send_message("Pick a series to follow, I suppose!")
        else:
            return await i.response.send_message(msg)
    
        for j in range(len(manga_ids)):
            await msg.add_reaction(emojis[j])

        def check(reaction, user):
            return user == i.user and reaction.message == msg

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
                channel_exists = True if self.channels_md.find_one(
                    {"channel_id": str(i.channel_id)}) else False
                if not channel_exists:
                    self.channels_md.insert_one({
                        'channel_id': str(i.channel_id),
                        'mangas': '{}',
                    })
                mangas_on_channel = (self.channels_md.find_one(
                    {"channel_id": str(i.channel_id)}))['mangas']
                mangas_dict = eval(mangas_on_channel)
                idx = 0
                for j, emoji in enumerate(emojis):
                    if emoji == str(reaction):
                        idx = j
                        break
                if str(reaction) == emojis[idx]:
                    if manga_ids[idx] not in mangas_dict:
                        chapter_response = await md.get_latest(manga_ids[idx])
                        title_response = chapter_response.get_title()
                        latest = title_response[0]
                        is_title = title_response[1]
                        chapter_link = chapter_response.get_link()
                        mangas_dict.update({f"{manga_ids[idx]}": str(latest)})
                        new_doc = self.channels_md.find_one_and_update(
                            {'channel_id': str(i.channel_id)},
                            {
                                '$set': {
                                    'mangas': str(mangas_dict)
                                }
                            },
                            return_document=pymongo.ReturnDocument.AFTER
                        )
                        await i.channel.send(f"This channel will receive notifications on new chapters of {titles[idx]}, I suppose!")
                    else:
                        await i.channel.send(f"This channel is already on the receiver list for the new chapters of {titles[idx]}, I suppose!")
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.reply("I'm not accepting any follow requests anymore, in fact!")
                break



    # remove the channel from the receiver list
    @app_commands.command(name="remove")
    async def commands_remove_channel(self, i: discord.Interaction, series: str=""):
        md = MangaDex()
        channel_entry = {
            "id": i.channel_id,
        }
        series = self.aliases[series] if series in self.aliases else series
        success_msg = "This text channel will no longer receive notifications, I suppose!"
        failure_msg = "This text channel is not on the receiver list, in fact!"
        is_in_list = self.channels_rz.count_documents(channel_entry, limit=1) != 0
        is_in_kaguya_list = self.channels_kaguya.count_documents(
            channel_entry, limit=1) != 0
        is_in_onk_list = self.channels_onk.count_documents(channel_entry, limit=1) != 0
        is_in_gb_list = self.channels_gb.count_documents(channel_entry, limit=1) != 0
        if series == "rz":
            if is_in_list:
                self.channels_rz.find_one_and_delete(channel_entry)
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "kaguya":
            if is_in_kaguya_list:
                self.channels_kaguya.find_one_and_delete(channel_entry)
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "onk":
            if is_in_onk_list:
                self.channels_onk.find_one_and_delete(channel_entry)
                msg = success_msg
            else:
                msg = failure_msg
        elif series == "gb":
            if is_in_gb_list:
                self.channels_gb.find_one_and_delete(channel_entry)
                msg = success_msg
            else:
                msg = failure_msg
        else:
            channel_exists = True if self.channels_md.find_one(
                {"channel_id": str(i.channel_id)}) else False
            if not channel_exists:
                msg = "This channel is not on any receiver list, in fact!"

            mangas_on_channel = (self.channels_md.find_one(
                {"channel_id": str(i.channel_id)}))['mangas']
            mangas_dict = eval(mangas_on_channel)

            embed = discord.Embed(
                title=f"Pick one of the series you wish to unfollow, I suppose!" if len(
                    mangas_dict) > 0 else "This channel is not following any series, in fact!\n Use `/add <manga_title>` to pick some series to start, I suppose!",
                color=discord.Colour.random(),
            )

            titles = []
            manga_ids = []
            emojis = md.emojis
            for j, rs in enumerate(mangas_dict):
                manga_ids.append(rs)
                title = await md.get_manga_title(rs)
                titles.append(title)
                title += f' {emojis[j]}'
                embed.add_field(name=title, value='\u200b', inline=False)

            msg = [embed, manga_ids, titles, emojis]

        if isinstance(msg, list):
            emojis = msg[3]
            manga_ids = msg[1]
            titles = msg[2]
            msg = msg[0]
            msg = await i.channel.send(embed=msg)
            await i.response.send_message("Pick a series to unfollow , in fact!")
        else:
            return await i.response.send_message(msg)
        for j in range(len(manga_ids)):
            await msg.add_reaction(emojis[j])

        def check(reaction, user):
            return user == i.user and reaction.message == msg

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
                mangas_on_channel = (self.channels_md.find_one(
                    {"channel_id": str(i.channel_id)}))['mangas']
                mangas_dict = eval(mangas_on_channel)
                idx = 0
                for j, emoji in enumerate(emojis):
                    if emoji == str(reaction):
                        idx = j
                        break
                if str(reaction) == emojis[idx]:
                    if manga_ids[idx] in mangas_dict:
                        mangas_dict.pop(manga_ids[idx])
                        new_doc = self.channels_md.find_one_and_update(
                            {'channel_id': str(i.channel_id)},
                            {
                                '$set': {
                                    'mangas': str(mangas_dict)
                                }
                            },
                            return_document=pymongo.ReturnDocument.AFTER
                        )
                        title = titles[idx]
                        await i.channel.send(f"This channel will no longer receive notifications on new chapters of {title}, I suppose!")
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.reply("I'm not accepting any unfollow requests anymore, in fact!")
                break
    
    # task sets a random avatar every day
    @discord.ext.tasks.loop(hours=24)
    async def tasks_change_avatar(self):
        try:
            for image_record in self.db_avatars.find():
                url = image_record["url"]
                file_name = os.path.join(
                    os.path.join(os.getcwd(), "avatars"), url.split("/")[-1]
                )
                res = requests.get(url, stream=True)

                if res.status_code == 200:
                    file_exists = os.path.exists(file_name)
                    if not file_exists:
                        with open(file_name, "wb") as f:
                            shutil.copyfileobj(res.raw, f)
                        print("Image successfully downloaded: ", file_name)
                    else:
                        print("This image already exists!")
                else:
                    print("Image Couldn't be retrieved")

            file = open(self.select_random_image_path(), "rb")
            print(file)
            new_avatar = file.read()
            await self.bot.wait_until_ready()
            await self.bot.user.edit(avatar=new_avatar)
            print("Avatar changed successfully!")
        except Exception as e:
            print(e)


    # task that removes non existing(deleted) channels every 10 seconds
    @discord.ext.tasks.loop(seconds=10)
    async def tasks_filter_channels(self):
        for channel in self.channels_rz.find():
            if not self.bot.get_channel((channel["id"])):
                channel_entry = {
                    "id": channel["id"],
                }
                self.channels_rz.find_one_and_delete(channel_entry)
        for channel in self.channels_kaguya.find():
            if not self.bot.get_channel((channel["id"])):
                channel_entry = {
                    "id": channel["id"],
                }
                self.channels_kaguya.find_one_and_delete(channel_entry)
        for channel in self.channels_onk.find():
            if not self.bot.get_channel((channel["id"])):
                channel_entry = {
                    "id": channel["id"],
                }
                self.channels_onk.find_one_and_delete(channel_entry)
        for channel in self.channels_gb.find():
            if not self.bot.get_channel((channel["id"])):
                channel_entry = {
                    "id": channel["id"],
                }
                self.channels_gb.find_one_and_delete(channel_entry)
        for channel in self.channels_md.find():
            if not self.bot.get_channel((channel["channel_id"])):
                channel_entry = {
                    "channel_id": channel["channel_id"],
                }
                self.channels_gb.find_one_and_delete(channel_entry)
                
    
    # send a list of followed series of a channel
    @app_commands.command(name="following")
    async def commands_following(self, i: discord.Interaction):
        series = []
        for channels in self.all_channels:
            for channel in self.db_channels[channels].find():
                if self.bot.get_channel(channel['id']) == i.channel:
                    series.append(self.collection_aliases[channels])

        channel_exists = self.channels_md.find_one(
            {"channel_id": str(i.channel_id)}) if self.channels_md.find_one(
            {"channel_id": str(i.channel_id)}) else False
        if channel_exists:
            md = MangaDex()
            mangas_on_channel = (channel_exists)['mangas']
            mangas_dict = eval(mangas_on_channel)
            for manga_id in mangas_dict:
                series.append(await md.get_manga_title(manga_id))

        frame = discord.Embed(
            color=discord.Colour.random(),
            title="This channel is following the series below, in fact!" if len(
                series) > 0 else "This channel is not following any series, I suppose!",
            description="" if len(
                series) > 0 else "Use `/add <series>` to start following a series on this channel, in fact!"
        )
        if len(series) > 0:
            counter = 1
            desc = ""
            for s in series:
                desc += f"**{counter}.** {s}\n"
                counter += 1
            frame.description = desc
        await i.response.send_message(embed=frame)

        
    
async def setup(bot: commands.Bot):
    await bot.add_cog(DB(bot))
