from nextcord.ext import commands
import json

with open('users/allowed.json') as file:
  json_content = file.read()
allowed_ids = json.loads(json_content)


class Permisions(commands.Cog):

  def __init__(self, bot):
    self.client = bot

  @commands.command(description='Get A List Of Registered Users.')
  async def users(self, ctx):
    users = ""
    for id in allowed_ids:
      user = await self.client.fetch_user(int(id))
      users += f"- **id:** `{id}`, **username:** `{user.name}`\n"

    await ctx.reply(users)


def setup(bot):
  bot.add_cog(Permisions(bot))
