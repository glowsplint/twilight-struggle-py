#!/usr/bin/env python
# coding: utf-8

# ### Twilight Struggle

# In[ ]:


import pandas as pd
import numpy as np
import random
from twilight_map import *


# In[ ]:


all_countries = dict()


# In[ ]:


class country:
    def __init__(self, country_name, country_index, adjacent_countries, us_influence, ussr_influence, region=0, stability=0, battleground=False, superpower=False, chinese_civil_war=False):
        self.country_name = country_name
        self.country_index = country_index
        self.region = region
        self.stability = stability
        self.battleground = battleground
        self.adjacent_countries = adjacent_countries
        self.us_influence = us_influence
        self.ussr_influence = ussr_influence
        self.superpower = superpower
        self.chinese_civil_war = chinese_civil_war
        self.evaluate_control()
        all_countries[country_name] = self

    def evaluate_control(self):
        if self.us_influence - self.ussr_influence >= self.stability:
            self.control = 'us'
        elif self.ussr_influence - self.us_influence >= self.stability:
            self.control = 'ussr'
        else:
            self.control = 'none'

    def __repr__(self):
        if self.stability == 0:
            return f'country({self.country_name}, adjacent = {self.adjacent_countries})'
        else:
            return f'country({self.country_name}, region = {self.region}, stability = {self.stability}, battleground = {self.battleground}, adjacent = {self.adjacent_countries}, us_inf = {self.us_influence}, ussr_inf = {self.ussr_influence}), control = {self.control}'

    def set_influence(self, us_influence, ussr_influence):
        if self.superpower == True:
            raise ValueError('Cannot set influence on superpower!')
        self.us_influence = us_influence
        self.ussr_influence = ussr_influence
        self.evaluate_control()

    def reset_influence(self):
        self.us_influence, self.ussr_influence = 0, 0
        self.evaluate_control()

    def adjust_influence(self, us_influence, ussr_influence):
        self.us_influence += us_influence
        self.ussr_influence += ussr_influence
        self.evaluate_control()

    def place_influence(self, side, effective_operations_points):
        if side == 'ussr' and self.control == 'us':
            # here we deduct 2 from effective_operations_points, to place 1 influence in the country, and then call the function again
            if effective_operations_points >= 2:
                self.adjust_influence(0, 1)
            else:
                raise ValueError('Not enough operations points!')
            if effective_operations_points - 2 > 0:
                self.place_influence(side, effective_operations_points - 2)
        elif side == 'us' and self.control == 'ussr':
            if effective_operations_points >= 2:
                self.adjust_influence(1, 0)
            else:
                raise ValueError('Not enough operations points!')
            if effective_operations_points - 2 > 0:
                self.place_influence(side, effective_operations_points - 2)
        else:
            if side == 'us':
                self.adjust_influence(effective_operations_points, 0)
            elif side == 'ussr':
                self.adjust_influence(0, effective_operations_points)
            else:
                raise ValueError("side must be 'us' or 'ussr'!")

    def coup(self, side, effective_operations_points):
        '''
        TODO:
        1. Prevent coup if no opposing influence in the country. I would prefer to write this in a way that prevents this from happening altogether, as opposed to throwing up an error if this is tried.
        2. Prevent coup under DEFCON restrictions. Will write it in a style same as 1.
        3. Prevent coup if there is no influence at all in the country.
        4. Add military operations points.
        5. Reduce DEFCON status level if self.battleground = True
        '''

        die_roll = np.random.randint(6) + 1
        difference = die_roll + effective_operations_points - self.stability*2
        if difference > 0:
            if side == 'us':
                # subtract from opposing first.. and then add to yours
                if difference > self.ussr_influence:
                    self.adjust_influence(difference - self.ussr_influence, 0)
                self.adjust_influence(0, -min(difference, self.us_influence))

            if side == 'ussr':
                if difference > self.us_influence:
                    self.adjust_influence(0, difference - self.us_influence)
                self.adjust_influence(-min(difference, self.us_influence), 0)
            print(f'Coup successful with roll of {die_roll}. Difference: {difference}')
        else:
            print(f'Coup failed with roll of {die_roll}')
        self.evaluate_control()
    
    def realignment(self):
        '''
        TODO:
        1. Prevent realignment under DEFCON restrictions.
        2. Prevent realignment if there is no influence at all in the country.
        '''
        
        modifier = 0
        for adjacent_country in self.adjacent_countries:
            modifier += ((all_countries[adjacent_country.country_name]).control == 'us')
            modifier -= ((all_countries[adjacent_country.country_name]).control == 'ussr')
        if self.us_influence - self.ussr_influence > 0:
            modifier += 1
        elif self.us_influence - self.ussr_influence < 0:
            modifier -= 1
        us_roll, ussr_roll = np.random.randint(6) + 1, np.random.randint(6) + 1
        difference = us_roll - ussr_roll + modifier
        if difference > 0:
            self.adjust_influence(0, -min(difference, self.ussr_influence))
        elif difference < 0:
            self.adjust_influence(-min(-difference, self.us_influence), 0)
        print(f'US rolled: {us_roll}, USSR rolled: {ussr_roll}, Modifer = {modifier}, Difference = {difference}')


