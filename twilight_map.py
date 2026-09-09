from itertools import chain
from twilight_enums import Side, MapRegion, InputType, CardAction


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
        for name in CountryInfo.ALL.keys():
            self.ALL[name] = Country(name)

    def __getitem__(self, item):
        return self.ALL[item]

    def has_influence(self, side: Side):
        '''Returns list of names that have influence from side, less superpowers..'''
        return (n for n, c in self.ALL.items()
                if c.has_influence(side) and not c.info.superpower)

    @property
    def has_us_influence(self):
        '''Returns list of names that have US influence, less superpowers..'''
        return [country.info.name for country in self.ALL.values() if country.influence[Side.US] > 0 and country.info.superpower == False]

    @property
    def has_ussr_influence(self):
        '''Returns list of names that have USSR influence, less superpowers..'''
        return [country.info.name for country in self.ALL.values() if country.influence[Side.USSR] > 0 and country.info.superpower == False]

    def can_coup(self, game_instance, name: str, side: Side, free=False,
                 ignore_defcon=False) -> bool:
        '''
        Checks if the country can be couped by a given side.

        Parameters
        ----------
        game_instance : Game object
            The game object the country resides within.
        name : str
            String representation of the country we are checking.
        side : Side
            Player side which we are checking. Can be Side.US or Side.USSR.

        Accounts for:
        - NATO
        - US_Japan_Mutual_Defense_Pact
        - The_Reformer
        '''
        country = self[name]
        if country.info.superpower:
            return False

        if (side == Side.USSR
                and 'NATO' in game_instance.basket[Side.US]
                and name in game_instance.calculate_nato_countries()):
            return False
        if (side == Side.USSR
                and 'US_Japan_Mutual_Defense_Pact'
                in game_instance.basket[Side.US]
                and name == 'Japan'):
            return False
        if (side == Side.USSR
                and 'The_Reformer' in game_instance.basket[Side.USSR]
                and name in _DEFCON_RESTRICTED[4]):
            return False
        if (not ignore_defcon
                and name in _DEFCON_RESTRICTED.get(
                    game_instance.defcon_track, ())):
            return False

        return not (side == Side.US and country.influence[Side.USSR] == 0 or
                    side == Side.USSR and country.influence[Side.US] == 0)

    def coup(self, game_instance, name: str, side: Side, effective_ops: int,
             die_roll: int, free=False, ignore_defcon=False):
        '''
        The result of a given side couping in a country, with a die_roll provided.
        Accounts for:
        - Global operations modifiers
        - Latin_American_Death_Squads,
        - Nuclear_Subs
        - Yuri_And_Samantha
        - The_China_Card
        - Vietnam_Revolts
        - Cuban_Missile_Crisis
        - SALT Negotiations


        Parameters
        ----------
        game_instance : Game object
            The game object the country resides within.
        name : str
            String representation of the country we are checking.
        side : Side
            Player side which we are checking. Can be Side.US or Side.USSR.
        effective_ops : int
            The number of effective operations used in the coup.
        die_roll: int
            The die roll of the coup. Should be bounded within range(1,7).
        '''
        assert(self.can_coup(
            game_instance, name, side, free=free,
            ignore_defcon=ignore_defcon))
        country = self[name]

        coup_modifier = 0

        # Latin American Death Squads
        ca = list(CountryInfo.REGION_ALL[MapRegion.CENTRAL_AMERICA])
        sa = list(CountryInfo.REGION_ALL[MapRegion.SOUTH_AMERICA])
        if name in ca or name in sa:
            if 'Latin_American_Death_Squads' in game_instance.basket[side]:
                coup_modifier += 1
            elif 'Latin_American_Death_Squads' in game_instance.basket[side.opp]:
                coup_modifier -= 1

        # SALT Negotiations
        if 'Salt_Negotiations' in game_instance.basket[side] or 'Salt_Negotiations' in game_instance.basket[side.opp]:
            coup_modifier -= 1

        difference = die_roll + effective_ops + \
            coup_modifier - country.info.stability * 2
        outcome = 'success' if difference > 0 else 'failure'

        if outcome == 'success':
            if side == Side.USSR:
                country.change_influence(max(
                    0, difference - country.influence[Side.US]), -min(difference, country.influence[Side.US]))

            if side == Side.US:
                country.change_influence(-min(difference, country.influence[Side.USSR]), max(
                    0, difference - country.influence[Side.USSR]))
        print(
            f'Coup {outcome} with roll of {die_roll}. Difference: {difference}')

        # Cuban Missile Crisis overrides Nuclear Subs
        if 'Cuban_Missile_Crisis' in game_instance.basket[side.opp]:
            game_instance.defcon_track = 1
            print('Game ended by thermonuclear war')
            game_instance.terminate(
                side=side.opp,
                reason='thermonuclear_war',
                context={
                    'defcon': 1,
                    'cause': 'Cuban_Missile_Crisis',
                    'loser': side.toStr(),
                },
            )
        elif country.info.battleground:
            if side == Side.US:
                if 'Nuclear_Subs' not in game_instance.basket[Side.US]:
                    game_instance.change_defcon(-1)
            else:
                game_instance.change_defcon(-1)

        if game_instance.terminated:
            return

        # Yuri and Samantha
        if side == Side.US and 'Yuri_and_Samantha' in game_instance.basket[Side.USSR]:
            game_instance.change_vp(1)

        # Free coups
        if not free:
            game_instance.change_milops(side, effective_ops)

    def can_realignment(self, game_instance, name: str, side: Side,
                        free=False, ignore_defcon=False) -> bool:
        '''
        Checks if the country can be realigned by a given side.

        Parameters
        ----------
        game_instance : Game object
            The game object the country resides within.
        name : str
            String representation of the country we are checking.
        side : Side
            Player side which we are checking. Can be Side.US or Side.USSR.
        '''
        country = self[name]
        if country.info.superpower:
            return False

        d4 = list(CountryInfo.REGION_ALL[MapRegion.EUROPE])
        d3 = d4 + list(CountryInfo.REGION_ALL[MapRegion.ASIA])
        d2 = d3 + list(CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST])

        if (side == Side.USSR
                and 'NATO' in game_instance.basket[Side.US]
                and name in game_instance.calculate_nato_countries()):
            return False
        if (side == Side.USSR
                and 'US_Japan_Mutual_Defense_Pact'
                in game_instance.basket[Side.US]
                and name == 'Japan'):
            return False
        restricted = {
            4: d4,
            3: d3,
            2: d2,
        }.get(game_instance.defcon_track, ())
        if not ignore_defcon and name in restricted:
            return False

        if side == Side.USSR and country.ussr_influence_only:
            return False
        elif side == Side.US and country.us_influence_only:
            return False
        else:
            return not (country.influence[Side.USSR] == 0 and country.influence[Side.US] == 0)

    def realignment(self, game_instance, name: str, side: Side,
                    ussr_roll: int, us_roll: int, free=False,
                    ignore_defcon=False):
        '''
        The result of a given side using realignment in a country, with both dice rolls provided.

        Parameters
        ----------
        game_instance : Game object
            The game object the country resides within.
        name : str
            String representation of the country we are checking.
        side : Side
            Player side which we are checking. Can be Side.US or Side.USSR.
        us_roll, us_roll: ints
            The respective dice rolls of the realignment. Should be bounded within range(1,7).
        '''
        assert(self.can_realignment(
            game_instance, name, side, free=free,
            ignore_defcon=ignore_defcon))
        country = self[name]

        ussr_advantage = 0  # net positive is in favour of USSR
        if 'Iran_Contra_Scandal' in game_instance.basket[Side.USSR]:
            ussr_advantage += 1

        for adjacent_name in country.info.adjacent_countries:
            adjacent = self[adjacent_name]
            if adjacent.info.superpower:
                continue
            ussr_advantage -= (adjacent.control == Side.US)
            ussr_advantage += (adjacent.control == Side.USSR)

        # Superpower adjacency grants an additional +/-1 regardless of control checks.
        if 'USSR' in country.info.adjacent_countries:
            ussr_advantage += 1
        if 'US' in country.info.adjacent_countries:
            ussr_advantage -= 1

        if country.influence[Side.USSR] > country.influence[Side.US]:
            ussr_advantage += 1
        elif country.influence[Side.USSR] < country.influence[Side.US]:
            ussr_advantage -= 1

        difference = ussr_roll - us_roll + ussr_advantage
        if difference > 0:
            country.change_influence(0, -difference)
        elif difference < 0:
            country.change_influence(difference, 0)
        print(
            f'USSR rolled: {ussr_roll}, US rolled: {us_roll}, ussr_advantage = {ussr_advantage}, Difference = {difference}')



    def can_place_influence(self, game_instance, name: str, side: Side, effective_ops: int) -> bool:
        '''
        Checks if influence can be placed in a country, according to:
        1. Is there influence in the country itself, or any of its adjacent countries?
        2. If this country is controlled by the opposite power, is effective_ops at least 2?
        3. Does the card being used has at least 1 effective operation point? (so scoring cards can't be used for influence)

        Parameters
        ----------
        game_instance : Game object
            The game object the country resides within.
        name : str
            String representation of the country we are checking.
        side : Side
            Player side which we are checking. Can be Side.US or Side.USSR.
        effective_ops : int
            The number of effective operations used in the coup.
        '''
        country = self[name]

        def has_influence_around(country: Country):
            if country.info.superpower:
                return False

            countries_to_check = country.info.adjacent_countries.copy()
            countries_to_check.append(name)
            for country in countries_to_check:
                if self[country].influence[side] > 0:
                    return True
            return False

        def sufficient_ops(effective_ops: int):
            # if country is controlled by opposition, if ops > 1, return true, else false
            if country.control == side.opp:
                return True if effective_ops >= 2 else False
            else:
                return True

        def is_chernobyl():
            if side != Side.USSR:
                return True
            banned_region = next(
                (region for token, region in _CHERNOBYL_REGION.items()
                 if token in game_instance.basket[Side.US]),
                None)
            if banned_region is None:
                return True
            return name not in CountryInfo.REGION_ALL[banned_region]

        return has_influence_around(country) and sufficient_ops(effective_ops) and is_chernobyl()

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

    def build_standard(self):
        '''
        Sets the appropriate amount of influence in each country.
        '''
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


