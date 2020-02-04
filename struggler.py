#!/usr/bin/env python
# coding: utf-8

# ### Twilight Struggle

# In[1]:


import pandas as pd
import numpy as np
import random
from twilight_cards import *


# Moved all country information into the twilight_cards.py file.

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
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        all_cards[self.card_name] = self
        if self.stage == 'Early War':
            early_war_cards[self.card_name] = self
#         if self.stage == 'Mid War':
#             mid_war_cards[card_name] = self
#         if self.stage == 'Late War':
#             late_war_cards[card_name] = self
    
    def __repr__(self):
#         sb = []
#         for key in self.__dict__:
#             sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))
#         return ', '.join(sb)
        if hasattr(self, 'operations_points'):
            return f'{self.card_name} - {self.operations_points}'
        else:
            return self.card_name
    
    def trigger_event_first(self):
        # only possible if opponent event
        # self.use_for_event()
        # do something else
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


'''Pre-headline setup'''
ussr_hand.append(early_war_cards.pop('The_China_Card')) # Move the China card from the early war pile to USSR hand
draw_pile.extend(early_war_cards.values()) # Put early war cards into the draw pile
random.shuffle(draw_pile) # Shuffle the draw pile
ussr_hand.extend([draw_pile.pop() for i in range(8)])
us_hand.extend([draw_pile.pop() for i in range(8)])


# In[7]:


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

class UI:

    help = """
The following commands are available:
?           Displays this help text.
m           Lists all possible moves, along with their respective IDs.
m <ID>      Makes a move.
m commit    Commits all moves made.
s           Displays the overall game state.
s ?         Shows help on game state queries.
c ?         Shows help on card information queries.

new         Start a new game.
quit        Exit the game.
"""

    @staticmethod
    def run():
    
        while True:
            # get user input
            user_choice = input("> ").split(" ", 1)
            
            if len(user_choice) == 1: user_choice.append("")
            
            # parse the input
            if len(user_choice) == 0 or user_choice[0] == "?":
                print(UI.help)
                
            elif user_choice[0] == "quit":
                break;
                
            elif user_choice[0] == "new":
                print("Uninplemented")
            
            elif user_choice[0] == "c":
                UI.parse_card(user_choice[1])
            
            elif user_choice[0] == "s":
                UI.parse_state(user_choice[1])
            
            elif user_choice[0] == "m":
                UI.parse_move(user_choice[1])
                
            else:
                print("Invalid command. Enter ? for help.")

    @staticmethod
    def parse_move(comd):
        
        if comd == "":
            print("Listing all moves.")
            print("Unimplemented")
            # Here you want to call some function to get all possible moves.
            # Each move should be deterministically assigned an ID (so it 
            # can be referenced later).
        elif comd == "commit":
            print("Game state advancing.")
            # this is where you tell the game engine to lock in the currently
            # selected move.
            print("Unimplemented")
        else:
            print("Making move ID %s" % comd)
            # check moves to find the corresponding ID. If it's not found print
            # an error message.
            # Then, tell the game engine to make a temp move.
            # or for now, we can just actually make the move with no takeback
            # which means the commit command won't do anything.
            print("Unimplemented")
                     
    help_card = """
c           Display a list of cards in the current player's hand.
c <ID#>     Display information about the card with the given ID number.
c dis       Display a list of cards in the discard pile
c rem       Display a list of removed cards.
c dec       Returns the number of cards in the draw deck.
"""
    @staticmethod
    def parse_card(comd):
    
        if comd == "":
            print("Listing cards in hand.")
            print("Unimplemented")
        elif comd == "?":
            print(UI.help_card)
        elif comd == "opp":
            print("Cards in opponent's hand: %d" % 1) # TODO make it based on state
            print("Unimplemented")
        elif comd == "dis":
            print("Listing %d discarded cards." % len(discard_pile))
            for c in discard_pile:
                print(c)
        elif comd == "rem":
            print("Listing %d removed cards."  % len(removed_pile))
            for c in removed_pile:
                print(c)
        elif comd == "dec":
            print("Cards in draw pile: %d." % len(draw_pile))
        else:
            print("Invalid command. Enter ? for help.")
    
    
    help_state = """
s <eu|as|me|af|na|sa>   Displays the scoring state and country data for the given region.
"""
    @staticmethod
    def parse_state(comd):
        if comd == "":
            print("=== Game state ===")
            print("VP status: %d" % Game.vp_track)
            print("Unimplemented")
        elif comd == "?":
            print(UI.help_state)
        else:
            # remember to check if comd is a valid ID
            print("State of %s:" % comd)
            print("Unimplemented")


# In[8]:


early_war_cards


# ### Create space race track
# 1. Create the buffs
# 2. Need to add the additional functionality gained with being faster on the space race.

# ### Scoring Cards

# Hi Box. Below Asia_Scoring prints the right message but doesn't change the VP track. Problem with global variables?

# In[9]:

#this is a temporary measure. It should go into UI.new()
g = Game()

Asia_Scoring.use_for_event()
Game.main.vp_track
UI.run()
