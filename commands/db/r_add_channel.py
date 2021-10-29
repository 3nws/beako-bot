async def commands_add_channel(ctx, series_obj):
    await ctx.send(series_obj.add_channel())