class Country:

    def __init__(self, name: str):
        self.info = CountryInfo.ALL[name]
        self.influence = [0, 0]  # ussr, then us influence

    def __repr__(self):
        if self.info.stability == 0:
            return f'Country({self.info.name}, Superpower = True, Adjacent = {self.info.adjacent_countries})'
        else:
            return f'Country({self.info.name}, \nUS_influence\t= {self.influence[Side.US]}, {self.us_influence_only}\nUSSR_influence\t= {self.influence[Side.USSR]}, {self.ussr_influence_only}\nControl \t= {self.control}'

    def get_state_str(self):
        if self.info.superpower:
            return f'{self.info.name} [Superpower]'
        else:
            ctrl = self.control
            bg_str = '\033[105mBG\033[0m ' if self.info.battleground else ''
            stab_str = f'{self.info.name} {self.info.stability}'
            if ctrl == Side.US:
                name_str = f'{bg_str:3}\033[104m{stab_str:23}\033[0m'
                ctrl_str = f'[{ctrl.name} control]'
            elif ctrl == Side.USSR:
                name_str = f'{bg_str:3}\033[101m{stab_str:23}\033[0m'
                ctrl_str = f'[{ctrl.name} control]'
            else:
                name_str = f'{bg_str:3}{stab_str:23}'
                ctrl_str = ''

            return f'{name_str}US {self.influence[Side.US]}:{self.influence[Side.USSR]} USSR {ctrl_str}'

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

    def set_influence(self, ussr_influence, us_influence):
        self.influence[Side.US] = us_influence
        self.influence[Side.USSR] = ussr_influence

    def change_influence(self, ussr_influence: int, us_influence: int):
        self.influence[Side.US] += us_influence
        self.influence[Side.USSR] += ussr_influence
        if self.influence[Side.US] < 0:
            self.influence[Side.US] = 0
        if self.influence[Side.USSR] < 0:
            self.influence[Side.USSR] = 0

    def remove_influence(self, side):
        if self.influence[side] == 0:
            return False
        self.influence[side] = 0
        return True

    def increment_influence(self, side, amt=1):
        self.influence[side] += amt
        return True

    def decrement_influence(self, side, amt=1):
        if self.influence[side] == 0:
            return False
        self.influence[side] = max(self.influence[side] - amt, 0)
        return True

    def match_influence(self, side):
        self.influence[side] = max(
            self.influence[side], self.influence[side.opp]
        )
        return True

