import enum
from typing import Iterable, Callable
# you can now refer to USSR and US as Side.USSR / Side.US / Side.NEUTRAL
# without concern about which is 0 and which is 1; also robust to
# change any time.


class Side(enum.IntEnum):

    USSR = 0
    US = 1
    NEUTRAL = 2

    @staticmethod
    def fromStr(s):
        if s.lower() == 'us':
            return Side.US
        elif s.lower() == 'ussr':
            return Side.USSR
        elif s.lower() == 'neutral':
            return Side.NEUTRAL
        else:
            raise NameError('Invalid string for Side.fromStr')

    def toStr(self):
        if self == Side.US:
            return 'US'
        elif self == Side.USSR:
            return 'USSR'
        else:
            return 'NEUTRAL'

    @property
    def opp(self):
        if self == Side.USSR:
            return Side.US
        elif self == Side.US:
            return Side.USSR
        else:
            return Side.NEUTRAL

    @property
    def vp_mult(self):
        if self == Side.USSR:
            return 1
        elif self == Side.US:
            return -1
        else:
            return 0


class MapRegion(enum.IntEnum):

    EUROPE = 0
    ASIA = 1
    MIDDLE_EAST = 2
    AFRICA = 3
    CENTRAL_AMERICA = 4
    SOUTH_AMERICA = 5

    WESTERN_EUROPE = 6
    EASTERN_EUROPE = 7
    SOUTHEAST_ASIA = 8

    @staticmethod
    def fromStr(inStr):
        s = inStr.lower()
        if s == 'europe' or s == 'eu':
            return MapRegion.EUROPE
        elif s == 'asia' or s == 'as':
            return MapRegion.ASIA
        elif s == 'middle east' or s == 'me':
            return MapRegion.MIDDLE_EAST
        elif s == 'africa' or s == 'af':
            return MapRegion.AFRICA
        elif s == 'central america' or s == 'ca':
            return MapRegion.CENTRAL_AMERICA
        elif s == 'south america' or s == 'sa':
            return MapRegion.SOUTH_AMERICA
        elif s == 'western europe' or s == 'we':
            return MapRegion.WESTERN_EUROPE
        elif s == 'eastern europe' or s == 'ee':
            return MapRegion.EASTERN_EUROPE
        elif s == 'southeast asia' or s == 'se':
            return MapRegion.SOUTHEAST_ASIA
        else:
            raise NameError('Invalid string for MapRegion.fromStr')


class InputType(enum.IntEnum):

    COMMIT = 0
    ROLL_DICE = 1

    # these should have a list of text options.
    SELECT_CARD_ACTION = 3  # Realign, coup, space, event, etc.
    SELECT_CARD = 4
    SELECT_COUNTRY = 5
    SELECT_MULTIPLE = 6


class CardAction(enum.IntEnum):

    PLAY_EVENT = 0,
    RESOLVE_EVENT_FIRST = 1
    INFLUENCE = 2
    REALIGNMENT = 3
    COUP = 4
    SPACE = 5
