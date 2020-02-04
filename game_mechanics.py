import math
from twilight_map import *

class Game:

    # you can now refer to USSR and USA as Game.Side.USSR / Game.Side.USA
    # without concern about which is 0 and which is 1; also robust to
    # change any time.
    class Side:
        USSR = 0
        USA = 1
        
        @staticmethod
        def fromStr(s):
            if s.lower() == "usa": return Game.Side.USA
            elif s.lower() == "ussr": return Game.Side.USSR
            else: raise NameError("Invalid string for Game.Side.fromStr")

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
        
        # For new set the first created game to be the actual ongoing game.
        if Game.main is None: Game.main = self

# to add game terminate functionality EndGame()

    def change_vp(self, n): # positive for ussr
        self.vp_track += n
        if self.vp_track >= 20:
            print('USSR victory')
            # EndGame()
        if self.vp_track <= -20:
            print('US victory')
            # EndGame()

    def change_defcon(n):
        self.defcon_track += min(n, 5 - self.defcon_track)
        if self.defcon_track < 2:
            print('Game ended by thermonuclear war')
            # EndGame()

# SPACE (function)
def space(side):

    x = Game.Side.fromStr(side)
    
    # this one could be something game specific later
    space_track = Game.main.space_track

    if space_track[x] in [0,2,4,6]:
        modifier = 0
    elif space_track[x] in [1,3,5]:
        modifier = -1
    else:
        modifier = 1

    y = 1 - 2*x # multiplier for VPs - gives 1 for USSR and -1 for US
    roll = np.random.randint(6) + 1
    if roll + modifier <= 3:
        space_track[x] += 1
        print(f'Success with roll of {roll}.')

        if space_track[x] == 1:
            if space_track[1-x] < 1:
                change_vp(2*y)
            else:
                change_vp(y)

        elif space_track[x] == 3:
            if space_track[1-x] < 3:
                change_vp(2*y)

        elif space_track[x] == 5:
            if space_track[1-x] < 5:
                change_vp(3*y)
            else:
                change_vp(y)

        elif space_track[x] == 7:
            if space_track[1-x] < 7:
                change_vp(4*y)
            else:
                change_vp(2*y)

        elif space_track[x] == 8:
            if space_track[1-x] < 8:
                change_vp(2*y)

    else:
        print(f'Failure with roll of {roll}.')

# definitely want to make all the country states be stored in the specific Game object

def DegradeDEFCONLevel(n):
    Game.main.change_defcon(-n)

def GainVictoryPointsForDEFCONBelow(n):
    Game.main.change_vp(defcon_track - n)

def RemoveAllOpponentInfluenceInCuba(_):
    Cuba.set_influence(0, max(3, Cuba.ussr_influence))

def RemoveAllOpponentInfluenceInRomania(_):
    Romania.set_influence(0, max(3, Cuba.ussr_influence))

def GainInfluenceInEgypt(_):
    Egypt.adjust_influence(-math.ceil(Egypt.us_influence/2), 2)

def RemoveOpponentInfluenceInFrance(_):
    France.adjust_influence(-2, 1)

def GainInfluenceForControlInJapan(_):
    Japan.set_influence(Japan.ussr_influence + 4, Japan.ussr_influence)


'''Scoring Mechanics'''
# TO ADD SHUTTLE DIPLOMACY AND FORMOSAN RESOLUTION
def ScoreAsia(_):

    areas = []
    for x in list(all_countries.values()):
        if x.region in ["Asia", "Southeast Asia"]:
            areas.append(x)

    presence, domination, control = [3,7,9]

    bg_count = [0,0] # USSR, US
    country_count = [0,0]
    bgs = 0

    for x in areas:
        bg_count[0] += (x.battleground and x.control == 'ussr')
        bg_count[1] += (x.battleground and x.control == 'us')
        country_count[0] += (x.control == 'ussr')
        country_count[1] += (x.control == 'us')
        bgs += x.battleground

    swing = bg_count[0] - bg_count[1]

    # presence
    if country_count[0] > 0:
        swing += presence
    if country_count[1] > 0:
        swing -= presence

    # control
    if bg_count[0] == bgs:
        swing += control - presence
    if bg_count[1] == bgs:
        swing -= control - presence

    # domination
    if bg_count[0] < bgs and bg_count[0] > bg_count[1] and country_count[0] > country_count[1] and country_count[0] - bg_count[0] > 0:
        swing += domination - presence
    if bg_count[1] < bgs and bg_count[1] > bg_count[0] and country_count[1] > country_count[0] and country_count[1] - bg_count[1] > 0:
        swing -= domination - presence

    # adjacent
    if Afghanistan.control == 'us':
        swing -= 1
    if North_Korea.control == 'us':
        swing -= 1

    Game.main.change_vp(swing)
    print(f'Asia scores for {swing} VPs')

