async def commands_remove_channel(ctx, series_obj):
    msg = await series_obj.remove_channel()
    await ctx.send(msg)
