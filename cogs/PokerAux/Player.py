"""
Auxiliary module for the Poker Cog. This module defines classes related to
poker players.
"""


from enum import Enum, auto, unique


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

    def __init__(self, member, chips, status=PlayerStatus.normal):
        self.member = member
        self.chips = chips
        self.status = status

        # is the player still playing
        self.active = True
        
        # the player hasn't has his/her turn in the round yet
        self.turn_pending = False
        
        # has the player folded for this round
        self.not_folded = True

        # if the player went all in this round
        self.all_in = False

        # how much the player has betted this round
        self.betted = 0

        self.hole_cards = None