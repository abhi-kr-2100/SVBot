"""
Auxiliary module for the Poker Cog. This module defines classes related to
poker cards and deck.
"""


from enum import IntEnum, Enum, unique, auto
from random import shuffle


@unique
class CardRank(IntEnum):
    """One of the 13 playing card ranks."""

    two     = 2
    three   = 3
    four    = 4
    five    = 5
    six     = 6
    seven   = 7
    eight   = 8
    nine    = 9
    ten     = 10
    jack    = 11
    queen   = 12
    king    = 13
    ace     = 14

@unique
class CardSuit(Enum):
    """One of the four playing suits."""

    diamond = 1
    heart   = 2
    club    = 3
    spade   = 4


class Card:
    """A playing card."""

    def __init__(self, rank, suit):
        assert isinstance(rank, CardRank) and isinstance(suit, CardSuit)

        self.rank = rank
        self.suit = suit

    def __str__(self):
        if self.rank == CardRank.jack:
            rank_name = 'Jack'
            rank_symb = rank_name[0]
        elif self.rank == CardRank.queen:
            rank_name = 'Queen'
            rank_symb = rank_name[0]
        elif self.rank == CardRank.king:
            rank_name = 'King'
            rank_symb = rank_name[0]
        elif self.rank == CardRank.ace:
            rank_name = 'Ace'
            rank_symb = rank_name[0]
        else:
            rank_name = str(self.rank.value)
            rank_symb = rank_name

        if self.suit == CardSuit.diamond:
            suit_name = 'Diamonds'
            suit_symb = ':diamonds:'
        elif self.suit == CardSuit.club:
            suit_name = 'Clubs'
            suit_symb = ':clubs:'
        elif self.suit == CardSuit.heart:
            suit_name = 'Hearts'
            suit_symb = ':hearts:'
        elif self.suit == CardSuit.spade:
            suit_name = 'Spades'
            suit_symb = ':spades:'
        else:
            assert False, "This shouldn't have happened!"

        return f"{rank_name} of {suit_name} ({rank_symb} {suit_symb})"


class Deck:
    """A standard 52-card deck."""

    def __init__(self):
        self.cards = [
            Card(r, s) for s in list(CardSuit) for r in list(CardRank)
        ]

    def shuffle_deck(self):
        """Shuffle all remaining cards."""

        shuffle(self.cards)

    def deal(self, n=1):
        """Deal n cards from top of the deck."""

        assert n >= 0, "Can't deal a negative number of cards!"
        
        if len(self.cards) < n:
            raise ValueError("No enough cards to deal.")

        cards = []
        for i in range(n):
            cards.append(self.cards.pop())

        return cards

    def reset(self):
        """Start the deck anew, but shuffled."""

        self.cards = [
            Card(r, s) for s in list(CardSuit) for r in list(CardRank)
        ]
        self.shuffle_deck()