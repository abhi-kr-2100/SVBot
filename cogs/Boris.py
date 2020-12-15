"""Display the :boris: emoji."""


from random import random

from discord.ext import commands, tasks


class Boris(commands.Cog):
    """Display the :boris: emoji when called."""

    def __init__(self, bot):
        self.bot = bot
        self.ctx = None

    # @commands.command(
    #     name='boris',
    #     help='Display the Boris emoji.'
    # )
    # async def boris(self, ctx):
    #     """Display :Boris: at arbitrary times."""

    #     await ctx.send("<:Boris:756477965784842261>")


def setup(bot):
    bot.add_cog(Boris(bot))