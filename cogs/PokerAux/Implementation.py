"""This module actually implements the methods of the poker cog."""


from typing import List

from discord.ext.commands import Context

from .Game import Game
from .Player import Player
from ..utils.utils import reply
from .Constants import STARTING_CHIPS, SM_BLIND_BET


async def poker(cog, ctx: Context, players: List[Player]):
    """Start the game of poker."""

    cog.game = Game(
        ctx,
        players,
        STARTING_CHIPS,
        SM_BLIND_BET
    )

    while cog.game.winner is None:
        await ctx.send("------ N E W    R O U N D ------")

        try:
            await cog.game.preflop()
            await cog.game.start_betting()

            await cog.game.flop()
            await cog.game.start_betting()
            
            await cog.game.turn()
            await cog.game.start_betting()
            
            await cog.game.river()
            await cog.game.start_betting()
            
            await cog.game.showdown()
            await cog.game.next_round()
        except AttributeError:  # the game has been ended by an admin
            await ctx.send("The game has been ended prematurely.")
            return

    await ctx.send(f"{cog.game.winner.member.mention} wins the game!")
    await ctx.send(f"Game Over!")
    cog.game = None

async def call(cog, ctx: Context):
    """Bet the minimum required chips."""

    pp = cog.game.pending_players[cog.game.pending_index]
    min_bet = cog.game.min_bet - pp.betted

    # player can't match the minimum amount without going all-in
    if min_bet >= pp.chips:
        await reply(ctx, f"goes all in with {pp.chips} chips.")

        min_bet = pp.chips
        pp.all_in = True
    elif min_bet == 0:
        await reply(ctx, f"checks.")
    else:
        await reply(ctx, f"bets {min_bet} chips.")

    cog.game.place_bet(pp, min_bet)
    pp.turn_pending = False

    cog.game.pending_index += 1
    cog.game.pending_index %= cog.game.n

async def bet(cog, ctx: Context, amt: int):
    """Place a bet."""

    pp = cog.game.pending_players[cog.game.pending_index]
    min_bet = cog.game.min_bet - pp.betted

    if amt > pp.chips:
        await reply(ctx, "You don't have enough chips.")
        return
    
    if amt < min_bet:
        await reply(ctx, f"You must bet {min_bet} or higher.")
        return
    
    if amt == pp.chips:
        await reply(ctx, f"goes all in with {amt} chips!")

        pp.all_in = True
    elif amt == min_bet:
        if amt == 0:
            await reply(ctx, "checks.")
        else:
            await reply(ctx, f"calls with {amt} chips.")
    else:
        await reply(ctx, f"bets {amt} chips.")

    cog.game.place_bet(pp, amt)
    pp.turn_pending = False
    cog.game.min_bet = max(cog.game.min_bet, pp.betted)

    cog.game.pending_index += 1
    cog.game.pending_index %= cog.game.n

async def fold(cog, ctx: Context):
    await reply(ctx, "folds.")
    
    pp = cog.game.pending_players[cog.game.pending_index]
    pp.not_folded = False
    pp.turn_pending = False
    
    cog.game.pending_index += 1
    cog.game.pending_index %= cog.game.n

async def all_in(cog, ctx: Context):        
    pp = cog.game.pending_players[cog.game.pending_index]
    
    await reply(ctx, f"goes all in with {pp.chips}!")
    
    cog.game.place_bet(pp, pp.chips)
    
    pp.turn_pending = False
    pp.all_in = True

    cog.game.min_bet = max(cog.game.min_bet, pp.betted)

    cog.game.pending_index += 1
    cog.game.pending_index %= cog.game.n

async def chips(cog, ctx: Context, player: Player):        
    for p in cog.game.players:
        if p.member == player:
            await ctx.send(f"{p.member.mention} has {p.chips} chips.")
            return

    await ctx.send(f"{player.mention} is not playing with you.")

async def pot(cog, ctx: Context):        
    await ctx.send(f'Pot: {cog.game.pot} chips')

async def turn(cog, ctx: Context):    
    pp = cog.game.pending_players[cog.game.pending_index]
    await ctx.send(f"It's {pp.member.mention}'s turn.")

async def runnable(cog, ctx: Context, pp=True):
    """Check against errors like wrong turn or not inside game."""

    if cog.game is None:
        await reply(
            ctx,
            "We're not inside a poker game right now."
        )
        return False

    if pp:
        pending_player = cog.game.pending_players[cog.game.pending_index]
        if ctx.author != pending_player.member:
            await reply(
                ctx,
                f"It's not your turn yet. "
                f"{pending_player.member.mention} is supposed to act."
            )
            return False

    return True