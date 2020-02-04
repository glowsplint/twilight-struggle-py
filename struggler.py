#!/usr/bin/env python
# coding: utf-8

# ### Twilight Struggle

# In[1]:


import pandas as pd
import numpy as np
import random
from twilight_cards import *


# In[2]:


all_cards = dict()
early_war_cards = dict()


# In[3]:


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
    def __init__(self, card_name, card_number, **kwargs):
        self.card_name = card_name
        self.card_number = card_number
        for key, value in kwargs.items():
            setattr(self, key, value)
        all_cards[card_name] = self
        if self.stage == 'Early War':
            early_war_cards[card_name] = self
    
    def __repr__(self):
#         sb = []
#         for key in self.__dict__:
#             sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
#         return ', '.join(sb)
        return self.card_name
    
    def trigger_event_first(self):
        # only possible if opponent event
        pass
    
    def use_for_influence(self):
        pass
    
    def use_for_space_race(self):
        pass
    
    def use_for_event(self):
        for event in self.event_effects:
            event[0](event[1])
        if hasattr(self, 'remove_if_used_as_event'):
            if self.remove_if_used_as_event:
            # to add functionality for remove cards from hand and into removed pile
                pass
    
    def use_for_coup(self):
        pass
    
    def use_for_realignment(self):
        pass
    
    def possible_actions(self):
        pass


# Let's create cards by index 1-110. Early war: 1-35, 103-106. Mid war: 36-81, 107-108. Late war: 82-102, 109-110. China card is card(6).

# ### Setup

# In[4]:


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


# In[5]:


us_hand = []
ussr_hand = []
removed_pile = []
discard_pile = []
draw_pile = []


# In[6]:


len(early_war_cards)


# In[7]:


'''
Remove the China card from the early war pile. Put early war cards into the draw pile. Shuffle and deal the draw pile.
Distribute the cards to players. Each player receives 8 cards each.
'''
ussr_hand.append(early_war_cards.pop('The China Card'))
draw_pile.extend(early_war_cards.values())
random.shuffle(draw_pile)
ussr_hand.extend([draw_pile.pop() for i in range(8)])
us_hand.extend([draw_pile.pop() for i in range(8)])


# In[8]:


draw_pile


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

# In[9]:


early_war_cards


# ### Create space race track
# 1. Create the buffs
# 2. Need to add the additional functionality gained with being faster on the space race.

# ### Scoring Cards

# Hi Box. Below Asia_Scoring prints the right message but doesn't change the VP track. Problem with globals variables?

# In[10]:


Asia_Scoring.use_for_event()
vp_track


# In[11]:


Egypt


# In[12]:


Nasser.use_for_event()
Egypt


# In[ ]:




