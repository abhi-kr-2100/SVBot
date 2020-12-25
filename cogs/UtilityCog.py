"""A general-purpose Cog meant for simple utility commands."""


import discord
from discord.ext import commands

from .utils.utils import reply


class UtilityCog(commands.Cog):
    """A general-purpose cog meant for simple utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name='id',
        help='Display your user id on Discord'
    )
    async def id_cmd(self, ctx: commands.Context):
        """Display the ID of the user who runs the command."""

        await reply(ctx, f"Your ID is `{ctx.author.id}`.")


def setup(bot: commands.Bot):
    bot.add_cog(UtilityCog(bot))