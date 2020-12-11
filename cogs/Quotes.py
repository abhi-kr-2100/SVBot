"""
A Cog to display a quote given a tag.

The quotes are stored in a SQLite3 database called quotes.db.
"""


from random import choice
import sqlite3

from discord.ext import commands

from .utils.utils import reply


class Quotes(commands.Cog):
    """Cog to display a quote given a tag."""

    def __init__(self, bot):
        self.bot = bot

        self.conn = sqlite3.connect('quotes.db')
        self.c = self.conn.cursor()

    @commands.command(
        name='qt',
        help="Display a quote related to the given tag."
    )
    async def quote(self, ctx, tag):
        """Reply with a relevent quote given a tag."""

        tag = tag.lower()

        tag_id = self.c.execute(
            'SELECT TagId FROM tags WHERE TagName=?', (tag,)
        ).fetchone()

        quote_id = choice(
            self.c.execute(
                'SELECT QuoteId FROM links WHERE TagId=?', tag_id
            ).fetchall()
        )

        quote = self.c.execute(
            'SELECT QuoteText FROM quotes WHERE QuoteId=?', quote_id
        ).fetchone()[0]

        await reply(ctx, quote)


def setup(bot):
    bot.add_cog(Quotes(bot))