import pymongo
import os
import asyncio

from dotenv import load_dotenv
from commands.db.classes.MangaDex import MangaDex
from pymongo.errors import ConnectionFailure

load_dotenv()

client = pymongo.MongoClient('localhost', 27017)
try:
    client.admin.command('ping')
except ConnectionFailure:
    print("Local not available")
    client = pymongo.MongoClient(os.getenv("DB_URL"))


# chapter db
db_chapter = client.chapter

# channels data
channels_md = db_chapter.data_mangadex


async def commands_remove_channel(bot, i, series_obj):
    md = MangaDex()
    msg = await series_obj.remove_channel(bot, i)
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
            reaction, user = await bot.wait_for('reaction_add', check=check, timeout=60.0)
            mangas_on_channel = (channels_md.find_one(
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
                    new_doc = channels_md.find_one_and_update(
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
