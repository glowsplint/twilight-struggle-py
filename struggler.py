#!/usr/bin/env python
# coding: utf-8

# ### Twilight Struggle

# In[1]:


import numpy as np
import random

from twilight_map import *
from game_mechanics import *
from twilight_cards import *


# ### Setup

# ### Create space race track
# 1. Create the buffs
# 2. Need to add the additional functionality gained with being faster on the space race.

# ### Scoring Cards

# In[2]:


# this is a temporary measure. It should go into UI.new()
g = Game()
g.start()
Asia_Scoring.use_for_event()
Europe_Scoring.use_for_event()
g.ui.run()


# In[3]:


g.stage.operations_influence(Side.USSR, 6, start_flag=True)

