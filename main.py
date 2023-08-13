from nextcord.ext import commands
import nextcord
import os

bot = commands.Bot(intents=nextcord.Intents.all(), command_prefix='.')

@bot.event
async def on_ready():
  await bot.change_presence(status=nextcord.Status.idle)
  print("On.")


# command not found
@bot.event
async def on_command_error(ctx, error):
  if isinstance(error, commands.CommandNotFound):
    await ctx.message.add_reaction("❓")
    await ctx.send('?')
  else:
    print(error)


# scan cocks
for cock in os.listdir('./cocks'):
  if cock.endswith('.py'):
    bot.load_extension('cocks.' + cock[:-3])

bot.run("MTEzOTE4MzU2NjQ1OTI0ODY1Mg.GYKKqY.2_vAJd44aP3DEhmDuc3bVIKu3yFPyAQxW0Vtz4")