USSR = {
    'name': 'USSR',
    'country_index': 1,
    'superpower': True,
    'stability': 999,
    'adjacent_countries': ['Finland', 'Poland', 'Romania', 'Afghanistan', 'North_Korea'],
}

US = {
    'name': 'US',
    'country_index': 2,
    'superpower': True,
    'stability': 999,
    'adjacent_countries': ['Japan', 'Mexico', 'Cuba', 'Canada'],
}

Canada = {
    'name': 'Canada',
    'country_index': 3,
    'region': 'Western Europe',
    'stability': 4,
    'adjacent_countries': ['US', 'UK'],
}

UK = {
    'name': 'UK',
    'country_index': 4,
    'region': 'Western Europe',
    'stability': 5,
    'adjacent_countries': ['Canada', 'Norway', 'Benelux', 'France'],
}

Norway = {
    'name': 'Norway',
    'country_index': 5,
    'region': 'Western Europe',
    'stability': 4,
    'adjacent_countries': ['UK', 'Sweden'],
}

Sweden = {
    'name': 'Sweden',
    'country_index': 6,
    'region': 'Western Europe',
    'stability': 4,
    'adjacent_countries': ['Norway', 'Finland', 'Denmark'],
}

Finland = {
    'name': 'Finland',
    'country_index': 7,
    'region': 'Europe',
    'stability': 4,
    'adjacent_countries': ['Sweden', 'USSR'],
}

