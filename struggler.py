#!/usr/bin/env python
# coding: utf-8

# ### Twilight Struggle

# In[1]:


import pandas as pd
import numpy as np
import random
from twilight_map import *
from twilight_cards import *
from scoring_functionality import *


# ### Create cards, hand, discard pile, draw pile, removed pile

# In[2]:


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
    def __init__(self, card_number, **kwargs):
        self.card_number = card_number
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def __repr__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
        return ', '.join(sb)


# Let's create cards by index 1-110. Early war: 1-35, 103-106. Mid war: 36-81, 107-108. Late war: 82-102, 109-110. China card is card(6).

# In[3]:


all_cards = [card(i+1) for i in range(110)]
early_war_indices = [i+1 for i in range(35)]
early_war_indices.extend([i+1 for i in range(103-1,106)])
mid_war_indices = [i+1 for i in range(36-1,81)]
mid_war_indices.extend([i+1 for i in range(107-1,108)])
late_war_indices = [i+1 for i in range(82-1,102)]
late_war_indices.extend([i+1 for i in range(109-1,110)])


# In[4]:


early_war_cards = [card(i) for i in early_war_indices]
mid_war_cards = [card(i) for i in mid_war_indices]
late_war_cards = [card(i) for i in late_war_indices]


# In[5]:


us_hand = []
ussr_hand = []


# ### Setup

# In[6]:


Arab_Israeli_War = card(**Arab_Israeli_War)
Asia_Scoring = card(**Asia_Scoring)
Blockade = card(**Blockade)
CIA_Created = card(**CIA_Created)
COMECON = card(**COMECON)
Captured_Nazi_Scientist = card(**Captured_Nazi_Scientist)
Containment = card(**Containment)
De_Gaulle_Leads_France = card(**De_Gaulle_Leads_France)
De_Stalinization = card(**De_Stalinization)
Decolonization = card(**Decolonization)
Defectors = card(**Defectors)
Duck_and_Cover = card(**Duck_and_Cover)
East_European_Unrest = card(**East_European_Unrest)
Europe_Scoring = card(**Europe_Scoring)
Fidel = card(**Fidel)
Five_Year_Plan = card(**Five_Year_Plan)
Formosan_Resolution = card(**Formosan_Resolution)
Independent_Reds = card(**Independent_Reds)
Indo_Pakistani_War = card(**Indo_Pakistani_War)
Korean_War = card(**Korean_War)
Marshall_Plan = card(**Marshall_Plan)
Middle_East_Scoring = card(**Middle_East_Scoring)
NATO = card(**NATO)
NORAD = card(**NORAD)
Nasser = card(**Nasser)
Nuclear_Test_Ban = card(**Nuclear_Test_Ban)
Olympic_Games = card(**Olympic_Games)
Red_Scare_Purge = card(**Red_Scare_Purge)
Romanian_Abdication = card(**Romanian_Abdication)
Socialist_Governments = card(**Socialist_Governments)
Special_Relationship = card(**Special_Relationship)
Suez_Crisis = card(**Suez_Crisis)
The_Cambridge_Five = card(**The_Cambridge_Five)
The_China_Card = card(**The_China_Card)
Truman_Doctrine = card(**Truman_Doctrine)
UN_Intervention = card(**UN_Intervention)
US_Japan_Mutual_Defense_Pact = card(**US_Japan_Mutual_Defense_Pact)
Vietnam_Revolts = card(**Vietnam_Revolts)
Warsaw_Pact_Formed = card(**Warsaw_Pact_Formed)


# In[7]:


'''
Remove the China card from the early war pile. Shuffle the early war pile.
Distribute the cards to players. Each player receives 8 cards each.
'''
ussr_hand.append(early_war_cards.pop(5))
random.shuffle(early_war_cards)
ussr_hand.extend([early_war_cards.pop() for i in range(8)])
us_hand.extend([early_war_cards.pop() for i in range(8)])


# In[8]:


ussr_hand


# In[9]:


early_war_cards


# In[ ]:


late_war_cards


# ### Tracks

# In[ ]:


vp_track = 0 # positive for ussr
turn_track = 1
ar_track = 1 # increment by 0.5 for each side's action round
defcon_track = 5
milops_track = [0, 0] # ussr first
space_track = [0, 0] # 0 is start, 1 is earth satellite etc


# In[ ]:


# to add game terminate functionality EndGame()
def change_vp(n): # positive for ussr
    global vp_track
    vp_track += n
    if vp_track >= 20:
        print('USSR victory')
        # EndGame()
    if vp_track <= -20:
        print('US victory')
        # EndGame()

def change_defcon(n):
    global defcon_track
    defcon_track += min(n, 5 - defcon_track)
    if defcon_track < 2:
        print('Game ended by thermonuclear war')
        # EndGame()
    


# ### Create the turn order
# 1. Increase DEFCON status
# 2. Deal Cards
# 3. Headline Phase
# 4. Action Rounds (advance round marker)
# 5. Check milops
# 6. Check for held scoring card
# 7. Flip China Card
# 8. Advance turn marker
# 9. Final scoring (end T10)

# In[ ]:





# ### Create space race track
# 1. Create the buffs
# 2. Need to add the additional functionality gained with being faster on the space race.

# In[ ]:


# SPACE (function)
def space(side):
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

