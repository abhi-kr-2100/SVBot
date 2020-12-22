"""
Auxiliary module for the Poker Cog. This module defines classes related to
poker cards and deck.
"""


from enum import IntEnum, Enum, unique
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

    def __str__(self) -> str:
        if self.rank == CardRank.jack:
            rank_symb = 'J'
        elif self.rank == CardRank.queen:
            rank_symb = 'Q'
        elif self.rank == CardRank.king:
            rank_symb = 'K'
        elif self.rank == CardRank.ace:
            rank_symb = 'A'
        else:
            rank_symb = str(self.rank.value)

        return rank_symb


@unique
class CardSuit(Enum):
    """One of the four playing suits."""

    spades = 1
    hearts = 2
    diamonds = 3
    clubs = 4

    def __str__(self) -> str:
        """Return the appropriate code for the suit's Discord emoji."""
        
        suit_symb = ''

        if self.suit == CardSuit.diamonds:
            suit_symb = ':diamonds:'
        elif self.suit == CardSuit.clubs:
            suit_symb = ':clubs:'
        elif self.suit == CardSuit.hearts:
            suit_symb = ':hearts:'
        elif self.suit == CardSuit.spades:
            suit_symb = ':spades:'

        return suit_symb


class Card:
    """A playing card."""

    def __init__(self, rank: CardRank, suit: CardSuit):
        self.rank = rank
        self.suit = suit

    def pec(self) -> tuple[int, int]:
        """Return a tuple that can be used to construct a pokereval.Card."""

        return (self.rank.value, self.suit.value)

    def __str__(self) -> str:
        return f"{self.rank} {self.suit}"


class Deck:
    """A standard 52-card deck."""

    def __init__(self):
        self.cards = [
            Card(r, s) for s in list(CardSuit) for r in list(CardRank)
        ]

    def shuffle_deck(self):
        """Shuffle all remaining cards."""

        shuffle(self.cards)

    def deal(self, n: int = 1) -> list[Card]:
        """Deal n cards from top of the deck."""
        
        if len(self.cards) < n:
            raise ValueError("No enough cards to deal.")

        cards = []
        for i in range(n):
            cards.append(self.cards.pop())

        return cards if n != 1 else cards[0]

    def reset(self):
        """Start the deck anew, but shuffled."""

        self.cards = [
            Card(r, s) for s in list(CardSuit) for r in list(CardRank)
        ]
        self.shuffle_deck()