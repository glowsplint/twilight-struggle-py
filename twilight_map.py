import random
from twilight_enums import *


class CountryInfo:

    ALL = dict()
    REGION_ALL = [set() for r in MapRegion]

    def __init__(self, name='', country_index='', adjacent_countries=None,
                 region='', stability=0, battleground=False, superpower=False,
                 chinese_civil_war=False, **kwargs):

        self.name = name
        self.country_index = country_index
        self.stability = stability
        self.battleground = battleground
        self.adjacent_countries = adjacent_countries
        self.superpower = superpower
        self.chinese_civil_war = chinese_civil_war

        CountryInfo.ALL[name] = self
        if region == 'Europe':
            self.regions = [MapRegion.EUROPE,
                            MapRegion.EASTERN_EUROPE, MapRegion.WESTERN_EUROPE]
        elif region == 'Western Europe':
            self.regions = [MapRegion.EUROPE, MapRegion.WESTERN_EUROPE]
        elif region == 'Eastern Europe':
            self.regions = [MapRegion.EUROPE, MapRegion.EASTERN_EUROPE]
        elif region == 'Asia':
            self.regions = [MapRegion.ASIA]
        elif region == 'Southeast Asia':
            self.regions = [MapRegion.ASIA, MapRegion.SOUTHEAST_ASIA]
        elif region == 'Middle East':
            self.regions = [MapRegion.MIDDLE_EAST]
        elif region == 'Africa':
            self.regions = [MapRegion.AFRICA]
        elif region == 'Central America':
            self.regions = [MapRegion.CENTRAL_AMERICA]
        elif region == 'South America':
            self.regions = [MapRegion.SOUTH_AMERICA]
        elif region == '':
            self.regions = []
        else:
            print(f'Unrecognized region string: {region}')
            self.regions = []

        for r in self.regions:
            CountryInfo.REGION_ALL[r].add(name)

    def __deepcopy__(self, memo):
        return self


