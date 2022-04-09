import pymongo
import requests
import os
import random
import shutil
import discord

from dotenv import load_dotenv
from bs4 import BeautifulSoup

from commands.db.classes.Re_zero import Re_zero
from commands.db.classes.Guya_moe import Guya_moe
from commands.db.classes.Grand_Blue import Grand_Blue
from commands.db.classes.MangaDex import MangaDex

load_dotenv()

client = pymongo.MongoClient(os.getenv("DB_URL"))

# channels db
db_channels = client.channel_id

# chapter db
db_chapter = client.chapter

# chapters data
data_rz = db_chapter.data
data_kaguya = db_chapter.data_kaguya
data_onk = db_chapter.data_onk
data_gb = db_chapter.data_gb

# flip image urls db
db_flips = client.flips

# avatars url db
db_avatars = client.avatars.data

# flip image urls data
flips = db_flips.data

# avatars path
avatars = os.path.join(os.getcwd(), "avatars")

# channels data
channels_md = db_chapter.data_mangadex

channels_rz = db_channels.data
channels_kaguya = db_channels.data_kaguya
channels_onk = db_channels.data_onk
channels_gb = db_channels.data_gb

all_channels = [collection['name'] for collection in db_channels.list_collections()]

collection_aliases = {
    "data": "Re:Zero",
    "data_kaguya": "Kaguya-sama",
    "data_onk": "Oshi No Ko",
    "data_gb": "Grand Blue Dreaming",
}

