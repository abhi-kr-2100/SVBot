"""A cog to play poker on Discord."""


from typing import Optional

import discord
from discord.ext import commands

from .utils.utils import reply
from .PokerAux.Game import Game
from .PokerAux import Implementation
from .PokerAux.Constants import CHANNEL_NAME


class Poker(commands.Cog):
    """Cog to play poker."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.poker_channel: Optional[discord.TextChannel] = None
        self.game: Optional[Game] = None

    @commands.command(
        name='poker',
        help='Start a game of poker!'
    )
    @commands.guild_only()
    async def poker(self, ctx: commands.Context, *players: discord.Member):
        """Start a game of poker with the given players!"""

        if not ctx.channel.name.startswith(CHANNEL_NAME):
            await reply(
                ctx,
                "You can only play poker in a channel named 'poker'. Please "
                "create a new channel called 'poker' and run this command "
                "there."
            )
            return
        else:
            self.poker_channel = ctx.channel

        if self.game is not None:
            await reply(
                ctx,
                "Someone is already player poker. Please wait for them to "
                "finish."
            )
            return

        players = (ctx.author,) + players

        if len(players) < 2:
            await reply(ctx, "You can't play poker alone!")
            return

        # make sure all players in the given players list are unique
        if len(set(players)) != len(players):
            await reply(
                ctx,
                "One player can only occupy one position."
            )
            return

        await Implementation.poker(self, ctx, players)

    @commands.command(
        name='killpoker',
        help='End a running game of poker.'
    )
    @commands.has_permissions(administrator=True)
    async def killpoker(self, ctx: commands.Context):
        """
        End a running game of poker.
        
        This command can only be run by an admin.
        """

        self.game = None

    @commands.command(
        name='endpoker',
        help='End a running game of poker.'
    )
    async def endpoker(self, ctx: commands.Context):
        """
        End a running poker game.
        
        This command can only be run by one of the active players.
        """

        if not await Implementation.runnable(self, ctx, False):
            return
        if not ctx.author in (p.member for p in self.game.players):
            await reply(ctx, "You can't run this command.")
            return

        self.game = None

    @commands.command(
        name='call',
        help='Bet the minimum required amount.'
    )
    @commands.guild_only()
    async def call(self, ctx: commands.Context):
        """Bet the minimum required chips in poker."""

        if not await Implementation.runnable(self, ctx):
            return
        if ctx.channel != self.poker_channel:
            raise commands.NoPrivateMessage

        await Implementation.call(self, ctx)

    @commands.command(
        name='bet',
        help='Place a bet.'
    )
    @commands.guild_only()
    async def bet(self, ctx: commands.Context, amt: int = None):
        """Bet the given amount of chips."""

        if not await Implementation.runnable(self, ctx):
            return
        if ctx.channel != self.poker_channel:
            raise commands.NoPrivateMessage

        if amt is None:
            await reply(ctx, "You didn't say how much you want to bet!")
            return

        await Implementation.bet(self, ctx, amt)

    @commands.command(
        name='fold',
        help='Fold your cards for this round'
    )
    @commands.guild_only()
    async def fold(self, ctx: commands.Context):
        """Fold your cards for this round."""

        if not await Implementation.runnable(self, ctx):
            return
        if ctx.channel != self.poker_channel:
            raise commands.NoPrivateMessage

        await Implementation.fold(self, ctx)

    @commands.command(
        name='all-in',
        help='Bet all your chips!'
    )
    @commands.guild_only()
    async def all_in(self, ctx: commands.Context):
        """
        Bet all your chips.
        
        TODO: Implement side pots.
        """

        if not await Implementation.runnable(self, ctx):
            return
        if ctx.channel != self.poker_channel:
            raise commands.NoPrivateMessage

        await Implementation.all_in(self, ctx)

    @commands.command(
        name='chips',
        help='Display the number of chips held by the player.'
    )
    async def chips(self, ctx: commands.Context, player: discord.Member = None):
        """
        Display the number of chips held by the given player.
        
        If no player is given, the person who runs the command is used.
        """

        if not await Implementation.runnable(self, ctx, False):
            return

        if player is None:
            player = ctx.author

        await Implementation.chips(self, ctx, player)

    @commands.command(
        name='pot',
        help='Show how many chips are in the pot.'
    )
    async def pot(self, ctx: commands.Context):
        """Show the amount of chips in the pot."""

        if not await Implementation.runnable(self, ctx, False):
            return

        await Implementation.pot(self, ctx)

    @commands.command(
        name='turn',
        help='Display which player is supposed to act now.'
    )
    async def turn(self, ctx: commands.Context):
        """Display which player's turn it is."""

        if not await Implementation.runnable(self, ctx, False):
            return

        await Implementation.turn(self, ctx)

    @poker.error
    async def poker_error(self, ctx: commands.Context, err: Exception):
        if isinstance(err, commands.NoPrivateMessage):
            await ctx.send("You can't use this command in a DM.")
        else:
            raise err

    @killpoker.error
    async def killpoker_error(self, ctx: commands.Context, err: Exception):
        if isinstance(err, commands.MissingPermissions):
            await ctx.send("You don't have the permission to run this command.")
        else:
            raise err

    @call.error
    async def call_error(self, ctx: commands.Context, err: Exception):
        if isinstance(err, commands.NoPrivateMessage):
            await ctx.send(
                "You can't use this command here. "
                f"Please go to {self.poker_channel.mention}, and use this "
                "command there."
            )
        else:
            raise err

    @bet.error
    async def bet_error(self, ctx: commands.Context, err: Exception):
        if isinstance(err, commands.NoPrivateMessage):
            await ctx.send(
                "You can't use this command here. "
                f"Please go to {self.poker_channel.mention}, and use this "
                "command there."
            )
        else:
            raise err

    @fold.error
    async def fold_error(self, ctx: commands.Context, err: Exception):
        if isinstance(err, commands.NoPrivateMessage):
            await ctx.send(
                "You can't use this command here. "
                f"Please go to {self.poker_channel.mention}, and use this "
                "command there."
            )
        else:
            raise err

    @all_in.error
    async def all_in_error(self, ctx: commands.Context, err: Exception):
        if isinstance(err, commands.NoPrivateMessage):
            await ctx.send(
                "You can't use this command here. "
                f"Please go to {self.poker_channel.mention}, and use this "
                "command there."
            )
        else:
            raise err


def setup(bot):
    bot.add_cog(Poker(bot))