def ScoreEurope(_):

    areas = []
    for x in list(all_countries.values()):
        if x.region in ["Europe", "Western Europe", "Eastern Europe"]:
            areas.append(x)

    presence, domination, control = [3,7,120]

    bg_count = [0,0] # USSR, US
    country_count = [0,0]
    bgs = 0

    for x in areas:
        bg_count[0] += (x.battleground and x.control == 'ussr')
        bg_count[1] += (x.battleground and x.control == 'us')
        country_count[0] += (x.control == 'ussr')
        country_count[1] += (x.control == 'us')
        bgs += x.battleground

    swing = bg_count[0] - bg_count[1]

    # presence
    if country_count[0] > 0:
        swing += presence
    if country_count[1] > 0:
        swing -= presence

    # control
    if bg_count[0] == bgs:
        swing += control - presence
    if bg_count[1] == bgs:
        swing -= control - presence

    # domination
    if bg_count[0] < bgs and bg_count[0] > bg_count[1] and country_count[0] > country_count[1] and country_count[0] - bg_count[0] > 0:
        swing += domination - presence
    if bg_count[1] < bgs and bg_count[1] > bg_count[0] and country_count[1] > country_count[0] and country_count[1] - bg_count[1] > 0:
        swing -= domination - presence

    # adjacent
    if Canada.control == 'ussr':
        swing += 1
    if Finland.control == 'us':
        swing -= 1
    if Poland.control == 'us':
        swing -= 1
    if Romania.control == 'us':
        swing -= 1

    Game.main.change_vp(swing)
    print(f'Europe scores for {swing} VPs')

# TO ADD SHUTTLE DIPLOMACY
def ScoreMiddleEast(_):

    areas = []
    for x in list(all_countries.values()):
        if x.region == "Middle East":
            areas.append(x)

    presence, domination, control = [3,5,7]

    bg_count = [0,0] # USSR, US
    country_count = [0,0]
    bgs = 0

    for x in areas:
        bg_count[0] += (x.battleground and x.control == 'ussr')
        bg_count[1] += (x.battleground and x.control == 'us')
        country_count[0] += (x.control == 'ussr')
        country_count[1] += (x.control == 'us')
        bgs += x.battleground

    swing = bg_count[0] - bg_count[1]

    # presence
    if country_count[0] > 0:
        swing += presence
    if country_count[1] > 0:
        swing -= presence

    # control
    if bg_count[0] == bgs:
        swing += control - presence
    if bg_count[1] == bgs:
        swing -= control - presence

    # domination
    if bg_count[0] < bgs and bg_count[0] > bg_count[1] and country_count[0] > country_count[1] and country_count[0] - bg_count[0] > 0:
        swing += domination - presence
    if bg_count[1] < bgs and bg_count[1] > bg_count[0] and country_count[1] > country_count[0] and country_count[1] - bg_count[1] > 0:
        swing -= domination - presence

    Game.main.change_vp(swing)
    print(f'Middle East scores for {swing} VPs')