Denmark = {
    'name': 'Denmark',
    'country_index': 8,
    'region': 'Western Europe',
    'stability': 3,
    'adjacent_countries': ['Sweden', 'West_Germany'],
}

Benelux = {
    'name': 'Benelux',
    'country_index': 9,
    'region': 'Western Europe',
    'stability': 3,
    'adjacent_countries': ['UK', 'West_Germany'],
}

France = {
    'name': 'France',
    'country_index': 10,
    'region': 'Western Europe',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['UK', 'West_Germany', 'Spain_Portugal', 'Italy', 'Algeria'],
}

Spain_Portugal = {
    'name': 'Spain_Portugal',
    'country_index': 11,
    'region': 'Western Europe',
    'stability': 2,
    'adjacent_countries': ['France', 'Italy', 'Morocco'],
}

Italy = {
    'name': 'Italy',
    'country_index': 12,
    'region': 'Western Europe',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['France', 'Spain_Portugal', 'Austria', 'Yugoslavia', 'Greece'],
}

Greece = {
    'name': 'Greece',
    'country_index': 13,
    'region': 'Western Europe',
    'stability': 2,
    'adjacent_countries': ['Italy', 'Yugoslavia', 'Bulgaria', 'Turkey'],
}

Austria = {
    'name': 'Austria',
    'country_index': 14,
    'region': 'Europe',
    'stability': 4,
    'adjacent_countries': ['West_Germany', 'East_Germany', 'Hungary', 'Italy'],
}

West_Germany = {
    'name': 'West_Germany',
    'country_index': 15,
    'region': 'Western Europe',
    'stability': 4,
    'battleground': True,
    'adjacent_countries': ['France', 'Benelux', 'Denmark', 'East_Germany', 'Austria'],
}


East_Germany = {
    'name': 'East_Germany',
    'country_index': 16,
    'region': 'Eastern Europe',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['West_Germany', 'Austria', 'Czechoslovakia', 'Poland'],
}


Poland = {
    'name': 'Poland',
    'country_index': 17,
    'region': 'Eastern Europe',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['East_Germany', 'Czechoslovakia', 'USSR'],
}


Czechoslovakia = {
    'name': 'Czechoslovakia',
    'country_index': 18,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['East_Germany', 'Poland', 'Hungary'],
}


Hungary = {
    'name': 'Hungary',
    'country_index': 19,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['Austria', 'Czechoslovakia', 'Romania', 'Yugoslavia'],
}


Yugoslavia = {
    'name': 'Yugoslavia',
    'country_index': 20,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['Italy', 'Hungary', 'Greece', 'Romania'],
}


Romania = {
    'name': 'Romania',
    'country_index': 21,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['Hungary', 'Yugoslavia', 'Turkey', 'USSR'],
}


Bulgaria = {
    'name': 'Bulgaria',
    'country_index': 22,
    'region': 'Eastern Europe',
    'stability': 3,
    'adjacent_countries': ['Greece', 'Turkey'],
}


