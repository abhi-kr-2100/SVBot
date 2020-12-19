"""
Auxiliary module for the Poker Cog. This module defines classes related to
the poker game.
"""


import asyncio
from random import randint, choice

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

        self.winner = None

    def place_bet(self, player, amt):
        """Place a bet of given amout on behalf of the given player."""

        self.pot += amt
        player.chips -= amt
        player.betted += amt

    async def start_betting(self):
        """Wait till all players have had their turn."""

        # the first pending player bets first
        self.pending_index = 0

        # betting ends when:
        # - all active players have at least made one move
        # - all players have betted the minimum amount (if possible for them)
        # - if they have not betted the minimum amount, they should either be
        #   all-in or folded
        #
        # OR
        #
        # - if everyone except one player folds
        #
        # OR
        #
        # - if everyone or everyone except one player is all in.
        while True:
            # players who have not had even one turn to act
            turn_pending_players = [
                p for p in self.pending_players if p.turn_pending
            ]

            # how many players have to bet more
            # players don't have to bet more only if one of these is true:
            # - they have matched min_bet
            # - they have gone all-in
            # - they have folded
            held_players = []
            for p in self.pending_players:
                # player has matched min_bet
                if self.min_bet == p.betted or p.all_in or not p.not_folded:
                    continue
                held_players.append(p)

            if len(turn_pending_players) == len(held_players) == 0:
                break

            # all except one has folded; there's no one to bet
            if self._all_folded():
                break

            if self._all_except_one_all_in():
                break

            # folded players shouldn't act
            if not self.pending_players[self.pending_index].not_folded:
                self.pending_index += 1
                self.pending_index %= self.n

            # players who are all-in shouldn't act
            if self.pending_players[self.pending_index].all_in:
                self.pending_index += 1
                self.pending_index %= self.n

            await asyncio.sleep(0)  # allow other tasks to continue
        
    async def preflop(self):
        """Prepare the game for the next turn."""

        await self.ctx.send("------ P R E F L O P ------")

        self._pre_turn_setup()

        self.deck.reset()
        await self._deal_holes()
        await self._setup_blinds()
        await self._post_blinds()

        self._assign_turns(self.big_blind_i + 1)

    async def flop(self):
        """Deal the poker flop."""
        
        # winner has already been decided
        if self._all_folded():
            return

        await self.ctx.send("------ F L O P ------")

        self._pre_turn_setup()
        
        c1, c2, c3 = self.deck.deal(3)
        self.community_cards += [c1, c2, c3]

        await self._display_community_cards()

        self._assign_turns(self.small_blind_i)

    async def turn(self):
        """The stage in poker after the flop."""

        # winner has already been decided
        if self._all_folded():
            return

        await self.ctx.send("------ T U R N ------")

        self._pre_turn_setup()
        
        c4 = self.deck.deal()
        self.community_cards += [c4]

        await self._display_community_cards()

        self._assign_turns(self.small_blind_i)

    async def river(self):
        """The last hand in a poker turn."""

        # winner has already been decided
        if self._all_folded():
            return

        await self.ctx.send("------ R I V E R ------")
            
        self._pre_turn_setup()
        
        c5 = self.deck.deal()
        self.community_cards.append(c5)

        await self._display_community_cards()

        self._assign_turns(self.small_blind_i)

    async def showdown(self):
        """Time for remaining players to compare cards."""

        # change the community cards to be compatible with pokereval's
        # HandEvaluator
        community_cards = [Card(*c.pec()) for c in self.community_cards]
        
        max_score = 0
        winners = []

        active_players = [p for p in self.players if p.not_folded]

        # the unfolded player wins by default; no need to show his/her cards
        if len(active_players) == 1:
            await self.ctx.send(
                f"{active_players[0].member.mention} wins this round."
            )
            self._divide_pot(active_players)
            return

        for p in active_players:
            await self.ctx.send(
                f"{p.member.mention} -- "
                f"({p.hole_cards[0]}) ({p.hole_cards[1]})"
            )

            # change the hole cards to be compatible with pokereval's
            # HandEvaluator
            hole_cards = [Card(*c.pec()) for c in p.hole_cards]
            score = HandEvaluator.evaluate_hand(hole_cards, community_cards)
            
            if score > max_score:
                max_score = score
                winners = [p]
            elif score == max_score:
                winners.append(p)

        await self.ctx.send('Winners of this round are:')
        for w in winners:
            await self.ctx.send(
                f'{w.member.mention} with '
                f'({w.hole_cards[0]}) and ({w.hole_cards[1]})'
            )

        self._divide_pot(winners)

    async def next_round(self):
        """Prepare the game for the next round."""

        self.community_cards = []
        self.pot = 0

        for p in self.players:
            if p.chips == 0:
                # this player has lost the game
                p.active = False
            else:
                p.active = True
                p.turn_pending = True
                p.not_folded = True
                p.all_in = False
                p.betted = 0

        self.players = [p for p in self.players if p.active]
        self.n = len(self.players)
        
        if len(self.players) == 1:
            self.winner = self.players[0]

    def _all_folded(self):
        """Have all except one player folded?"""

        return len([p for p in self.pending_players if p.not_folded]) == 1

    def _all_except_one_all_in(self):
        """
        Is every player except one all in?
        
        The one who is not all in, must not have any pending bets:
            - should either be folded
            - or matched
        """

        not_all_in = [p for p in self.pending_players if not p.all_in]

        # have all not all in players met their obligations
        for p in not_all_in:
            # this player has betted the most; everyone else is trying to match
            # him/her
            if p.betted == self.min_bet:
                continue

            if p.not_folded:
                # if they have not, the betting must continue
                return False

        return len(not_all_in) <= 1

    def _divide_pot(self, winners):
        """Divide the pot among the winners."""

        amt_each = self.pot // len(winners)
        amt_left = self.pot % len(winners)

        for p in winners:
            p.chips += amt_each

        choice(winners).chips += amt_left

    def _assign_turns(self, start):
        """Change players to be pending turn."""

        for i in range(start, start + self.n):
            p = self.players[i % self.n]
            if p.not_folded:
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
        self.pot += 3 * self.sm_blind_bet

    async def _deal_holes(self):
        """Deal hole cards to all players."""

        for p in self.players:
            if not p.active:
                continue

            c1, c2 = self.deck.deal(2)
            p.hole_cards = [c1, c2]
            
            await p.member.send("Here are your cards:")
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
            p.turn_pending = False
            p.betted = 0