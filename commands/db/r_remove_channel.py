import pymongo
import os
import asyncio

from dotenv import load_dotenv
from commands.db.classes.MangaDex import MangaDex

load_dotenv()

client = pymongo.MongoClient(os.getenv("DB_URL"))

# chapter db
db_chapter = client.chapter

# channels data
channels_md = db_chapter.data_mangadex


async def commands_remove_channel(bot, ctx, series_obj):
    md = MangaDex()
    msg = await series_obj.remove_channel(bot, ctx)
    if isinstance(msg, list):
        emojis = msg[3]
        manga_ids = msg[1]
        titles = msg[2]
        msg = msg[0]
        msg = await ctx.send(embed=msg)
    else:
        return await ctx.send(msg)
    for i in range(len(manga_ids)):
        await msg.add_reaction(emojis[i])

    def check(reaction, user):
        return user == ctx.author

    while True:
        reaction, user = await bot.wait_for("reaction_add", check=check)
        mangas_on_channel = (channels_md.find_one({"channel_id": str(ctx.channel.id)}))[
            "mangas"
        ]
        mangas_dict = eval(mangas_on_channel)
        idx = 0
        for i, emoji in enumerate(emojis):
            if emoji == str(reaction):
                idx = i
                break
        if str(reaction) == emojis[idx]:
            if manga_ids[idx] in mangas_dict:
                mangas_dict.pop(manga_ids[idx])
                new_doc = channels_md.find_one_and_update(
                    {"channel_id": str(ctx.channel.id)},
                    {"$set": {"mangas": str(mangas_dict)}},
                    return_document=pymongo.ReturnDocument.AFTER,
                )
                title = titles[idx]
                await ctx.channel.send(
                    f"This channel will no longer receive notifications on new chapters of {title}, I suppose!"
                )
