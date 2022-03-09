async def commands_ban(ctx, user, reason):
    await user.ban(reason=reason)
    await ctx.send(f"{user} has been yeeted forever, I suppose!")
