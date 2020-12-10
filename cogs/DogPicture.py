"""
A Cog to display a dog picture whenever !dog command is issued.
"""

from requests import get as http_get

from discord.ext import commands

from .utils.utils import reply


class DogPicture(commands.Cog):
    """Cog to display a random dog picture."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='dog',
        help='Display a random dog image.'
    )
    async def dog(self, ctx):
        """Display a random dog image."""

        API_CALL = "https://api.thedogapi.com/v1/images/search"

        resp = http_get(API_CALL)
        if resp.status_code != 200:
            await reply(ctx, "An error occurred!")
            return

        await ctx.send(resp.json()[0]['url'])


def setup(bot):
    bot.add_cog(DogPicture(bot))