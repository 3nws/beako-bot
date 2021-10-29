async def commands_remove_channel(ctx, series_obj):
    await ctx.send(series_obj.remove_channel())