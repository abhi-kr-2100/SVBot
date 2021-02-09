"""Mimic the sticker features of Discord."""


from os import getenv

from discord.ext import commands

from .utils.utils import reply


class UtilityCog(commands.Cog):
    """A general-purpose cog meant for simple utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.s_reg = self._get_s_registry()

    @commands.command(
        name='s',
        help='Display a sticker.'
    )
    async def s_cmd(self, ctx: commands.Context, s_name: str):
        """Display a sticker."""

        if ctx.author.id != 711994085480726639:
            return

        url = self.s_reg.get(s_name.strip().lower())
        if url:
            await ctx.send(url)
        else:
            await reply(ctx, f"No such sticker: {s_name}")

    def _get_s_registry(self):
        """Return a dict mapping sticker name to sticker URL."""

        with open(getenv('S_FILENAME')) as s_file:
            return dict(
                (t[0].lower(), t[1]) for t in [line.split() for line in s_file]
            )


def setup(bot: commands.Bot):
    bot.add_cog(UtilityCog(bot))