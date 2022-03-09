async def commands_clean(ctx, limit, msg_id):
    await ctx.message.delete()

    if (msg_id):
        msg = await ctx.fetch_message(msg_id)
        history = await ctx.channel.history(limit=limit, after=msg, oldest_first=True).flatten()
        for message in history:
            await message.delete()
    else:
        await ctx.channel.purge(limit=limit)

    await ctx.send('Cleared by {}, I suppose!'.format(ctx.author.mention))
