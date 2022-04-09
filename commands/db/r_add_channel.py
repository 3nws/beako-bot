async def commands_add_channel(bot, ctx, series_obj):
    msg = await series_obj.add_channel(bot, ctx)
    if isinstance(msg, list):
        emojis = msg[0]
        msg = msg[1]
    msg = await ctx.send(embed=msg)
    for emoji in emojis:
        await msg.add_reaction(emoji)
        
    def check(reaction, user):
            return user == message.author

    # try:
    #     reaction, user = await bot.wait_for('reaction_add', timeout=60.0, check=check)
        
        # if str(reaction.emoji) == emojis[0]:
        
    # except asyncio.TimeoutError:
    #     await channel.send('You took too long to pick one, in fact!')
    # else:
    #     print("Add channel else block on wait_for()")
