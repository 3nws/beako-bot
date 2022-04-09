async def commands_add_channel(bot, ctx, series_obj):
    msg = await series_obj.add_channel(bot, ctx)
    if isinstance(msg, list):
        emojis = msg[0]
        titles = msg[2]
        manga_ids = msg[3]
        msg = msg[1]
    print(emojis, msg, titles, manga_ids)
    msg = await ctx.send(embed=msg)
    for emoji in emojis:
        await msg.add_reaction(emoji)
        
    # def check(reaction, user):
    #         return user == message.author
        
    # try:
    #     reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
    #     mangas_on_channel = (channels_md.find_one(channel_id))['mangas']
    #     mangas_dict = eval(mangas_on_channel)
    #     if str(reaction.emoji) == emojis[0]:
    #         if not is_in_md_list:
    #             mangas_dict.update({f"{titles[0]}": {md.get_latest(manga_ids[0])}})
    #             channels_md.update_one({"channel_id": id}, {"$set": {"mangas": str(mangas_dict)}})
                
                
    # except asyncio.TimeoutError:
    #     await channel.send('You took too long to pick one, in fact!')
    # else:
    #     print("Add channel else block on wait_for()")