class GameMap:

    def __init__(self):
        self.ALL = dict()
        # Create mapping of (k,v) = (country_index, name)
        self.index_country_mapping = dict()
        for name in CountryInfo.ALL.keys():
            self.ALL[name] = Country(name)
            self.index_country_mapping[self.ALL[name]
                                       .info.country_index] = self.ALL[name].info.name

    def __getitem__(self, item):
        return self.ALL[item]

    '''Returns list of names that have influence from side, less superpowers..'''
    def has_influence(self, side: Side):
        return map(lambda item: item[0],
                   filter(lambda item: item[1].has_influence(side) and not item[1].info.superpower,
                      self.ALL.items()))

    def has_us_influence(self):
        '''Returns list of names that have US influence, less superpowers..'''
        country_list = []
        for country in self.ALL.values():
            if country.influence[Side.US] > 0 and country.info.superpower == False:
                country_list.append(country.info.name)
        return country_list

    def has_ussr_influence(self):
        '''Returns list of names that have USSR influence, less superpowers..'''
        country_list = []
        for country in self.ALL.values():
            if country.influence[Side.USSR] > 0 and country.info.superpower == False:
                country_list.append(country.info.name)
        return country_list

    def build_standard(self):
        self['USSR'].set_influence(999, 0)
        self['North_Korea'].set_influence(3, 0)
        self['East_Germany'].set_influence(3, 0)
        self['Finland'].set_influence(1, 0)
        self['Syria'].set_influence(1, 0)
        self['Iraq'].set_influence(1, 0)

        self['US'].set_influence(0, 999)
        self['Australia'].set_influence(0, 4)
        self['Philippines'].set_influence(0, 1)
        self['Canada'].set_influence(0, 2)
        self['UK'].set_influence(0, 5)
        self['Panama'].set_influence(0, 1)
        self['Israel'].set_influence(0, 1)
        self['Iran'].set_influence(0, 1)
        self['South_Korea'].set_influence(0, 1)
        self['Japan'].set_influence(0, 1)
        self['South_Africa'].set_influence(0, 1)
        return

    def can_coup(self, game_instance, name: str, side: Side):
        country = self[name]
        if country.info.superpower:
            return False

        d4 = [n for n in CountryInfo.REGION_ALL[MapRegion.EUROPE]]
        d3 = [n for n in CountryInfo.REGION_ALL[MapRegion.ASIA]]
        d3.extend(d4)
        d2 = [n for n in CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST]]
        d2.extend(d3)

        if 'NATO' in game_instance.basket[Side.US] and name in d4:
            return False
        elif 'US_Japan_Mutual_Defense_Pact' in game_instance.basket[Side.US] and name == 'Japan':
            return False
        elif game_instance.defcon_track == 4 and name in d4:
            return False
        elif game_instance.defcon_track == 3 and name in d3:
            return False
        elif game_instance.defcon_track == 2 and name in d2:
            return False

        return not (side == Side.US and country.influence[Side.USSR] == 0 or
                    side == Side.USSR and country.influence[Side.US] == 0)

    def coup(self, game_instance, name: str, side: Side, effective_ops: int, die_roll: int):
        assert(self.can_coup(game_instance, name, side))
        country = self[name]

        modifier = 0
        ca = list(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA])
        sa = list(CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA])

        if name in ca or name in sa:
            if 'Latin_American_Death_Squads' in game_instance.basket[side]:
                modifier += 1
            elif 'Latin_American_Death_Squads' in game_instance.basket[side.opp]:
                modifier -= 1

        difference = die_roll + effective_ops + modifier - country.info.stability * 2

        if difference > 0:
            if side == Side.USSR:
                # subtract from opposing first.. and then add to yours
                country.change_influence(max(
                    0, difference - country.influence[Side.US]), -min(difference, country.influence[Side.US]))

            if side == Side.US:
                country.change_influence(-min(difference, country.influence[Side.USSR]), max(
                    0, difference - country.influence[Side.USSR]))
            print(
                f'Coup successful with roll of {die_roll}. Difference: {difference}')
        else:
            print(f'Coup failed with roll of {die_roll}.')

        if country.info.battleground and 'Nuclear_Subs' not in game_instance.basket[Side.US]:
            game_instance.change_defcon(-1)

        if side == Side.US and 'Yuri_and_Samantha' in game_instance.basket[Side.USSR]:
            game_instance.change_vp(1)

        game_instance.change_milops(side, effective_ops)

    def can_realignment(self, game_instance, name: str, side: Side):
        country = self[name]
        if country.info.superpower:
            return False

        d4 = [n for n in CountryInfo.REGION_ALL[MapRegion.EUROPE]]
        d3 = [n for n in CountryInfo.REGION_ALL[MapRegion.ASIA]]
        d3.extend(d4)
        d2 = [n for n in CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST]]
        d2.extend(d3)

        if 'NATO' in game_instance.basket[Side.US] and name in d4:
            return False
        elif 'US_Japan_Mutual_Defense_Pact' in game_instance.basket[Side.US] and name == 'Japan':
            return False
        elif game_instance.defcon_track == 4 and name in d4:
            return False
        elif game_instance.defcon_track == 3 and name in d3:
            return False
        elif game_instance.defcon_track == 2 and name in d2:
            return False

        if side == Side.USSR and country.ussr_influence_only:
            return False
        elif side == Side.US and country.us_influence_only:
            return False
        else:
            return not (country.influence[Side.USSR] == 0 and country.influence[Side.US] == 0)

    def realignment(self, game_instance, name: str, side: Side):
        assert(self.can_realignment(game_instance, name, side))
        country = self[name]

        modifier = 0  # net positive is in favour of US
        if 'Iran_Contra_Scandal' in game_instance.basket[Side.USSR]:
            modifier -= 1

        for adjacent_name in country.info.adjacent_countries:
            modifier += ((self[adjacent_name]).control == Side.US)
            modifier -= ((self[adjacent_name]).control == Side.USSR)
        if country.influence[Side.US] - country.influence[Side.USSR] > 0:
            modifier += 1
        elif country.influence[Side.US] - country.influence[Side.USSR] < 0:
            modifier -= 1
        us_roll, ussr_roll = random.randint(1, 6), random.randint(1, 6)
        difference = us_roll - ussr_roll + modifier
        if difference > 0:
            country.change_influence(-min(difference,
                                          country.influence[Side.USSR]), 0)
        elif difference < 0:
            country.change_influence(
                0, -min(-difference, country.influence[Side.US]))
        print(
            f'US rolled: {us_roll}, USSR rolled: {ussr_roll}, Modifer = {modifier}, Difference = {difference}')

    # assume that a specific card has already been selected before the running of this function
    def can_place_influence(self, name: str, side: Side, effective_ops: int):
        # Here we run two different checks in order:
        # 1. In any of the adjacent countries and itself, is there existing influence of the same side?
        # 2. If this country is controlled by the opposite power, is effective_ops at least 2?
        # 2a. Also checks if the card being used has at least 1 effective operation point (so scoring cards can't be used for influence)
        country = self[name]

        def has_influence_around(self, name: str, side: Side):
            if self[name].info.superpower:
                return False

            countries_to_check = self[name].info.adjacent_countries.copy()
            countries_to_check.append(name)
            for country in countries_to_check:
                if self[country].influence[side] > 0:
                    return True
            return False  # returns false if none of the above are true

        def sufficient_ops(self, effective_ops: int):
            # if country is controlled by opposition, if ops > 1, return true, else false
            if country.control == side.opp:
                return True if effective_ops >= 2 else False
            else:
                return True

        return has_influence_around(self, name, side) and sufficient_ops(self, effective_ops)

    def place_influence(self, name: str, side: Side, effective_ops: int):
        if side == Side.USSR and self[name].control == Side.US:
            # here we deduct 2 from effective_ops, to place 1 influence in the country, and then call the function again
            if effective_ops >= 2:
                self[name].change_influence(1, 0)
            else:
                raise ValueError('Not enough operations points!')
            if effective_ops - 2 > 0:
                self.place_influence(name, side, effective_ops - 2)
        elif side == Side.US and self[name].control == Side.USSR:
            if effective_ops >= 2:
                self[name].change_influence(0, 1)
            else:
                raise ValueError('Not enough operations points!')
            if effective_ops - 2 > 0:
                self.place_influence(name, side, effective_ops - 2)
        else:
            if side == Side.US:
                self[name].change_influence(0, effective_ops)
            elif side == Side.USSR:
                self[name].change_influence(effective_ops, 0)
            else:
                raise ValueError('side must be \'us\' or \'ussr\'!')

    # these functions have slightly different syntax from the Country ones, if you want to use them
    # you should preferably call the country methods directly, but these can be more elegant
    def change_influence(self, name: str, side: Side, influence: int):
        if side == Side.USSR:
            self[name].change_influence(influence, 0)
        elif side == Side.US:
            self[name].change_influence(0, influence)

    def set_influence(self, name: str, side: Side, influence: int):
        if side == Side.USSR:
            self[name].set_influence(influence, self[name].influence[Side.US])
        elif side == Side.US:
            self[name].set_influence(
                self[name].influence[Side.USSR], influence)


class Country:

    def __init__(self, name: str):
        self.info = CountryInfo.ALL[name]
        self.influence = [0, 0]  # ussr, then us influence


    @property
    def control(self):
        if self.influence[Side.US] - self.influence[Side.USSR] >= self.info.stability:
            return Side.US
        elif self.influence[Side.USSR] - self.influence[Side.US] >= self.info.stability:
            return Side.USSR
        else:
            return Side.NEUTRAL

    @property
    def us_influence_only(self):
        return self.influence[Side.US] > 0 and self.influence[Side.USSR] == 0

    @property
    def ussr_influence_only(self):
        return self.influence[Side.USSR] > 0 and self.influence[Side.US] == 0

    def has_influence(self, side):
        return self.influence[side]

    @property
    def has_us_influence(self):
        return self.influence[Side.US] > 0

    @property
    def has_ussr_influence(self):
        return self.influence[Side.USSR] > 0

    def __repr__(self):
        if self.info.stability == 0:
            return f'Country({self.info.name}, Superpower = True, Adjacent = {self.info.adjacent_countries})'
        else:
            return f'Country({self.info.name}, \nUS_influence\t= {self.influence[Side.US]}, {self.us_influence_only}\nUSSR_influence\t= {self.influence[Side.USSR]}, {self.ussr_influence_only}\nControl \t= {self.control}'

    def set_influence(self, ussr_influence, us_influence):
        self.influence[Side.US] = us_influence
        self.influence[Side.USSR] = ussr_influence

    def reset_influence(self):
        self.influence[Side.US] = 0
        self.influence[Side.USSR] = 0

    def change_influence(self, ussr_influence: int, us_influence: int):
        self.influence[Side.US] += us_influence
        self.influence[Side.USSR] += ussr_influence
        if self.influence[Side.US] < 0:
            self.influence[Side.US] = 0
        if self.influence[Side.USSR] < 0:
            self.influence[Side.USSR] = 0

    def remove_influence(self, side):
        if self.influence[side] == 0: return False
        self.influence[side] = 0
        return True

    def increment_influence(self, side, amt=1):
        self.influence[side] += amt
        return True

    def decrement_influence(self, side, amt=1):
        if self.influence[side] == 0: return False
        self.influence[side] = max(self.influence[side] - amt, 0)
        return True


