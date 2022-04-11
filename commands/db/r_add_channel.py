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

async def commands_add_channel(bot, ctx, series_obj):
    md = MangaDex()
    msg = await series_obj.add_channel(bot, ctx)
    if isinstance(msg, list):
        emojis = msg[0]
        titles = msg[2]
        manga_ids = msg[3]
        msg = msg[1]
        msg = await ctx.send(embed=msg)
    else:
        return await ctx.send(msg)
    for i in range(len(manga_ids)):
        await msg.add_reaction(emojis[i])
        
    def check(reaction, user):
            return user == ctx.author
        
    while True:
        reaction, user = await bot.wait_for('reaction_add', check=check)
        channel_exists = True if channels_md.find_one({"channel_id": str(ctx.channel.id)}) else False
        if not channel_exists:
            channels_md.insert_one({
                'channel_id': str(ctx.channel.id),
                'mangas': '{}',
            })
        mangas_on_channel = (channels_md.find_one({"channel_id": str(ctx.channel.id)}))['mangas']
        mangas_dict = eval(mangas_on_channel)
        idx = 0
        for i, emoji in enumerate(emojis):
            if emoji == str(reaction):
                idx = i
                break
        if str(reaction) == emojis[idx]:
            if manga_ids[idx] not in mangas_dict:
                chapter_response = md.get_latest(manga_ids[idx])
                title_response = chapter_response.get_title()
                latest = title_response[0]
                is_title = title_response[1]
                chapter_link = chapter_response.get_link()
                mangas_dict.update({f"{manga_ids[idx]}": str(latest)})
                new_doc = channels_md.find_one_and_update(
                    {'channel_id': str(ctx.channel.id)}, 
                    {
                        '$set': {
                            'mangas': str(mangas_dict)
                        }
                    },
                    return_document=pymongo.ReturnDocument.AFTER
                )
                await ctx.channel.send(f"This channel will receive notifications on new chapters of {titles[idx]}, I suppose!")
            else:
                ## THE FUCK?!
                # await ctx.channel.send('This channel is already on the receiver list, in fact!')
                pass
