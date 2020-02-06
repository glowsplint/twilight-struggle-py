import math
import random
from twilight_enums import *
from twilight_map import *

class Game:

    # this is the currently active game. One may refer to this as
    # Game.main. The point is to have a globally accessible game
    # object for the active game, but still allow for other game
    # objects to deal with hypothetical future/past game states
    # which would be useful for non-committed actions and possibly
    # the AI depending on how you do it.
    main = None

    '''VP, AR, Milops, Space tracks'''
    def __init__(self):
        self.vp_track = 0 # positive for ussr
        self.turn_track = 1
        self.ar_track = 1 # increment by 0.5 for each side's action round
        self.defcon_track = 5
        self.milops_track = [0, 0] # ussr first
        self.space_track = [0, 0] # 0 is start, 1 is earth satellite etc
        self.map = GameMap()
        
        # For new set the first created game to be the actual ongoing game.
        if Game.main is None: Game.main = self

# to add game terminate functionality EndGame()

    def start(self):
        self.map.build_standard()

    def change_vp(self, n): # positive for ussr
        self.vp_track += n
        if self.vp_track >= 20:
            print('USSR victory')
            # EndGame()
        if self.vp_track <= -20:
            print('US victory')
            # EndGame()

    def change_defcon(self, n):
        self.defcon_track += min(n, 5 - self.defcon_track)
        if self.defcon_track < 2:
            print('Game ended by thermonuclear war')
            # EndGame()

# SPACE (function)
    def space(self, side):

        x = Side.fromStr(side)

        # this one could be something game specific later
        space_track = self.space_track

        if space_track[x] in [0,2,4,6]:
            modifier = 0
        elif space_track[x] in [1,3,5]:
            modifier = -1
        else:
            modifier = 1

        y = x.vp_mult # multiplier for VPs - gives 1 for USSR and -1 for US
        roll = random.randint(6) + 1
        if roll + modifier <= 3:
            space_track[x] += 1
            print(f'Success with roll of {roll}.')

            if space_track[x] == 1:
                if space_track[x.opp] < 1:
                    self.change_vp(2*y)
                else:
                    self.change_vp(y)

            elif space_track[x] == 3:
                if space_track[x.opp] < 3:
                    self.change_vp(2*y)

            elif space_track[x] == 5:
                if space_track[x.opp] < 5:
                    self.change_vp(3*y)
                else:
                    self.change_vp(y)

            elif space_track[x] == 7:
                if space_track[x.opp] < 7:
                    self.change_vp(4*y)
                else:
                    self.change_vp(2*y)

            elif space_track[x] == 8:
                if space_track[x.opp] < 8:
                    self.change_vp(2*y)

        else:
            print(f'Failure with roll of {roll}.')

    def score(self, region, presence_vps, domination_vps, control_vps):

        bg_count = [0, 0, 0]  # USSR, USA, NEUTRAL
        country_count = [0, 0, 0]
        vps = [0, 0]

        for n in CountryInfo.REGION_ALL[region]:
            x = self.map[n]
            if x.info.battleground:
                bg_count[x.control] += 1
            country_count[x.control] += 1
            if x.control.opp.name in x.info.adjacent_countries:
                vps[x.control] += 1

        for s in [Side.USSR, Side.USA]:
            vps[s] += bg_count[s]
            if country_count[s] > country_count[s.opp]:
                if bg_count[s] == sum(bg_count):
                    vps[s] += control_vps
                elif bg_count[s] > bg_count[s.opp]:
                    vps[s] += domination_vps
            elif country_count[s] > 0:
                vps[s] += presence_vps

        swing = vps[Side.USSR] - vps[Side.USA]
        self.change_vp(swing)
        print(f'{region.name} scores for {swing} VPs')
# definitely want to make all the country states be stored in the specific Game object

def DegradeDEFCONLevel(n):
    Game.main.change_defcon(-n)

def GainVictoryPointsForDEFCONBelow(n):
    Game.main.change_vp(Game.main.defcon_track - n)

def RemoveAllOpponentInfluenceInCuba(_):
    Cuba.set_influence(0, max(3, Cuba.ussr_influence))

def RemoveAllOpponentInfluenceInRomania(_):
    Romania.set_influence(0, max(3, Romania.ussr_influence))

def GainInfluenceInEgypt(_):
    Egypt.adjust_influence(-math.ceil(Egypt.us_influence/2), 2)

def RemoveOpponentInfluenceInFrance(_):
    France.adjust_influence(-2, 1)

def GainInfluenceForControlInJapan(_):
    Japan.set_influence(Japan.ussr_influence + 4, Japan.ussr_influence)


'''Scoring Mechanics'''
# TO ADD SHUTTLE DIPLOMACY AND FORMOSAN RESOLUTION
def ScoreAsia(_):
    Game.main.score(MapRegion.ASIA, 3, 7, 9)

def ScoreEurope(_):
    Game.main.score(MapRegion.EUROPE, 3, 7, 120)

# TO ADD SHUTTLE DIPLOMACY
def ScoreMiddleEast(_):
    Game.main.score(MapRegion.MIDDLE_EAST, 3, 5, 7)

def ScoreCentralAmerica(_):
    Game.main.score(MapRegion.CENTRAL_AMERICA, 1, 3, 5)

def ScoreAfrica(_):
    Game.main.score(MapRegion.AFRICA, 1, 4, 6)

def ScoreSouthAmerica(_):
    Game.main.score(MapRegion.AFRICA, 2, 5, 6)

def ScoreSoutheastAsia(_):

    country_count = [0,0]
    for n in CountryInfo.REGION_ALL[MapRegion.SOUTHEAST_ASIA]:
        x = Game.main.map[n]
        country_count[Side.USSR] += (x.control == Side.USSR)
        country_count[Side.USA] += (x.control == Side.USA)
    swing = country_count[Side.USSR] - country_count[Side.USA]

    # thailand double VP
    if Game.main.map['Thailand'].control == Side.USSR:
        swing += 1
    if Game.main.map['Thailand'].control == Side.USA:
        swing -= 1

    Game.main.change_vp(swing)
    print(f'Southeast Asia scores for {swing} VPs')
