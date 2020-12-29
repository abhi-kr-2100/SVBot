"""Register GIFs for quick use later."""


from discord.ext import commands

from .utils.utils import reply
from .ErgonomicGIFAux import Implementations


class ErgonomicGIF(commands.Cog):
    """Register GIFs for quick use later."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.users_table = 'GIFUsers'
        self.regs_table = 'GIFRegistrations'

        Implementations.create_tables(self.users_table, self.regs_table)
        
    @commands.command(
        name='newgif',
        help='Register a new GIF.'
    )
    async def newgif(self, ctx: commands.Context, key: str, url: str):
        """Register a given GIF's URL to the given keyword."""

        uid = Implementations.get_uid(self.users_table, ctx.author.id)
        Implementations.create_registration(self.regs_table, uid, key, url)

        await reply(ctx, "GIF registration successfully created.")

    @commands.command(
        name='gif',
        help='Display the GIF associated with the given keyword.'
    )
    async def gif(self, ctx: commands.Context, key: str):
        """Display the GIF associated with key."""

        uid = Implementations.get_uid(self.users_table, ctx.author.id)
        url = Implementations.get_gif_url(self.regs_table, uid, key)

        if url is None:
            await reply(ctx, f"No GIF has been associated with {key}.")
        else:
            await ctx.send(url)


def setup(bot: commands.Bot):
    bot.add_cog(ErgonomicGIF(bot))