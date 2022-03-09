async def commands_add_channel(ctx, series_obj):
    msg = await series_obj.add_channel()
    await ctx.send(msg)
