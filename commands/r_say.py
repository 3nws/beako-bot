async def commands_say(ctx, msg):
  await ctx.message.delete()
  await ctx.send(msg)