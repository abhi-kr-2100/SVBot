"""Register GIFs for quick use later."""


from discord.ext import commands

from .utils.utils import reply
from .ErgonomicGIFAux import Implementation


class ErgonomicGIF(commands.Cog):
    """Register GIFs for quick use later."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.users_table = 'GIFUsers'
        self.regs_table = 'GIFRegistrations'

        Implementation.create_tables(self.users_table, self.regs_table)
        
    @commands.command(
        name='newgif',
        help='Register a new GIF.'
    )
    async def newgif(self, ctx: commands.Context, key: str, url: str):
        """Register a given GIF's URL to the given keyword."""

        uid = Implementation.get_uid(self.users_table, ctx.author.id)
        Implementation.create_registration(self.regs_table, uid, key, url)

        await reply(ctx, "GIF registration successfully created.")

    @commands.command(
        name='gif',
        help='Display the GIF associated with the given keyword.'
    )
    async def gif(self, ctx: commands.Context, key: str):
        """Display the GIF associated with key."""

        uid = Implementation.get_uid(self.users_table, ctx.author.id)
        url = Implementation.get_gif_url(self.regs_table, uid, key)

        if url is None:
            await reply(ctx, f"No GIF has been associated with {key}.")
        else:
            await ctx.send(url)

    @commands.command(
        name='gifls',
        help='Display all GIF associations that you have created.'
    )
    async def gifls(self, ctx: commands.Context):
        """List all GIF associations that the user has created."""

        uid = Implementation.get_uid(self.users_table, ctx.author.id)
        keys = Implementation.get_keys(self.regs_table, uid)

        await reply(ctx, ', '.join(keys))

    @commands.command(
        name='gifrm',
        help='Remove a keyword along with all GIFs associated with it.'
    )
    async def gifrm(self, ctx: commands.Context, key: str):
        uid = Implementation.get_uid(self.users_table, ctx.author.id)
        success = Implementation.remove_key(self.regs_table, uid, key)

        if not success:
            await reply(ctx, "This key is not present in the first place!")
        else:
            await reply(ctx, "Key deleted.")

    @commands.command(
        name='gifkeyls',
        help='Display all GIF URLs associated with the given key.'
    )
    async def gifkeyls(self, ctx: commands.Context, key: str):
        """Display all GIF URLs associated with the given key."""

        uid = Implementation.get_uid(self.users_table, ctx.author.id)
        urls = Implementation.get_urls(self.regs_table, uid, key)

        for u in urls:
            await ctx.send(f"`{u}`")

    @commands.command(
        name='gifurlrm',
        help='Delete one URL associated with a given key.'
    )
    async def gifurlrm(self, ctx: commands.Context, key: str, url: str):
        """Remove URL from key."""

        uid = Implementation.get_uid(self.users_table, ctx.author.id)
        Implementation.remove_url(self.regs_table, uid, key, url)

        await reply(ctx, "URL deleted.")


def setup(bot: commands.Bot):
    bot.add_cog(ErgonomicGIF(bot))