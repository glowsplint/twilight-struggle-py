import math
import random
import numpy as np

from twilight_enums import *
from twilight_map import *
from twilight_cards import *

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
        self.ar_track = 1 # increment by 1 for each side's action round
        self.defcon_track = 5
        self.milops_track = np.array([0, 0]) # ussr first
        self.space_track = np.array([0, 0]) # 0 is start, 1 is earth satellite etc
        self.has_spaced = [False, False]
        self.map = GameMap()
        self.cards = GameCards()
        self.US_hand = []
        self.USSR_hand = []
        self.removed_pile = []
        self.discard_pile = []
        self.draw_pile = []

        # For new set the first created game to be the actual ongoing game.
        if Game.main is None: Game.main = self

    # to add game terminate functionality EndGame()

    def start(self):
        self.map.build_standard()
        self.deal()

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

    def deal(self):
        def top_up_cards(self, n):
            ussr_held = len(self.USSR_hand)
            us_held = len(self.US_hand)

            if 'The_China_Card' in self.USSR_hand: # Ignore China Card if it is in either hand
                ussr_held = len(self.USSR_hand) - 1
            elif 'The_China_Card' in self.USSR_hand:
                us_held = len(self.US_hand) - 1

            # if turn 4, add mid war cards into draw pile and shuffle, same for turn 8 for late war cards
            if self.turn_track == 4:
                self.draw_pile.extend(self.cards.Mid_War)
                self.cards.Mid_War = []
                random.shuffle(self.draw_pile)
            if self.turn_track == 8:
                self.draw_pile.extend(self.cards.Late_War)
                self.cards.Late_War = []
                random.shuffle(self.draw_pile)

            # exhaust the draw pile
            while ussr_held < n or us_held < n:
                # if draw pile exhausted, shuffle the discard pile and put it as the new draw pile
                def recreate_draw_pile():
                    if self.draw_pile == []:
                        self.draw_pile = self.discard_pile
                        self.discard_pile = []
                        random.shuffle(self.draw_pile)
                if ussr_held < n:
                    self.USSR_hand.extend([self.draw_pile.pop()])
                    ussr_held += 1
                    recreate_draw_pile()
                if us_held < n:
                    self.US_hand.extend([self.draw_pile.pop()])
                    us_held += 1
                    recreate_draw_pile()

        '''Pre-headline setup'''
        if self.turn_track == 1 and self.ar_track == 1:
            # Move the China card from the early war pile to USSR hand, China card 6th from last
            self.USSR_hand.append(self.cards.Early_War.pop(5))
            self.draw_pile.extend(self.cards.Early_War) # Put early war cards into the draw pile
            self.cards.Early_War = []
            random.shuffle(self.draw_pile) # Shuffle the draw pile
            top_up_cards(self, 8)
        else:
            if self.turn_track in [1,2,3]:
                top_up_cards(self, 8)
            else:
                top_up_cards(self, 9)

    # need to make sure next_turn is only called after all extra rounds
    def next_turn(self):
        # played at the end of last US action round within turn
        # 1. Check milops
        def check_milops(self):
            milops_diff = self.milops_track - self.defcon_track
            milops_vp_change = np.where(milops_diff < 0, milops_diff, 0)
            swing = milops_vp_change[0] - milops_vp_change[1]
            self.change_vp(swing)

        # 2. Check for held scoring card
        def check_for_scoring_cards(self):
            scoring_list = ['Asia_Scoring', 'Europe_Scoring', 'Middle_East_Scoring', 'Central_America_Scoring', 'Southeast_Asia_Scoring', 'Africa_Scoring', 'South_America_Scoring']
            scoring_cards = [self.cards[y] for y in scoring_list]
            if any(True for x in scoring_cards if x in self.US_hand):
                print('USSR Victory!')
                # EndGame()
            elif any(True for x in scoring_cards if x in self.USSR_hand):
                print('US Victory!')
                # EndGame()

        # 3. Flip China Card
        def flip_china_card(self):
            if 'The_China_Card' in self.USSR_hand:
                self.USSR_hand[self.USSR_hand.index('The_China_Card')].flipped = False
            else:
                self.US_hand[self.US_hand.index('The_China_Card')].flipped = False

        # 4. Advance turn marker
        def advance_turn_marker(self):
            self.turn_track += 1
            self.ar_track = 1

        # 5. Final scoring (end T10)
        def final_scoring(self):
            if self.turn_track == 10 and (self.ar_track in [15,16,17]):
                ScoreAsia(0)
                ScoreEurope(0)
                ScoreMiddleEast(0)
                ScoreCentralAmerica(0)
                ScoreAfrica(0)
                ScoreSouthAmerica(0)
            print(f'Final scoring complete.')
            # EndGame()

        # 6. Increase DEFCON status
        def improve_defcon_status():
            self.change_defcon(1)

        # 7. Deal Cards -- written outside the next_turn function
        # 8. Headline Phase
        def headline(self):
            pass

        # 9. Action Rounds (advance round marker) -- action rounds are not considered between turns

        check_milops(self)
        check_for_scoring_cards(self)
        flip_china_card(self)
        advance_turn_marker(self) #turn marker advanced before final scoring
        final_scoring(self)
        improve_defcon_status()
        deal(self) # turn marker advanced before dealing
        headline(self)

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
                elif bg_count[s] > bg_count[s.opp] and country_count[s] > bg_count[s]:
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
def ScoreAsia():
    Game.main.score(MapRegion.ASIA, 3, 7, 9)

def ScoreEurope():
    Game.main.score(MapRegion.EUROPE, 3, 7, 120)

# TO ADD SHUTTLE DIPLOMACY
def ScoreMiddleEast():
    Game.main.score(MapRegion.MIDDLE_EAST, 3, 5, 7)

def ScoreCentralAmerica():
    Game.main.score(MapRegion.CENTRAL_AMERICA, 1, 3, 5)

def ScoreAfrica():
    Game.main.score(MapRegion.AFRICA, 1, 4, 6)

def ScoreSouthAmerica():
    Game.main.score(MapRegion.AFRICA, 2, 5, 6)

def ScoreSoutheastAsia():
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