Turkey = {
    'name': 'Turkey',
    'country_index': 23,
    'region': 'Western Europe',
    'stability': 2,
    'adjacent_countries': ['Greece', 'Bulgaria', 'Romania', 'Syria'],
}


Libya = {
    'name': 'Libya',
    'country_index': 24,
    'region': 'Middle East',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Tunisia', 'Egypt'],
}


Egypt = {
    'name': 'Egypt',
    'country_index': 25,
    'region': 'Middle East',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Libya', 'Israel', 'Sudan'],
}


Israel = {
    'name': 'Israel',
    'country_index': 26,
    'region': 'Middle East',
    'stability': 4,
    'battleground': True,
    'adjacent_countries': ['Lebanon', 'Syria', 'Jordan', 'Egypt'],
}


Lebanon = {
    'name': 'Lebanon',
    'country_index': 27,
    'region': 'Middle East',
    'stability': 1,
    'adjacent_countries': ['Israel', 'Syria', 'Jordan'],
}


Syria = {
    'name': 'Syria',
    'country_index': 28,
    'region': 'Middle East',
    'stability': 2,
    'adjacent_countries': ['Israel', 'Lebanon', 'Turkey'],
}


Iraq = {
    'name': 'Iraq',
    'country_index': 29,
    'region': 'Middle East',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Jordan', 'Saudi_Arabia', 'Gulf_States', 'Iran'],
}


Iran = {
    'name': 'Iran',
    'country_index': 30,
    'region': 'Middle East',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Iraq', 'Afghanistan', 'Pakistan'],
}


Jordan = {
    'name': 'Jordan',
    'country_index': 31,
    'region': 'Middle East',
    'stability': 2,
    'adjacent_countries': ['Iraq', 'Israel', 'Lebanon', 'Saudi_Arabia'],
}


Gulf_States = {
    'name': 'Gulf_States',
    'country_index': 32,
    'region': 'Middle East',
    'stability': 3,
    'adjacent_countries': ['Iraq', 'Saudi_Arabia'],
}


Saudi_Arabia = {
    'name': 'Saudi_Arabia',
    'country_index': 33,
    'region': 'Middle East',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Iraq', 'Jordan', 'Gulf_States'],
}


Afghanistan = {
    'name': 'Afghanistan',
    'country_index': 34,
    'region': 'Asia',
    'stability': 2,
    'adjacent_countries': ['USSR', 'Iran', 'Pakistan'],
}


Pakistan = {
    'name': 'Pakistan',
    'country_index': 35,
    'region': 'Asia',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Afghanistan', 'Iran', 'India'],
}


India = {
    'name': 'India',
    'country_index': 36,
    'region': 'Asia',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Pakistan', 'Burma'],
}


Burma = {
    'name': 'Burma',
    'country_index': 37,
    'region': 'Southeast Asia',
    'stability': 2,
    'adjacent_countries': ['India', 'Laos_Cambodia'],
}


Laos_Cambodia = {
    'name': 'Laos_Cambodia',
    'country_index': 38,
    'region': 'Southeast Asia',
    'stability': 1,
    'adjacent_countries': ['Burma', 'Thailand', 'Vietnam'],
}


Thailand = {
    'name': 'Thailand',
    'country_index': 39,
    'region': 'Southeast Asia',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Laos_Cambodia', 'Vietnam', 'Malaysia'],
}


Vietnam = {
    'name': 'Vietnam',
    'country_index': 40,
    'region': 'Southeast Asia',
    'stability': 1,
    'adjacent_countries': ['Laos_Cambodia', 'Thailand'],
}


Malaysia = {
    'name': 'Malaysia',
    'country_index': 41,
    'region': 'Southeast Asia',
    'stability': 2,
    'adjacent_countries': ['Thailand', 'Indonesia', 'Australia'],
}


Australia = {
    'name': 'Australia',
    'country_index': 42,
    'region': 'Asia',
    'stability': 4,
    'adjacent_countries': ['Malaysia'],
}


Indonesia = {
    'name': 'Indonesia',
    'country_index': 43,
    'region': 'Southeast Asia',
    'stability': 1,
    'adjacent_countries': ['Malaysia', 'Philippines'],
}