# In[ ]:


''' Creates entire map. '''
USSR = country(**USSR)
USA = country(**USA)
Canada = country(**Canada)
UK = country(**UK)
Norway = country(**Norway)
Sweden = country(**Sweden)
Finland = country(**Finland)
Denmark = country(**Denmark)
Benelux = country(**Benelux)
France = country(**France)
Spain_Portugal = country(**Spain_Portugal)
Italy = country(**Italy)
Greece = country(**Greece)
Austria = country(**Austria)
West_Germany = country(**West_Germany)
East_Germany = country(**East_Germany)
Poland = country(**Poland)
Czechoslovakia = country(**Czechoslovakia)
Hungary = country(**Hungary)
Yugoslavia = country(**Yugoslavia)
Romania = country(**Romania)
Bulgaria = country(**Bulgaria)
Turkey = country(**Turkey)
Libya = country(**Libya)
Egypt = country(**Egypt)
Israel = country(**Israel)
Lebanon = country(**Lebanon)
Syria = country(**Syria)
Iraq = country(**Iraq)
Iran = country(**Iran)
Jordan = country(**Jordan)
Gulf_States = country(**Gulf_States)
Saudi_Arabia = country(**Saudi_Arabia)
Afghanistan = country(**Afghanistan)
Pakistan = country(**Pakistan)
India = country(**India)
Burma = country(**Burma)
Laos_Cambodia = country(**Laos_Cambodia)
Thailand = country(**Thailand)
Vietnam = country(**Vietnam)
Malaysia = country(**Malaysia)
Australia = country(**Australia)
Indonesia = country(**Indonesia)
Philippines = country(**Philippines)
Japan = country(**Japan)
Taiwan = country(**Taiwan)
South_Korea = country(**South_Korea)
North_Korea = country(**North_Korea)
Algeria = country(**Algeria)
Morocco = country(**Morocco)
Tunisia = country(**Tunisia)
West_African_States = country(**West_African_States)
Ivory_Coast = country(**Ivory_Coast)
Saharan_States = country(**Saharan_States)
Nigeria = country(**Nigeria)
Cameroon = country(**Cameroon)
Zaire = country(**Zaire)
Angola = country(**Angola)
South_Africa = country(**South_Africa)
Botswana = country(**Botswana)
Zimbabwe = country(**Zimbabwe)
SE_African_States = country(**SE_African_States)
Kenya = country(**Kenya)
Somalia = country(**Somalia)
Ethiopia = country(**Ethiopia)
Sudan = country(**Sudan)
Mexico = country(**Mexico)
Guatemala = country(**Guatemala)
El_Salvador = country(**El_Salvador)
Honduras = country(**Honduras)
Costa_Rica = country(**Costa_Rica)
Panama = country(**Panama)
Nicaragua = country(**Nicaragua)
Cuba = country(**Cuba)
Haiti = country(**Haiti)
Dominican_Republic = country(**Dominican_Republic)
Colombia = country(**Colombia)
Ecuador = country(**Ecuador)
Peru = country(**Peru)
Chile = country(**Chile)
Argentina = country(**Argentina)
Uruguay = country(**Uruguay)
Paraguay = country(**Paraguay)
Bolivia = country(**Bolivia)
Brazil = country(**Brazil)
Venezuela = country(**Venezuela)
Chinese_Civil_War = country(**Chinese_Civil_War)


# ### Recreating coup and realignment logic.

# In[ ]:


