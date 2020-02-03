def ScoreCentralAmerica():
    global vp_track

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

    change_vp(swing)

def ScoreSouthAmerica():
    global vp_track

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

    change_vp(swing)

def ScoreAfrica():
    global vp_track

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

    change_vp(swing)

def ScoreEurope():
    global vp_track

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

    change_vp(swing)

# TO ADD SHUTTLE DIPLOMACY
def ScoreMiddleEast():
    global vp_track

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

    change_vp(swing)

# TO ADD SHUTTLE DIPLOMACY AND FORMOSAN RESOLUTION
def ScoreAsia():
    global vp_track

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

    change_vp(swing)