Philippines = {
    'name': 'Philippines',
    'country_index': 44,
    'region': 'Southeast Asia',
    'stability': 2,
    'adjacent_countries': ['Indonesia', 'Japan'],
}


Japan = {
    'name': 'Japan',
    'country_index': 45,
    'region': 'Asia',
    'stability': 4,
    'battleground': True,
    'adjacent_countries': ['Philippines', 'Taiwan', 'South_Korea', 'US'],
}


Taiwan = {
    'name': 'Taiwan',
    'country_index': 46,
    'region': 'Asia',
    'stability': 3,
    'adjacent_countries': ['Japan', 'South_Korea'],
}


South_Korea = {
    'name': 'South_Korea',
    'country_index': 47,
    'region': 'Asia',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Japan', 'Taiwan', 'North_Korea'],
}


North_Korea = {
    'name': 'North_Korea',
    'country_index': 48,
    'region': 'Asia',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['South_Korea', 'USSR'],
}


Algeria = {
    'name': 'Algeria',
    'country_index': 49,
    'region': 'Africa',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Morocco', 'Saharan_States', 'Tunisia', 'France'],
}


Morocco = {
    'name': 'Morocco',
    'country_index': 50,
    'region': 'Africa',
    'stability': 3,
    'adjacent_countries': ['Algeria', 'West_African_States', 'Spain_Portugal'],
}


Tunisia = {
    'name': 'Tunisia',
    'country_index': 51,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['Algeria', 'Libya'],
}


West_African_States = {
    'name': 'West_African_States',
    'country_index': 52,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['Morocco', 'Ivory_Coast'],
}


Ivory_Coast = {
    'name': 'Ivory_Coast',
    'country_index': 53,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['West_African_States', 'Nigeria'],
}


Saharan_States = {
    'name': 'Saharan_States',
    'country_index': 54,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Algeria', 'Nigeria'],
}


Nigeria = {
    'name': 'Nigeria',
    'country_index': 55,
    'region': 'Africa',
    'stability': 1,
    'battleground': True,
    'adjacent_countries': ['Ivory_Coast', 'Saharan_States', 'Cameroon'],
}


Cameroon = {
    'name': 'Cameroon',
    'country_index': 56,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Nigeria', 'Zaire'],
}


Zaire = {
    'name': 'Zaire',
    'country_index': 57,
    'region': 'Africa',
    'stability': 1,
    'battleground': True,
    'adjacent_countries': ['Cameroon', 'Angola', 'Zimbabwe'],
}


Angola = {
    'name': 'Angola',
    'country_index': 58,
    'region': 'Africa',
    'stability': 1,
    'battleground': True,
    'adjacent_countries': ['Zaire', 'Botswana', 'South_Africa'],
}


South_Africa = {
    'name': 'South_Africa',
    'country_index': 59,
    'region': 'Africa',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Angola', 'Botswana'],
}


Botswana = {
    'name': 'Botswana',
    'country_index': 60,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['Angola', 'South_Africa', 'Zimbabwe'],
}


Zimbabwe = {
    'name': 'Zimbabwe',
    'country_index': 61,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Zaire', 'Botswana', 'SE_African_States'],
}


SE_African_States = {
    'name': 'SE_African_States',
    'country_index': 62,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Zimbabwe', 'Kenya'],
}


Kenya = {
    'name': 'Kenya',
    'country_index': 63,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['SE_African_States', 'Somalia'],
}


Somalia = {
    'name': 'Somalia',
    'country_index': 64,
    'region': 'Africa',
    'stability': 2,
    'adjacent_countries': ['Kenya', 'Ethiopia'],
}


Ethiopia = {
    'name': 'Ethiopia',
    'country_index': 65,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Somalia', 'Sudan'],
}


Sudan = {
    'name': 'Sudan',
    'country_index': 66,
    'region': 'Africa',
    'stability': 1,
    'adjacent_countries': ['Ethiopia', 'Egypt'],
}


Mexico = {
    'name': 'Mexico',
    'country_index': 67,
    'region': 'Central America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Guatemala', 'US'],
}


Guatemala = {
    'name': 'Guatemala',
    'country_index': 68,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Mexico', 'El_Salvador', 'Honduras'],
}


El_Salvador = {
    'name': 'El_Salvador',
    'country_index': 69,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Guatemala', 'Honduras'],
}