aliases = {
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

rz_url = "https://witchculttranslation.com/arc-7/"
kaguya_url = "https://guya.moe/read/manga/Kaguya-Wants-To-Be-Confessed-To/"
onk_url = "https://guya.moe/read/manga/Oshi-no-Ko/"
gb_url = "https://mangareader.to/grand-blue-dreaming-8/"


def last_chapter(series):
    series = aliases[series] if series in aliases else series
    if series == "rz":
        return Re_zero(rz_url).latest_chapter()
    elif series == "kaguya":
        return Guya_moe(kaguya_url).latest_chapter()
    elif series == "onk":
        return Guya_moe(onk_url).latest_chapter()
    elif series == "gb":
        return Grand_Blue(gb_url).latest_chapter()
    else:
        return "What is that, I suppose?!"


def select_random_image_path():
    return os.path.join(avatars, random.choice(os.listdir(avatars)))


async def send_messages(bot, channels, title, data, db_rec, anchor):
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


# sends the latest english translated chapter


async def commands_latest_chapter(ctx, series):
    if series == "":
        message = "What series do you want to know about, in fact!"
    else:
        message = last_chapter(series)

    await ctx.send(message)


# add the channel to the receiver list


async def commands_add_channel(bot, ctx, id, series):
    channel_entry = {
        "id": id,
    }
    series = aliases[series] if series in aliases else series
    success_msg = "This text channel will receive notifications, I suppose!"
    failure_msg = "This text channel is already on the receiver list, in fact!"
    is_in_list = channels_rz.count_documents(channel_entry, limit=1) != 0
    is_in_kaguya_list = channels_kaguya.count_documents(
        channel_entry, limit=1) != 0
    is_in_onk_list = channels_onk.count_documents(channel_entry, limit=1) != 0
    is_in_gb_list = channels_gb.count_documents(channel_entry, limit=1) != 0
    if series == "rz":
        if not is_in_list:
            channels_rz.insert_one(channel_entry)
            return success_msg
        else:
            return failure_msg
    elif series == "kaguya":
        if not is_in_kaguya_list:
            channels_kaguya.insert_one(channel_entry)
            return success_msg
        else:
            return failure_msg
    elif series == "onk":
        if not is_in_onk_list:
            channels_onk.insert_one(channel_entry)
            return success_msg
        else:
            return failure_msg
    elif series == "gb":
        if not is_in_gb_list:
            channels_gb.insert_one(channel_entry)
            return success_msg
        else:
            return failure_msg
    elif series == "" or series == " ":
        return "To what list do you want to add this channel, in fact?!"
    else:
        md = MangaDex()
        results = md.search(series)
        return results


# remove the channel from the receiver list


async def commands_remove_channel(id, series):
    channel_entry = {
        "id": id,
    }
    series = aliases[series] if series in aliases else series
    success_msg = "This text channel will no longer receive notifications, I suppose!"
    failure_msg = "This text channel is not on the receiver list, in fact!"
    is_in_list = channels_rz.count_documents(channel_entry, limit=1) != 0
    is_in_kaguya_list = channels_kaguya.count_documents(
        channel_entry, limit=1) != 0
    is_in_onk_list = channels_onk.count_documents(channel_entry, limit=1) != 0
    is_in_gb_list = channels_gb.count_documents(channel_entry, limit=1) != 0
    if series == "rz":
        if is_in_list:
            channels_rz.find_one_and_delete(channel_entry)
            return success_msg
        else:
            return failure_msg
    elif series == "kaguya":
        if is_in_kaguya_list:
            channels_kaguya.find_one_and_delete(channel_entry)
            return success_msg
        else:
            return failure_msg
    elif series == "onk":
        if is_in_onk_list:
            channels_onk.find_one_and_delete(channel_entry)
            return success_msg
        else:
            return failure_msg
    elif series == "gb":
        if is_in_gb_list:
            channels_gb.find_one_and_delete(channel_entry)
            return success_msg
        else:
            return failure_msg
    elif series == "" or series == " ":
        return "From what list do you want to remove this channel, in fact?!"
    else:
        return "What is that, I suppose?!"


# task sets a random avatar every day


async def tasks_change_avatar(bot):
    try:
        for image_record in db_avatars.find():
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

        file = open(select_random_image_path(), "rb")
        print(file)
        new_avatar = file.read()
        await bot.user.edit(avatar=new_avatar)
        print("Avatar changed successfully!")
    except Exception as e:
        print(e)


# task that removes non existing(deleted) channels every 10 seconds


async def tasks_filter_channels(bot):
    for channel in channels_rz.find():
        if not bot.get_channel((channel["id"])):
            channel_entry = {
                "id": channel["id"],
            }
            channels_rz.find_one_and_delete(channel_entry)
    for channel in channels_kaguya.find():
        if not bot.get_channel((channel["id"])):
            channel_entry = {
                "id": channel["id"],
            }
            channels_kaguya.find_one_and_delete(channel_entry)
    for channel in channels_onk.find():
        if not bot.get_channel((channel["id"])):
            channel_entry = {
                "id": channel["id"],
            }
            channels_onk.find_one_and_delete(channel_entry)
    for channel in channels_gb.find():
        if not bot.get_channel((channel["id"])):
            channel_entry = {
                "id": channel["id"],
            }
            channels_gb.find_one_and_delete(channel_entry)


# task that checks chapter every 10 seconds


async def tasks_check_chapter(bot):
    # try:
        # for re zero
        # rz = Re_zero(rz_url)

        # most_recent_post_str = rz.scrape()[0]
        # latest_chapter_translated_link = rz.scrape()[1]

        # last_chapter = db_chapter.data.find_one()

        # await send_messages(
        #     bot,
        #     channels_rz,
        #     most_recent_post_str,
        #     data_rz,
        #     last_chapter,
        #     latest_chapter_translated_link,
        # )

        # # for kaguya-sama
        # kaguya = Guya_moe(kaguya_url)

        # most_recent_post_str = kaguya.scrape()[0]
        # latest_chapter_translated_link = kaguya.scrape()[1]

        # last_chapter = db_chapter.data_kaguya.find_one()

        # await send_messages(
        #     bot,
        #     channels_kaguya,
        #     most_recent_post_str,
        #     data_kaguya,
        #     last_chapter,
        #     latest_chapter_translated_link,
        # )

        # # for oshi no ko
        # onk = Guya_moe(onk_url)

        # most_recent_post_str = onk.scrape()[0]
        # latest_chapter_translated_link = onk.scrape()[1]

        # last_chapter = db_chapter.data_onk.find_one()

        # await send_messages(
        #     bot,
        #     channels_onk,
        #     most_recent_post_str,
        #     data_onk,
        #     last_chapter,
        #     latest_chapter_translated_link,
        # )
        
        # # for grand blue
        # gb = Grand_Blue(gb_url)

        # most_recent_post_str = gb.scrape()[0]
        # latest_chapter_translated_link = gb.scrape()[1]

        # last_chapter = db_chapter.data_gb.find_one()

        # await send_messages(
        #     bot,
        #     channels_gb,
        #     most_recent_post_str,
        #     data_gb,
        #     last_chapter,
        #     latest_chapter_translated_link,
        # )
        
        # for mangadex
        md = MangaDex()
        md.get_latest("428ad84a-69c6-426d-8ed4-b423c4929756")
        mangas_on_channel = eval((channels_md.find_one())['mangas'])
        for manga in mangas_on_channel:
            chapter = mangas_on_channel[manga]
            print(manga, chapter)

    # except Exception as e:
    #     print(e)


# flip command
async def commands_flip(ctx):
    pipe = [{"$sample": {"size": 1}}]
    flip = list(flips.aggregate(pipeline=pipe))[0]["url"]
    await ctx.send(flip)


async def commands_following(ctx, bot):
    series = []
    for channels in all_channels:
        for channel in db_channels[channels].find():
            if bot.get_channel(channel['id']) == ctx.channel:
                series.append(collection_aliases[channels])

    frame = discord.Embed(
        color=discord.Colour.random(),
        title="This channel is following the series below, in fact!" if len(series)>0 else "This channel is not following any series, I suppose!",
        description="" if len(
            series) > 0 else "Use `r.add <series>` to start following a series on this channel, in fact!"
    )
    if len(series)>0:
        counter = 1
        desc = ""
        for s in series:
            desc += f"**{counter}.** {s}\n"
            counter += 1
        frame.description = desc
    await ctx.send(embed=frame)
