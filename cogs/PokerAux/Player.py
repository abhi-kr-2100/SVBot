"""
Auxiliary module for the Poker Cog. This module defines classes related to
poker players.
"""


from enum import Enum, auto, unique
from typing import List, Optional

from .Cards import Card

import discord


@unique
class PlayerStatus(Enum):
    """Player's status based on sitting position."""

    small_blind     = auto()
    big_blind       = auto()
    dealer          = auto()
    normal          = auto()
    small_dealer    = auto()    # when there are only two players


class Player:
    """A poker player."""

    def __init__(self, member: discord.Member, chips: int,
                    status: PlayerStatus = PlayerStatus.normal) -> None:
        self.member = member
        self.chips  = chips
        self.status = status

        # is the player still playing
        self.active = True

        # the player hasn't has his/her turn in the round yet
        # this attribute is used to only indicate whether the player has made
        # his/her first move yet or not
        self.turn_pending = False
        
        # has the player folded for this round
        self.not_folded = True

        # if the player went all in this round
        self.all_in = False

        # how much the player has betted this round
        self.betted = 0

        self.hole_cards: Optional[List[Card]] = None