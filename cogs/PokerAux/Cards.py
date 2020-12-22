"""
Auxiliary module for the Poker Cog. This module defines classes related to
poker cards and deck.
"""


from enum import Enum, IntEnum, unique
from random import shuffle
from typing import List, Tuple


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
        return str(self.value) if self <= CardRank.ten else self.name[0].upper()


@unique
class CardSuit(Enum):
    """One of the four playing suits."""

    spades      = 1
    hearts      = 2
    diamonds    = 3
    clubs       = 4

    def __str__(self) -> str:
        """Return the appropriate code for the suit's Discord emoji."""

        return f':{self.name}:'


class Card:
    """A playing card."""

    def __init__(self, rank: CardRank, suit: CardSuit) -> None:
        self.rank = rank
        self.suit = suit

    def pec(self) -> Tuple[int, int]:
        """Return a tuple that can be used to construct a pokereval.Card."""

        return (self.rank.value, self.suit.value)

    def __str__(self) -> str:
        return f"{self.rank} {self.suit}"


class Deck:
    """A standard 52-card deck."""

    def __init__(self) -> None:
        self.cards = [
            Card(r, s) for s in list(CardSuit) for r in list(CardRank)
        ]

    def shuffle_deck(self) -> None:
        """Shuffle all remaining cards."""

        shuffle(self.cards)

    def deal(self, n: int = 1) -> List[Card]:
        """Deal n cards from top of the deck."""
        
        if len(self.cards) < n:
            raise ValueError("No enough cards to deal.")

        cards = [self.cards.pop() for _ in range(n)]

        return cards

    def reset(self) -> None:
        """Start the deck anew, but shuffled."""

        self.cards = [
            Card(r, s) for s in list(CardSuit) for r in list(CardRank)
        ]
        self.shuffle_deck()