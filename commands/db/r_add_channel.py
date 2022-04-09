import pymongo
import os

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
    for emoji in emojis:
        await msg.add_reaction(emoji)
        
    def check(reaction, user):
            return user == ctx.author
        
    try:
        channel_id = ctx.channel.id,
        reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        mangas_on_channel = (channels_md.find_one({"channel_id": str(ctx.channel.id)}))['mangas']
        print(mangas_on_channel)
        mangas_dict = eval(mangas_on_channel)
        # is_in_md_list = channels_md.count_documents(channel_entry, limit=1) != 0 gotta find an alternative
        if reaction == emojis[0]:
            # if not is_in_md_list:
                mangas_dict.update({f"{titles[0]}": {md.get_latest(manga_ids[0])}})
                channels_md.update_one({"channel_id": id}, {"$set": {"mangas": str(mangas_dict)}})
                print("added")

    except asyncio.TimeoutError:
        await channel.send('You took too long to pick one, in fact!')
    else:
        print("Add channel else block on wait_for()")