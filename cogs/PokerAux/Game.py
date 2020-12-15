"""
Auxiliary module for the Poker Cog. This module defines classes related to
the poker game.
"""


import asyncio
from random import randint

from pokereval.card import Card
from pokereval.hand_evaluator import HandEvaluator

from .Cards import Deck
from .Player import Player, PlayerStatus


class Game:
    """A game of poker."""

    def __init__(self, ctx, players, starting_chips, sm_blind):
        self.ctx = ctx

        self.pot = 0
        self.sm_blind_bet = sm_blind

        self.deck = Deck()
        self.deck.shuffle_deck()

        self.players = [Player(p, starting_chips) for p in players]
        self.n = len(players)

        # index of the dealer
        self.di = None
        
        self.small_blind_i = None
        self.big_blind_i = None

        self.community_cards = []

        # the minimum amount to bet during a particular turn
        self.min_bet = 0

        # player whose turn it is
        self.pending_players = []
        self.pending_index = 0

        self.winners = None

    def place_bet(self, player, amt):
        """Place a bet of given amout on behalf of the given player."""

        self.pot += amt
        player.chips -= amt
        player.betted += amt
        
    async def preflop(self):
        """Prepare the game for the next turn."""

        self._pre_turn_setup()

        self.deck.reset()
        await self._deal_holes()
        await self._setup_blinds()
        await self._post_blinds()

        self._assign_turns(self.big_blind_i + 1)

    async def start_betting(self):
        """Wait till all players have had their turn."""

        self.pending_index = 0

        while any(
            (p.betted != self.min_bet or p.active) for p in self.pending_players
        ):
            await asyncio.sleep(0)

    async def flop(self):
        """Deal the poker flop."""
        
        self._pre_turn_setup()
        
        c1, c2, c3 = self.deck.deal(3)
        self.community_cards += [c1, c2, c3]

        await self._display_community_cards()

        self._assign_turns(self.small_blind_i)

    async def turn(self):
        """The stage in poker after the flop."""

        self._pre_turn_setup()
        
        c4 = self.deck.deal()
        self.community_cards += [c4]

        await self._display_community_cards()

        self._assign_turns(self.small_blind_i)

    async def river(self):
        """The last hand in a poker turn."""

        self._pre_turn_setup()
        
        c5 = self.deck.deal()
        self.community_cards.append(c5)

        await self._display_community_cards()

        self._assign_turns(self.small_blind_i)

    async def showdown(self):
        """Time for remaining players to compare cards."""

        community_cards = [Card(*repr(c)) for c in self.community_cards]
        
        max_score = 0
        winners = []

        for p in self.players:
            if p.active:
                hole_cards = [Card(*c.pec()) for c in p.hole_cards]
                score = HandEvaluator.evaluate_hand(hole_cards, community_cards)
                
                if score > max_score:
                    max_score = score
                    winners = [p]
                elif score == max_score:
                    winners.append(p)

        self.winners = winners

    def _assign_turns(self, start):
        """Change players to be pending turn."""

        for i in range(start, start + self.n):
            p = self.players[i % self.n]
            p.turn_pending = True
            self.pending_players.append(p)

    async def _display_community_cards(self):
        to_display = ' '.join(f'({c})' for c in self.community_cards)
        await self.ctx.send(f"Community Cards: {to_display}")
    
    async def _post_blinds(self):
        """Enforce blind bets."""

        sm_b = self.players[self.small_blind_i]
        bg_b = self.players[self.big_blind_i]

        sm_b.chips -= self.sm_blind_bet
        sm_b.betted += self.sm_blind_bet
        await self.ctx.send(
            f'{sm_b.member.mention} posts small blind of '
            f'{self.sm_blind_bet}.'
        )
        
        bg_b.chips -= 2 * self.sm_blind_bet
        bg_b.betted += 2 * self.sm_blind_bet
        await self.ctx.send(
            f'{bg_b.member.mention} posts big blind of '
            f'{2 * self.sm_blind_bet}'
        )

        self.min_bet = 2 * self.sm_blind_bet

    async def _introduce(self):
        """Send an introductory message."""

        INSTRUCTIONS_URL = 'https://gist.github.com/abhi-kr-2100/cfd1bc4fc4ed7a4578c03ef650f04f1c'
        INTRO = (
            "Welcome to Discord Poker.!\n\n"
            "If you're playing for the first time, please read the instructions"
            f" here carefully: {INSTRUCTIONS_URL}.\n\n"
            "For optimal experience, use Discord in Light mode while playing "
            "Discord Poker.\n\n"
            "Enjoy the game! (FFF)"
        )

        await self.ctx.send(
            ', '.join(f'{p.member.mention}' for p in self.players)
        )
        await self.ctx.send(INTRO)

    async def _deal_holes(self):
        """Deal hole cards to all players."""

        for p in self.players:
            c1, c2 = self.deck.deal(2)
            p.hole_cards = [c1, c2]
            await p.member.send(str(c1))
            await p.member.send(str(c2))

    async def _setup_blinds(self):
        """Choose the dealer and the blinds."""

        if len(self.players) == 2:
            self.small_blind_i = 0
            
            self.players[self.small_blind_i].status = PlayerStatus.small_dealer
            await self.ctx.send(
                f"{self.players[self.small_blind_i].member.mention} "
                 "You're the small blind."
            )
            
            self.big_blind_i = 1

            self.players[self.big_blind_i].status = PlayerStatus.big_blind
            await self.ctx.send(
                f"{self.players[self.big_blind_i].member.mention} "
                 "You're the big blind."
            )
        else:
            if self.di is None:
                self.di = randint(0, self.n - 1)
            else:
                self.di = (self.di + 1) % self.n

            self.players[self.di % self.n].status = PlayerStatus.dealer

            self.small_blind_i = (self.di + 1) % self.n
            self.big_blind_i = (self.di + 2) % self.n

            sb = self.players[self.small_blind_i]
            bb = self.players[self.big_blind_i]
            
            sb.status = PlayerStatus.small_blind
            await self.ctx.send(
                f"{sb.member.mention} You're the small blind."
            )
            bb.status = PlayerStatus.big_blind
            await self.ctx.send(
                f"{bb.member.mention} You're the big blind."
            )

    def _pre_turn_setup(self):
        """Set up the game for a new turn."""

        self.min_bet = 0
        self.pending_players = []
        self.pending_index = 0

        for p in self.players:
            p.active = False
            p.betted = 0