def ScoreCentralAmerica(_):

    areas = []
    for x in list(all_countries.values()):
        if x.region == "Central America":
            areas.append(x)

    presence, domination, control = [1,3,5]

    bg_count = [0,0] # USSR, US
    country_count = [0,0]
    bgs = 0

    for x in areas:
        bg_count[0] += (x.battleground and x.control == 'ussr')
        bg_count[1] += (x.battleground and x.control == 'us')
        country_count[0] += (x.control == 'ussr')
        country_count[1] += (x.control == 'us')
        bgs += x.battleground

    swing = bg_count[0] - bg_count[1]

    # presence
    if country_count[0] > 0:
        swing += presence
    if country_count[1] > 0:
        swing -= presence

    # control
    if bg_count[0] == bgs:
        swing += control - presence
    if bg_count[1] == bgs:
        swing -= control - presence

    # domination
    if bg_count[0] < bgs and bg_count[0] > bg_count[1] and country_count[0] > country_count[1] and country_count[0] - bg_count[0] > 0:
        swing += domination - presence
    if bg_count[1] < bgs and bg_count[1] > bg_count[0] and country_count[1] > country_count[0] and country_count[1] - bg_count[1] > 0:
        swing -= domination - presence

    # adjacent
    if Cuba.control == 'ussr':
        swing += 1
    if Mexico.control == 'ussr':
        swing += 1

    Game.main.change_vp(swing)
    print(f'Central America scores for {swing} VPs')

def ScoreSoutheastAsia(_):
    areas = []
    for x in list(all_countries.values()):
        if x.region == "Southeast Asia":
            areas.append(x)
    print(areas)

    country_count = [0,0]
    for x in areas:
        country_count[0] += (x.control == 'ussr')
        country_count[1] += (x.control == 'us')
    swing = country_count[0] - country_count[1]

    # thailand double VP
    if Thailand.control == 'ussr':
        swing += 1
    if Thailand.control == 'us':
        swing -= 1

    Game.main.change_vp(swing)
    print(f'Southeast Asia scores for {swing} VPs')

def ScoreAfrica(_):

    areas = []
    for x in list(all_countries.values()):
        if x.region == "Africa":
            areas.append(x)

    presence, domination, control = [1,4,6]

    bg_count = [0,0] # USSR, US
    country_count = [0,0]
    bgs = 0

    for x in areas:
        bg_count[0] += (x.battleground and x.control == 'ussr')
        bg_count[1] += (x.battleground and x.control == 'us')
        country_count[0] += (x.control == 'ussr')
        country_count[1] += (x.control == 'us')
        bgs += x.battleground

    swing = bg_count[0] - bg_count[1]

    # presence
    if country_count[0] > 0:
        swing += presence
    if country_count[1] > 0:
        swing -= presence

    # control
    if bg_count[0] == bgs:
        swing += control - presence
    if bg_count[1] == bgs:
        swing -= control - presence

    # domination
    if bg_count[0] < bgs and bg_count[0] > bg_count[1] and country_count[0] > country_count[1] and country_count[0] - bg_count[0] > 0:
        swing += domination - presence
    if bg_count[1] < bgs and bg_count[1] > bg_count[0] and country_count[1] > country_count[0] and country_count[1] - bg_count[1] > 0:
        swing -= domination - presence

    Game.main.change_vp(swing)
    print(f'Africa scores for {swing} VPs')

def ScoreSouthAmerica(_):

    areas = []
    for x in list(all_countries.values()):
        if x.region == "South America":
            areas.append(x)

    presence, domination, control = [2,5,6]

    bg_count = [0,0] # USSR, US
    country_count = [0,0]
    bgs = 0

    for x in areas:
        bg_count[0] += (x.battleground and x.control == 'ussr')
        bg_count[1] += (x.battleground and x.control == 'us')
        country_count[0] += (x.control == 'ussr')
        country_count[1] += (x.control == 'us')
        bgs += x.battleground

    swing = bg_count[0] - bg_count[1]

    # presence
    if country_count[0] > 0:
        swing += presence
    if country_count[1] > 0:
        swing -= presence

    # control
    if bg_count[0] == bgs:
        swing += control - presence
    if bg_count[1] == bgs:
        swing -= control - presence

    # domination
    if bg_count[0] < bgs and bg_count[0] > bg_count[1] and country_count[0] > country_count[1] and country_count[0] - bg_count[0] > 0:
        swing += domination - presence
    if bg_count[1] < bgs and bg_count[1] > bg_count[0] and country_count[1] > country_count[0] and country_count[1] - bg_count[1] > 0:
        swing -= domination - presence

    Game.main.change_vp(swing)
    print(f'South America scores for {swing} VPs')
