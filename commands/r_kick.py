async def commands_kick(ctx, user, reason):
  await user.kick(reason=reason)
  await ctx.send(f"{user} has been yeeted.")