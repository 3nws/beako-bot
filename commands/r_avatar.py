import discord

async def commands_avatar(ctx, member):
  avatar_frame = discord.Embed(
    color = discord.Colour.random()
  )
  if member:
    avatar_frame.add_field(name=str(ctx.author)+" requested", value=member.mention+"'s avatar.")
    avatar_frame.set_image(url=f'{member.avatar_url}')
  else:
    avatar_frame.add_field(name=str(ctx.author), value=ctx.author.mention+"'s avatar.")
    avatar_frame.set_image(url=f'{ctx.author.avatar_url}')
    
  await ctx.send(embed=avatar_frame)