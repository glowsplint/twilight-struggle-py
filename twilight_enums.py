import enum

# you can now refer to USSR and USA as Side.USSR / Side.USA / Side.NEUTRAL
# without concern about which is 0 and which is 1; also robust to
# change any time.

class Side(enum.IntEnum):

    USSR = 0
    USA = 1
    NEUTRAL = 2

    @staticmethod
    def fromStr(s):
        if s.lower() == "usa":
            return Side.USA
        elif s.lower() == "ussr":
            return Side.USSR
        elif s.lower() == "neutral":
            return Side.NEUTRAL
        else:
            raise NameError("Invalid string for Side.fromStr")

    @property
    def opp(self):
        if self == Side.USSR: return Side.USA
        elif self == Side.USA: return Side.USSR
        else: return Side.NEUTRAL

    @property
    def vp_mult(self):
        if self == Side.USSR: return 1
        elif self == Side.USA: return -1
        else: return 0


class MapRegion(enum.IntEnum):

    EUROPE = 0
    ASIA = 1
    MIDDLE_EAST = 2
    AFRICA = 3
    CENTRAL_AMERICA = 4
    SOUTH_AMERICA = 5
    # Subregions
    WESTERN_EUROPE = 6
    EASTERN_EUROPE = 7
    SOUTHEAST_ASIA = 8

    @staticmethod
    def fromStr(inStr):
        s = inStr.lower()
        if s == "europe" or s == "eu":
            return MapRegion.EUROPE
        elif s == "asia" or s == "as":
            return MapRegion.ASIA
        elif s == "middle east" or s == "me":
            return MapRegion.MIDDLE_EAST
        elif s == "africa" or s == "af":
            return MapRegion.AFRICA
        elif s == "central america" or s == "ca":
            return MapRegion.CENTRAL_AMERICA
        elif s == "south america" or s == "sa":
            return MapRegion.SOUTH_AMERICA
        elif s == "western europe" or s == "we":
            return MapRegion.WESTERN_EUROPE
        elif s == "eastern europe" or s == "ee":
            return MapRegion.EASTERN_EUROPE
        elif s == "southeast asia" or s == "se":
            return MapRegion.SOUTHEAST_ASIA
        else:
            raise NameError("Invalid string for MapRegion.fromStr")
