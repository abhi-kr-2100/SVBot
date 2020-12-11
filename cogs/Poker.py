"""A cog to play poker on Discord."""


from discord.ext import commands


class Poker(commands.Cog):
    """Cog to play poker."""

    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Poker(bot))