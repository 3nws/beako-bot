async def commands_clean(ctx, limit):
  await ctx.message.delete()
  await ctx.channel.purge(limit=limit)
  await ctx.send('Cleared by {}'.format(ctx.author.mention))