def build_standard_map():
    Panama.set_influence(1, 0)
    Canada.set_influence(2, 0)
    UK.set_influence(2, 0)
    North_Korea.set_influence(0, 1)
    East_Germany.set_influence(0, 3)
    Finland.set_influence(0, 1)
    Syria.set_influence(0, 1)
    Israel.set_influence(1, 0)
    Iraq.set_influence(0, 1)
    Iran.set_influence(1, 0)
    North_Korea.set_influence(0, 3)
    South_Korea.set_influence(1, 0)
    Japan.set_influence(1, 0)
    Philippines.set_influence(1, 0)
    Australia.set_influence(4, 0)
    South_Africa.set_influence(1, 0)


# In[ ]:


build_standard_map()


# ### Create cards, hand, discard pile, draw pile, removed pile

# In[ ]:


class card:
    '''
    Cards should be able to be used for:
    1. Event
    2. Realignment
    3. Coup
    4. Placing influence
    5. Space race
    6. Trigger event first >> realignment/coup/influence
    '''
    def __init__(self, card_number):
        self.card_number = card_number
    
    def __repr__(self):
        return f'card({self.card_number})'


# Let's create cards by index 1-110. Early war: 1-35, 103-106. Mid war: 36-81, 107-108. Late war: 82-102, 109-110. China card is card(6).

# In[ ]:


all_cards = [card(i+1) for i in range(110)]
early_war_indices = [i+1 for i in range(35)]
early_war_indices.extend([i+1 for i in range(103-1,106)])
mid_war_indices = [i+1 for i in range(36-1,81)]
mid_war_indices.extend([i+1 for i in range(107-1,108)])
late_war_indices = [i+1 for i in range(82-1,102)]
late_war_indices.extend([i+1 for i in range(109-1,110)])


# In[ ]:


early_war_cards = [card(i) for i in early_war_indices]
mid_war_cards = [card(i) for i in mid_war_indices]
late_war_cards = [card(i) for i in late_war_indices]


# In[ ]:


us_hand = []
ussr_hand = []


# ### Setup

# In[ ]:


'''
Remove the China card from the early war pile. Shuffle the early war pile.
Distribute the cards to players. Each player receives 8 cards each.
'''
ussr_hand.append(early_war_cards.pop(5))
random.shuffle(early_war_cards)
ussr_hand.extend([early_war_cards.pop() for i in range(8)])
us_hand.extend([early_war_cards.pop() for i in range(8)])


# In[ ]:


ussr_hand


# In[ ]:


early_war_cards


# In[ ]:


late_war_cards


# In[ ]:





# ### Create the turn order

# ### Create space race track
# 1. Create the actual track
# 2. Create the buffs

# In[ ]:


# TRACKS
vp_track = 0 # positive for ussr
turn_track = 1
ar_track = 1 # increment by 0.5 for each side's action round
defcon_track = 5
milops_track = [0, 0] # ussr first
space_track = [0, 0] # 0 is start, 1 is earth satellite etc

'''
Need to add the additional functionality gained with being faster on the space race.
'''

# SPACE (function)
def space(side):
    global vp_track
    x = 0
    if side == 'us':
        x = 1
        
    if space_track[x] in [0,2,4,6]:
        modifier = 0
    elif space_track[x] in [1,3,5]:
        modifier = -1
    else:
        modifier = 1
    
    y = 1 - 2*x # multiplier for VPs - gives 1 for USSR and -1 for US
    roll = np.random.randint(6)
    if roll + 1 + modifier <= 3:
        space_track[x] += 1
        print(f'Success with roll of {roll}.')
        
        if space_track[x] == 1:
            if space_track[1-x] < 1:
                vp_track += 2*y
            else:
                vp_track += y
        
        elif space_track[x] == 3:
            if space_track[1-x] < 3:
                vp_track += 2*y
            
        elif space_track[x] == 5:
            if space_track[1-x] < 5:
                vp_track += 3*y
            else:
                vp_track += y
                
        elif space_track[x] == 7:
            if space_track[1-x] < 7:
                vp_track += 4*y
            else:
                vp_track += 2*y
                
        elif space_track[x] == 8:
            if space_track[1-x] < 8:
                vp_track += 2*y
    
    else:
        print(f'Failure with roll of {roll}.')


# In[ ]:


# CA SCORING TEST

def scoring_CA():
    global vp_track
    
    CA = []
    for x in list(all_countries.values()):
        if x.region == "Central America":
            CA.append(x)
            
    presence, domination, control = [1,3,5]

    bg_count = [0,0] # USSR, US
    country_count = [0,0]
    bgs = 0

    for x in CA:
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

    vp_track += swing