USSR = {
    'name': 'USSR',
    'country_index': 1,
    'superpower': True,
    'adjacent_countries': ['Finland', 'Poland', 'Romania', 'Afghanistan', 'North_Korea', 'Chinese_Civil_War'],
    'us_influence': 0,
    'ussr_influence': 999,
}

US = {
    'name': 'US',
    'country_index': 2,
    'superpower': True,
    'adjacent_countries': ['Japan', 'Mexico', 'Cuba', 'Canada'],
    'us_influence': 999,
    'ussr_influence': 0,
}

Canada = {
    'name': 'Canada',
    'country_index': 3,
    'region': 'Western Europe',
    'stability': 4,
    'adjacent_countries': ['US', 'UK'],
    'us_influence': 0,
    'ussr_influence': 0,
}

UK = {
    'name': 'UK',
    'country_index': 4,
    'region': 'Western Europe',
    'stability': 5,
    'adjacent_countries': ['Canada', 'Norway', 'Benelux', 'France'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Norway = {
    'name': 'Norway',
    'country_index': 5,
    'region': 'Western Europe',
    'stability': 4,
    'adjacent_countries': ['UK', 'Sweden'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Sweden = {
    'name': 'Sweden',
    'country_index': 6,
    'region': 'Western Europe',
    'stability': 4,
    'adjacent_countries': ['Norway', 'Finland', 'Denmark'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Finland = {
    'name': 'Finland',
    'country_index': 7,
    'region': 'Europe',
    'stability': 4,
    'adjacent_countries': ['Sweden', 'USSR'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Denmark = {
    'name': 'Denmark',
    'country_index': 8,
    'region': 'Western Europe',
    'stability': 3,
    'adjacent_countries': ['Sweden', 'West_Germany'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Benelux = {
    'name': 'Benelux',
    'country_index': 9,
    'region': 'Western Europe',
    'stability': 3,
    'adjacent_countries': ['UK', 'West_Germany'],
    'us_influence': 0,
    'ussr_influence': 0,
}

France = {
    'name': 'France',
    'country_index': 10,
    'region': 'Western Europe',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['UK', 'West_Germany', 'Spain_Portugal', 'Italy', 'Algeria'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Spain_Portugal = {
    'name': 'Spain_Portugal',
    'country_index': 11,
    'region': 'Western Europe',
    'stability': 2,
    'adjacent_countries': ['France', 'Italy', 'Morocco'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Italy = {
    'name': 'Italy',
    'country_index': 12,
    'region': 'Western Europe',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['France', 'Spain_Portugal', 'Austria', 'Yugoslavia', 'Greece'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Greece = {
    'name': 'Greece',
    'country_index': 13,
    'region': 'Western Europe',
    'stability': 2,
    'adjacent_countries': ['Italy', 'Yugoslavia', 'Bulgaria', 'Turkey'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Austria = {
    'name': 'Austria',
    'country_index': 14,
    'region': 'Europe',
    'stability': 4,
    'adjacent_countries': ['West_Germany', 'East_Germany', 'Hungary', 'Italy'],
    'us_influence': 0,
    'ussr_influence': 0,
}

West_Germany = {
    'name': 'West_Germany',
    'country_index': 15,
    'region': 'Western Europe',
    'stability': 4,
    'battleground': True,
    'adjacent_countries': ['France', 'Benelux', 'Denmark', 'East_Germany', 'Austria'],
    'us_influence': 0,
    'ussr_influence': 0,
}


East_Germany = {
    'name': 'East_Germany',
    'country_index': 16,
    'region': 'Eastern Europe',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['West_Germany', 'Austria', 'Czechoslovakia', 'Poland'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Poland = {
    'name': 'Poland',
    'country_index': 17,
    'region': 'Eastern Europe',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['East_Germany', 'Czechoslovakia', 'USSR'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Czechoslovakia = {
    'name': 'Czechoslovakia',
    'country_index': 18,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['East_Germany', 'Poland', 'Hungary'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Hungary = {
    'name': 'Hungary',
    'country_index': 19,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['Austria', 'Czechoslovakia', 'Romania', 'Yugoslavia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Yugoslavia = {
    'name': 'Yugoslavia',
    'country_index': 20,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['Italy', 'Hungary', 'Greece', 'Romania'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Romania = {
    'name': 'Romania',
    'country_index': 21,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['Hungary', 'Yugoslavia', 'Turkey', 'USSR'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Bulgaria = {
    'name': 'Bulgaria',
    'country_index': 22,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['Greece', 'Turkey'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Turkey = {
    'name': 'Turkey',
    'country_index': 23,
    'region': 'Western Europe',
    'stability': 2,
    'adjacent_countries': ['Greece', 'Bulgaria', 'Romania', 'Syria'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Libya = {
    'name': 'Libya',
    'country_index': 24,
    'region': 'Middle East',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Tunisia', 'Egypt'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Egypt = {
    'name': 'Egypt',
    'country_index': 25,
    'region': 'Middle East',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Libya', 'Israel', 'Sudan'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Israel = {
    'name': 'Israel',
    'country_index': 26,
    'region': 'Middle East',
    'stability': 4,
    'battleground': True,
    'adjacent_countries': ['Lebanon', 'Syria', 'Jordan', 'Egypt'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Lebanon = {
    'name': 'Lebanon',
    'country_index': 27,
    'region': 'Middle East',
    'stability': 1,
    'adjacent_countries': ['Israel', 'Syria', 'Jordan'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Syria = {
    'name': 'Syria',
    'country_index': 28,
    'region': 'Middle East',
    'stability': 2,
    'adjacent_countries': ['Israel', 'Lebanon', 'Turkey'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Iraq = {
    'name': 'Iraq',
    'country_index': 29,
    'region': 'Middle East',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Jordan', 'Saudi_Arabia', 'Gulf_States', 'Iran'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Iran = {
    'name': 'Iran',
    'country_index': 30,
    'region': 'Middle East',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Iraq', 'Afghanistan', 'Pakistan'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Jordan = {
    'name': 'Jordan',
    'country_index': 31,
    'region': 'Middle East',
    'stability': 2,
    'adjacent_countries': ['Iraq', 'Israel', 'Lebanon', 'Saudi_Arabia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Gulf_States = {
    'name': 'Gulf_States',
    'country_index': 32,
    'region': 'Middle East',
    'stability': 3,
    'adjacent_countries': ['Iraq', 'Saudi_Arabia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Saudi_Arabia = {
    'name': 'Saudi_Arabia',
    'country_index': 33,
    'region': 'Middle East',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Iraq', 'Jordan', 'Gulf_States'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Afghanistan = {
    'name': 'Afghanistan',
    'country_index': 34,
    'region': 'Asia',
    'stability': 2,
    'adjacent_countries': ['USSR', 'Iran', 'Pakistan'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Pakistan = {
    'name': 'Pakistan',
    'country_index': 35,
    'region': 'Asia',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Afghanistan', 'Iran', 'India'],
    'us_influence': 0,
    'ussr_influence': 0,
}


India = {
    'name': 'India',
    'country_index': 36,
    'region': 'Asia',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Pakistan', 'Burma'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Burma = {
    'name': 'Burma',
    'country_index': 37,
    'region': 'Southeast Asia',
    'stability': 2,
    'adjacent_countries': ['India', 'Laos_Cambodia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Laos_Cambodia = {
    'name': 'Laos_Cambodia',
    'country_index': 38,
    'region': 'Southeast Asia',
    'stability': 1,
    'adjacent_countries': ['Burma', 'Thailand', 'Vietnam'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Thailand = {
    'name': 'Thailand',
    'country_index': 39,
    'region': 'Southeast Asia',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Laos_Cambodia', 'Vietnam', 'Malaysia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Vietnam = {
    'name': 'Vietnam',
    'country_index': 40,
    'region': 'Southeast Asia',
    'stability': 1,
    'adjacent_countries': ['Laos_Cambodia', 'Thailand'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Malaysia = {
    'name': 'Malaysia',
    'country_index': 41,
    'region': 'Southeast Asia',
    'stability': 2,
    'adjacent_countries': ['Thailand', 'Indonesia', 'Australia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Australia = {
    'name': 'Australia',
    'country_index': 42,
    'region': 'Asia',
    'stability': 4,
    'adjacent_countries': ['Malaysia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Indonesia = {
    'name': 'Indonesia',
    'country_index': 43,
    'region': 'Southeast Asia',
    'stability': 1,
    'adjacent_countries': ['Malaysia', 'Philippines'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Philippines = {
    'name': 'Philippines',
    'country_index': 44,
    'region': 'Southeast Asia',
    'stability': 2,
    'adjacent_countries': ['Indonesia', 'Japan'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Japan = {
    'name': 'Japan',
    'country_index': 45,
    'region': 'Asia',
    'stability': 4,
    'battleground': True,
    'adjacent_countries': ['Philippines', 'Taiwan', 'South_Korea', 'US'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Taiwan = {
    'name': 'Taiwan',
    'country_index': 46,
    'region': 'Asia',
    'stability': 3,
    'adjacent_countries': ['Japan', 'South_Korea'],
    'us_influence': 0,
    'ussr_influence': 0,
}


South_Korea = {
    'name': 'South_Korea',
    'country_index': 47,
    'region': 'Asia',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Japan', 'Taiwan', 'North_Korea'],
    'us_influence': 0,
    'ussr_influence': 0,
}


North_Korea = {
    'name': 'North_Korea',
    'country_index': 48,
    'region': 'Asia',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['South_Korea', 'USSR'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Algeria = {
    'name': 'Algeria',
    'country_index': 49,
    'region': 'Africa',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Morocco', 'Saharan_States', 'Tunisia', 'France'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Morocco = {
    'name': 'Morocco',
    'country_index': 50,
    'region': 'Africa',
    'stability': 3,
    'adjacent_countries': ['Algeria', 'West_African_States', 'Spain_Portugal'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Tunisia = {
    'name': 'Tunisia',
    'country_index': 51,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['Algeria', 'Libya'],
    'us_influence': 0,
    'ussr_influence': 0,
}


West_African_States = {
    'name': 'West_African_States',
    'country_index': 52,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['Morocco', 'Ivory_Coast'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Ivory_Coast = {
    'name': 'Ivory_Coast',
    'country_index': 53,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['West_African_States', 'Nigeria'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Saharan_States = {
    'name': 'Saharan_States',
    'country_index': 54,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Algeria', 'Nigeria'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Nigeria = {
    'name': 'Nigeria',
    'country_index': 55,
    'region': 'Africa',
    'stability': 1,
    'battleground': True,
    'adjacent_countries': ['Ivory_Coast', 'Saharan_States', 'Cameroon'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Cameroon = {
    'name': 'Cameroon',
    'country_index': 56,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Nigeria', 'Zaire'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Zaire = {
    'name': 'Zaire',
    'country_index': 57,
    'region': 'Africa',
    'stability': 1,
    'battleground': True,
    'adjacent_countries': ['Cameroon', 'Angola', 'Zimbabwe'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Angola = {
    'name': 'Angola',
    'country_index': 58,
    'region': 'Africa',
    'stability': 1,
    'battleground': True,
    'adjacent_countries': ['Zaire', 'Botswana', 'South_Africa'],
    'us_influence': 0,
    'ussr_influence': 0,
}


South_Africa = {
    'name': 'South_Africa',
    'country_index': 59,
    'region': 'Africa',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Angola', 'Botswana'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Botswana = {
    'name': 'Botswana',
    'country_index': 60,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['Angola', 'South_Africa', 'Zimbabwe'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Zimbabwe = {
    'name': 'Zimbabwe',
    'country_index': 61,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Zaire', 'Botswana', 'SE_African_States'],
    'us_influence': 0,
    'ussr_influence': 0,
}


SE_African_States = {
    'name': 'SE_African_States',
    'country_index': 62,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Zimbabwe', 'Kenya'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Kenya = {
    'name': 'Kenya',
    'country_index': 63,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['SE_African_States', 'Somalia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Somalia = {
    'name': 'Somalia',
    'country_index': 64,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['Kenya', 'Ethiopia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Ethiopia = {
    'name': 'Ethiopia',
    'country_index': 65,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Somalia', 'Sudan'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Sudan = {
    'name': 'Sudan',
    'country_index': 66,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Ethiopia', 'Egypt'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Mexico = {
    'name': 'Mexico',
    'country_index': 67,
    'region': 'Central America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Guatemala', 'US'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Guatemala = {
    'name': 'Guatemala',
    'country_index': 68,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Mexico', 'El_Salvador', 'Honduras'],
    'us_influence': 0,
    'ussr_influence': 0,
}


El_Salvador = {
    'name': 'El_Salvador',
    'country_index': 69,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Guatemala', 'Honduras'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Honduras = {
    'name': 'Honduras',
    'country_index': 70,
    'region': 'Central America',
    'stability': 2,
    'adjacent_countries': ['Guatemala', 'El_Salvador', 'Costa_Rica', 'Nicaragua'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Costa_Rica = {
    'name': 'Costa_Rica',
    'country_index': 71,
    'region': 'Central America',
    'stability': 3,
    'adjacent_countries': ['Honduras', 'Nicaragua', 'Panama'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Panama = {
    'name': 'Panama',
    'country_index': 72,
    'region': 'Central America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Costa_Rica', 'Colombia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Nicaragua = {
    'name': 'Nicaragua',
    'country_index': 73,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Costa_Rica', 'Honduras', 'Cuba'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Cuba = {
    'name': 'Cuba',
    'country_index': 74,
    'region': 'Central America',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Nicaragua', 'Haiti', 'US'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Haiti = {
    'name': 'Haiti',
    'country_index': 75,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Cuba', 'Dominican_Republic'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Dominican_Republic = {
    'name': 'Dominican_Republic',
    'country_index': 76,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Haiti'],
    'us_influence': 0,
    'ussr_influence': 0,
}

Colombia = {
    'name': 'Colombia',
    'country_index': 77,
    'region': 'South America',
    'stability': 1,
    'adjacent_countries': ['Panama', 'Ecuador', 'Venezuela'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Ecuador = {
    'name': 'Ecuador',
    'country_index': 78,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Colombia', 'Peru'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Peru = {
    'name': 'Peru',
    'country_index': 79,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Ecuador', 'Bolivia', 'Chile'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Chile = {
    'name': 'Chile',
    'country_index': 80,
    'region': 'South America',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Peru', 'Argentina'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Argentina = {
    'name': 'Argentina',
    'country_index': 81,
    'region': 'South America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Chile', 'Uruguay', 'Paraguay'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Uruguay = {
    'name': 'Uruguay',
    'country_index': 82,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Argentina', 'Paraguay', 'Brazil'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Paraguay = {
    'name': 'Paraguay',
    'country_index': 83,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Argentina', 'Uruguay', 'Bolivia'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Bolivia = {
    'name': 'Bolivia',
    'country_index': 84,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Peru', 'Paraguay'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Brazil = {
    'name': 'Brazil',
    'country_index': 85,
    'region': 'South America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Uruguay', 'Venezuela'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Venezuela = {
    'name': 'Venezuela',
    'country_index': 86,
    'region': 'South America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Colombia', 'Brazil'],
    'us_influence': 0,
    'ussr_influence': 0,
}


Chinese_Civil_War = {
    'name': 'Chinese_Civil_War',
    'country_index': 87,
    'chinese_civil_war': True,
    'region': 'Asia',
    'stability': 3,
    'adjacent_countries': ['USSR'],
    'us_influence': 0,
    'ussr_influence': 0,
}

''' Creates entire map. '''
USSR = CountryInfo(**USSR)
US = CountryInfo(**US)
Canada = CountryInfo(**Canada)
UK = CountryInfo(**UK)
Norway = CountryInfo(**Norway)
Sweden = CountryInfo(**Sweden)
Finland = CountryInfo(**Finland)
Denmark = CountryInfo(**Denmark)
Benelux = CountryInfo(**Benelux)
France = CountryInfo(**France)
Spain_Portugal = CountryInfo(**Spain_Portugal)
Italy = CountryInfo(**Italy)
Greece = CountryInfo(**Greece)
Austria = CountryInfo(**Austria)
West_Germany = CountryInfo(**West_Germany)
East_Germany = CountryInfo(**East_Germany)
Poland = CountryInfo(**Poland)
Czechoslovakia = CountryInfo(**Czechoslovakia)
Hungary = CountryInfo(**Hungary)
Yugoslavia = CountryInfo(**Yugoslavia)
Romania = CountryInfo(**Romania)
Bulgaria = CountryInfo(**Bulgaria)
Turkey = CountryInfo(**Turkey)
Libya = CountryInfo(**Libya)
Egypt = CountryInfo(**Egypt)
Israel = CountryInfo(**Israel)
Lebanon = CountryInfo(**Lebanon)
Syria = CountryInfo(**Syria)
Iraq = CountryInfo(**Iraq)
Iran = CountryInfo(**Iran)
Jordan = CountryInfo(**Jordan)
Gulf_States = CountryInfo(**Gulf_States)
Saudi_Arabia = CountryInfo(**Saudi_Arabia)
Afghanistan = CountryInfo(**Afghanistan)
Pakistan = CountryInfo(**Pakistan)
India = CountryInfo(**India)
Burma = CountryInfo(**Burma)
Laos_Cambodia = CountryInfo(**Laos_Cambodia)
Thailand = CountryInfo(**Thailand)
Vietnam = CountryInfo(**Vietnam)
Malaysia = CountryInfo(**Malaysia)
Australia = CountryInfo(**Australia)
Indonesia = CountryInfo(**Indonesia)
Philippines = CountryInfo(**Philippines)
Japan = CountryInfo(**Japan)
Taiwan = CountryInfo(**Taiwan)
South_Korea = CountryInfo(**South_Korea)
North_Korea = CountryInfo(**North_Korea)
Algeria = CountryInfo(**Algeria)
Morocco = CountryInfo(**Morocco)
Tunisia = CountryInfo(**Tunisia)
West_African_States = CountryInfo(**West_African_States)
Ivory_Coast = CountryInfo(**Ivory_Coast)
Saharan_States = CountryInfo(**Saharan_States)
Nigeria = CountryInfo(**Nigeria)
Cameroon = CountryInfo(**Cameroon)
Zaire = CountryInfo(**Zaire)
Angola = CountryInfo(**Angola)
South_Africa = CountryInfo(**South_Africa)
Botswana = CountryInfo(**Botswana)
Zimbabwe = CountryInfo(**Zimbabwe)
SE_African_States = CountryInfo(**SE_African_States)
Kenya = CountryInfo(**Kenya)
Somalia = CountryInfo(**Somalia)
Ethiopia = CountryInfo(**Ethiopia)
Sudan = CountryInfo(**Sudan)
Mexico = CountryInfo(**Mexico)
Guatemala = CountryInfo(**Guatemala)
El_Salvador = CountryInfo(**El_Salvador)
Honduras = CountryInfo(**Honduras)
Costa_Rica = CountryInfo(**Costa_Rica)
Panama = CountryInfo(**Panama)
Nicaragua = CountryInfo(**Nicaragua)
Cuba = CountryInfo(**Cuba)
Haiti = CountryInfo(**Haiti)
Dominican_Republic = CountryInfo(**Dominican_Republic)
Colombia = CountryInfo(**Colombia)
Ecuador = CountryInfo(**Ecuador)
Peru = CountryInfo(**Peru)
Chile = CountryInfo(**Chile)
Argentina = CountryInfo(**Argentina)
Uruguay = CountryInfo(**Uruguay)
Paraguay = CountryInfo(**Paraguay)
Bolivia = CountryInfo(**Bolivia)
Brazil = CountryInfo(**Brazil)
Venezuela = CountryInfo(**Venezuela)
# Chinese_Civil_War = CountryInfo(**Chinese_Civil_War)