Honduras = {
    'name': 'Honduras',
    'country_index': 70,
    'region': 'Central America',
    'stability': 2,
    'adjacent_countries': ['Guatemala', 'El_Salvador', 'Costa_Rica', 'Nicaragua'],
}


Costa_Rica = {
    'name': 'Costa_Rica',
    'country_index': 71,
    'region': 'Central America',
    'stability': 3,
    'adjacent_countries': ['Honduras', 'Nicaragua', 'Panama'],
}


Panama = {
    'name': 'Panama',
    'country_index': 72,
    'region': 'Central America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Costa_Rica', 'Colombia'],
}


Nicaragua = {
    'name': 'Nicaragua',
    'country_index': 73,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Costa_Rica', 'Honduras', 'Cuba'],
}


Cuba = {
    'name': 'Cuba',
    'country_index': 74,
    'region': 'Central America',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Nicaragua', 'Haiti', 'US'],
}


Haiti = {
    'name': 'Haiti',
    'country_index': 75,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Cuba', 'Dominican_Republic'],
}


Dominican_Republic = {
    'name': 'Dominican_Republic',
    'country_index': 76,
    'region': 'Central America',
    'stability': 1,
    'adjacent_countries': ['Haiti'],
}

Colombia = {
    'name': 'Colombia',
    'country_index': 77,
    'region': 'South America',
    'stability': 1,
    'adjacent_countries': ['Panama', 'Ecuador', 'Venezuela'],
}


Ecuador = {
    'name': 'Ecuador',
    'country_index': 78,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Colombia', 'Peru'],
}


Peru = {
    'name': 'Peru',
    'country_index': 79,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Ecuador', 'Bolivia', 'Chile'],
}


Chile = {
    'name': 'Chile',
    'country_index': 80,
    'region': 'South America',
    'stability': 3,
    'battleground': True,
    'adjacent_countries': ['Peru', 'Argentina'],
}


Argentina = {
    'name': 'Argentina',
    'country_index': 81,
    'region': 'South America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Chile', 'Uruguay', 'Paraguay'],
}


Uruguay = {
    'name': 'Uruguay',
    'country_index': 82,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Argentina', 'Paraguay', 'Brazil'],
}


Paraguay = {
    'name': 'Paraguay',
    'country_index': 83,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Argentina', 'Uruguay', 'Bolivia'],
}


Bolivia = {
    'name': 'Bolivia',
    'country_index': 84,
    'region': 'South America',
    'stability': 2,
    'adjacent_countries': ['Peru', 'Paraguay'],
}


Brazil = {
    'name': 'Brazil',
    'country_index': 85,
    'region': 'South America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Uruguay', 'Venezuela'],
}


Venezuela = {
    'name': 'Venezuela',
    'country_index': 86,
    'region': 'South America',
    'stability': 2,
    'battleground': True,
    'adjacent_countries': ['Colombia', 'Brazil'],
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

# 按 DEFCON 级别禁政变的国家集合（静态：欧洲 / 欧洲+亚洲 / 欧洲+亚洲+中东）。
# 预计算一次——can_coup 在 RL rollout 热路径上逐国调用，每次重建 list 是浪费。
_DEFCON_RESTRICTED = {
    4: frozenset(CountryInfo.REGION_ALL[MapRegion.EUROPE]),
    3: frozenset(CountryInfo.REGION_ALL[MapRegion.EUROPE])
       | frozenset(CountryInfo.REGION_ALL[MapRegion.ASIA]),
    2: frozenset(CountryInfo.REGION_ALL[MapRegion.EUROPE])
       | frozenset(CountryInfo.REGION_ALL[MapRegion.ASIA])
       | frozenset(CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST]),
}

# Chernobyl 效果 token → 受限制区域（表化原 6 分支 if/elif）。
_CHERNOBYL_REGION = {
    'Chernobyl_Europe': MapRegion.EUROPE,
    'Chernobyl_Middle_East': MapRegion.MIDDLE_EAST,
    'Chernobyl_Asia': MapRegion.ASIA,
    'Chernobyl_Africa': MapRegion.AFRICA,
    'Chernobyl_Central_America': MapRegion.CENTRAL_AMERICA,
    'Chernobyl_South_America': MapRegion.SOUTH_AMERICA,
}
