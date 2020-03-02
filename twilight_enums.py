import enum
from typing import Iterable, Callable

class TrackEffects():

    def __init__(self, defcon: int=0, vp: int=0, milops: int=0):
        self.defcon = defcon
        self.vp = vp
        self.milops = milops

    def __iadd__(self, other):
        self.defcon += other.defcon
        self.vp += other.vp
        self.milops += other.milops
        return self

    def __repr__(self):
        items = []
        if self.defcon:
            items.append(f'DEFCON {self.defcon:+}')

        if self.vp:
            items.append(f'VP {self.vp:+}')

        if self.milops:
            items.append(f'Mil. Ops. {self.milops:+}')

        return '; '.join(items)

class CoupEffects(TrackEffects):

    def __init__(self, no_milops: bool=False, no_defcon_bg: bool=False, **kwargs):
        super().__init__(**kwargs)
        self.no_milops = no_milops
        self.no_defcon_bg = no_defcon_bg

    def __iadd__(self, other):
        super().__iadd__(other)
        self.no_milops = self.no_milops or other.no_milops
        self.no_defcon_bg = self.no_defcon_bg or other.no_defcon_bg
        return self

    def __repr__(self):
        items = []
        prefix = super().__repr__()

        if prefix: items.append(prefix)
        if self.no_milops:
            items.append('No mil. ops. gained')

        if self.no_defcon_bg:
            items.append('No DEFCON reduction for battlegrounds')

        return '; '.join(items)


class Side(enum.IntEnum):

    USSR = 0
    US = 1
    NEUTRAL = 2

    @classmethod
    def PLAYERS(cls):
        return (cls.USSR, cls.US)

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

    @classmethod
    def main_regions(self):
        return [MapRegion.EUROPE, MapRegion.ASIA, MapRegion.MIDDLE_EAST, MapRegion.AFRICA, MapRegion.CENTRAL_AMERICA, MapRegion.SOUTH_AMERICA]


class InputType(enum.IntEnum):

    COMMIT = 0
    ROLL_DICE = 1

    # these should have a list of text options.
    SELECT_CARD_ACTION = 3  # Realign, coup, space, event, etc.
    SELECT_CARD = 4
    SELECT_COUNTRY = 5
    SELECT_MULTIPLE = 6


class CardAction(enum.IntEnum):

    PLAY_EVENT = 0
    RESOLVE_EVENT_FIRST = 1
    INFLUENCE = 2
    REALIGNMENT = 3
    COUP = 4
    SPACE = 5
    SKIP_OPTIONAL_AR = 6
