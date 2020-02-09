#!/usr/bin/env python
# coding: utf-8

# ### Twilight Struggle

# In[1]:


import numpy as np
import random

from twilight_map import *
from game_mechanics import *
from twilight_cards import *


# ### Game Instance

# In[2]:


# this is a temporary measure. It should go into UI.new()
g = Game()
g.ui.run()


# In[3]:


g.ussr_hand

