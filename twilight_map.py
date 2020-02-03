all_countries = dict()

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

USSR = {
    "country_name": "USSR",
    "country_index": 1,
    "superpower": True,
    "adjacent_countries": ["Finland", "Poland", "Romania", "Afghanistan", "North_Korea", "Chinese_Civil_War"],
    "us_influence": 0,
    "ussr_influence": 999,
}

USA = {
    "country_name": "USA",
    "country_index": 2,
    "superpower": True,
    "adjacent_countries": ["Japan", "Mexico", "Cuba", "Canada"],
    "us_influence": 999,
    "ussr_influence": 0,
}

Canada = {
    "country_name": "Canada",
    "country_index": 3,
    "region": "Western Europe",
    "stability": 4,
    "adjacent_countries": ["USA", "UK"],
    "us_influence": 0,
    "ussr_influence": 0,
}

UK = {
    "country_name": "UK",
    "country_index": 4,
    "region": "Western Europe",
    "stability": 5,
    "adjacent_countries": ["Canada", "Norway", "Benelux", "France"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Norway = {
    "country_name": "Norway",
    "country_index": 5,
    "region": "Western Europe",
    "stability": 4,
    "adjacent_countries": ["UK", "Sweden"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Sweden = {
    "country_name": "Sweden",
    "country_index": 6,
    "region": "Western Europe",
    "stability": 4,
    "adjacent_countries": ["Norway", "Finland", "Denmark"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Finland = {
    "country_name": "Finland",
    "country_index": 7,
    "region": "Europe",
    "stability": 4,
    "adjacent_countries": ["Sweden", "USSR"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Denmark = {
    "country_name": "Denmark",
    "country_index": 8,
    "region": "Western Europe",
    "stability": 3,
    "adjacent_countries": ["Sweden", "West_Germany"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Benelux = {
    "country_name": "Benelux",
    "country_index": 9,
    "region": "Western Europe",
    "stability": 3,
    "adjacent_countries": ["UK", "West_Germany"],
    "us_influence": 0,
    "ussr_influence": 0,
}

France = {
    "country_name": "France",
    "country_index": 10,
    "region": "Western Europe",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["UK", "West_Germany", "Spain_Portugal", "Italy", "Algeria"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Spain_Portugal = {
    "country_name": "Spain_Portugal",
    "country_index": 11,
    "region": "Western Europe",
    "stability": 2,
    "adjacent_countries": ["France", "Italy", "Morocco"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Italy = {
    "country_name": "Italy",
    "country_index": 12,
    "region": "Western Europe",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["France", "Spain_Portugal", "Austria", "Yugoslavia", "Greece"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Greece = {
    "country_name": "Greece",
    "country_index": 13,
    "region": "Western Europe",
    "stability": 2,
    "adjacent_countries": ["Italy", "Yugoslavia", "Bulgaria", "Turkey"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Austria = {
    "country_name": "Austria",
    "country_index": 14,
    "region": "Europe",
    "stability": 4,
    "adjacent_countries": ["West_Germany", "East_Germany", "Hungary", "Italy"],
    "us_influence": 0,
    "ussr_influence": 0,
}

West_Germany = {
    "country_name": "West_Germany",
    "country_index": 15,
    "region": "Western Europe",
    "stability": 4,
    "battleground": True,
    "adjacent_countries": ["France", "Benelux", "Denmark", "East_Germany", "Austria"],
    "us_influence": 0,
    "ussr_influence": 0,
}


East_Germany = {
    "country_name": "East_Germany",
    "country_index": 16,
    "region": "Eastern Europe",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["West_Germany", "Austria", "Czechoslovakia", "Poland"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Poland = {
    "country_name": "Poland",
    "country_index": 17,
    "region": "Eastern Europe",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["East_Germany", "Czechoslovakia", "USSR"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Czechoslovakia = {
    "country_name": "Czechoslovakia",
    "country_index": 18,
    "region": "Eastern Europe",
    "stability": 3,
    "adjacent_countries": ["East_Germany", "Poland", "Hungary"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Hungary = {
    "country_name": "Hungary",
    "country_index": 19,
    "region": "Eastern Europe",
    "stability": 3,
    "adjacent_countries": ["Austria", "Czechoslovakia", "Romania", "Yugoslavia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Yugoslavia = {
    "country_name": "Yugoslavia",
    "country_index": 20,
    "region": "Eastern Europe",
    "stability": 3,
    "adjacent_countries": ["Italy", "Hungary", "Greece", "Romania"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Romania = {
    "country_name": "Romania",
    "country_index": 21,
    "region": "Eastern Europe",
    "stability": 3,
    "adjacent_countries": ["Hungary", "Yugoslavia", "Turkey", "USSR"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Bulgaria = {
    "country_name": "Bulgaria",
    "country_index": 22,
    "region": "Eastern Europe",
    "stability": 3,
    "adjacent_countries": ["Greece", "Turkey"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Turkey = {
    "country_name": "Turkey",
    "country_index": 23,
    "region": "Western Europe",
    "stability": 2,
    "adjacent_countries": ["Greece", "Bulgaria", "Romania", "Syria"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Libya = {
    "country_name": "Libya",
    "country_index": 24,
    "region": "Middle East",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Tunisia", "Egypt"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Egypt = {
    "country_name": "Egypt",
    "country_index": 25,
    "region": "Middle East",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Libya", "Israel", "Sudan"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Israel = {
    "country_name": "Israel",
    "country_index": 26,
    "region": "Middle East",
    "stability": 4,
    "battleground": True,
    "adjacent_countries": ["Lebanon", "Syria", "Jordan", "Egypt"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Lebanon = {
    "country_name": "Lebanon",
    "country_index": 27,
    "region": "Middle East",
    "stability": 1,
    "adjacent_countries": ["Israel", "Syria", "Jordan"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Syria = {
    "country_name": "Syria",
    "country_index": 28,
    "region": "Middle East",
    "stability": 2,
    "adjacent_countries": ["Israel", "Lebanon", "Turkey"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Iraq = {
    "country_name": "Iraq",
    "country_index": 29,
    "region": "Middle East",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["Jordan", "Saudi_Arabia", "Gulf_States", "Iran"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Iran = {
    "country_name": "Iran",
    "country_index": 30,
    "region": "Middle East",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Iraq", "Afghanistan", "Pakistan"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Jordan = {
    "country_name": "Jordan",
    "country_index": 31,
    "region": "Middle East",
    "stability": 2,
    "adjacent_countries": ["Iraq", "Israel", "Lebanon", "Saudi_Arabia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Gulf_States = {
    "country_name": "Gulf_States",
    "country_index": 32,
    "region": "Middle East",
    "stability": 3,
    "adjacent_countries": ["Iraq", "Saudi_Arabia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Saudi_Arabia = {
    "country_name": "Saudi_Arabia",
    "country_index": 33,
    "region": "Middle East",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["Iraq", "Jordan", "Gulf_States"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Afghanistan = {
    "country_name": "Afghanistan",
    "country_index": 34,
    "region": "Asia",
    "stability": 2,
    "adjacent_countries": ["USSR", "Iran", "Pakistan"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Pakistan = {
    "country_name": "Pakistan",
    "country_index": 35,
    "region": "Asia",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Afghanistan", "Iran", "India"],
    "us_influence": 0,
    "ussr_influence": 0,
}


India = {
    "country_name": "India",
    "country_index": 36,
    "region": "Asia",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["Pakistan", "Burma"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Burma = {
    "country_name": "Burma",
    "country_index": 37,
    "region": "Southeast Asia",
    "stability": 2,
    "adjacent_countries": ["India", "Laos_Cambodia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Laos_Cambodia = {
    "country_name": "Laos_Cambodia",
    "country_index": 38,
    "region": "Southeast Asia",
    "stability": 1,
    "adjacent_countries": ["Burma", "Thailand", "Vietnam"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Thailand = {
    "country_name": "Thailand",
    "country_index": 39,
    "region": "Southeast Asia",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Laos_Cambodia", "Vietnam", "Malaysia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Vietnam = {
    "country_name": "Vietnam",
    "country_index": 40,
    "region": "Southeast Asia",
    "stability": 1,
    "adjacent_countries": ["Laos_Cambodia", "Thailand"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Malaysia = {
    "country_name": "Malaysia",
    "country_index": 41,
    "region": "Southeast Asia",
    "stability": 2,
    "adjacent_countries": ["Thailand", "Indonesia", "Australia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Australia = {
    "country_name": "Australia",
    "country_index": 42,
    "region": "Asia",
    "stability": 4,
    "adjacent_countries": ["Malaysia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Indonesia = {
    "country_name": "Indonesia",
    "country_index": 43,
    "region": "Southeast Asia",
    "stability": 1,
    "adjacent_countries": ["Malaysia", "Philippines"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Philippines = {
    "country_name": "Philippines",
    "country_index": 44,
    "region": "Southeast Asia",
    "stability": 2,
    "adjacent_countries": ["Indonesia", "Japan"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Japan = {
    "country_name": "Japan",
    "country_index": 45,
    "region": "Asia",
    "stability": 4,
    "battleground": True,
    "adjacent_countries": ["Philippines", "Taiwan", "South_Korea", "USA"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Taiwan = {
    "country_name": "Taiwan",
    "country_index": 46,
    "region": "Asia",
    "stability": 3,
    "adjacent_countries": ["Japan", "South_Korea"],
    "us_influence": 0,
    "ussr_influence": 0,
}


South_Korea = {
    "country_name": "South_Korea",
    "country_index": 47,
    "region": "Asia",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["Japan", "Taiwan", "North_Korea"],
    "us_influence": 0,
    "ussr_influence": 0,
}


North_Korea = {
    "country_name": "North_Korea",
    "country_index": 48,
    "region": "Asia",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["South_Korea", "USSR"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Algeria = {
    "country_name": "Algeria",
    "country_index": 49,
    "region": "Africa",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Morocco", "Saharan_States", "Tunisia", "France"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Morocco = {
    "country_name": "Morocco",
    "country_index": 50,
    "region": "Africa",
    "stability": 3,
    "adjacent_countries": ["Algeria", "West_African_States", "Spain_Portugal"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Tunisia = {
    "country_name": "Tunisia",
    "country_index": 51,
    "region": "Africa",
    "stability": 2,
    "adjacent_countries": ["Algeria", "Libya"],
    "us_influence": 0,
    "ussr_influence": 0,
}


West_African_States = {
    "country_name": "West_African_States",
    "country_index": 52,
    "region": "Africa",
    "stability": 2,
    "adjacent_countries": ["Morocco", "Ivory_Coast"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Ivory_Coast = {
    "country_name": "Ivory_Coast",
    "country_index": 53,
    "region": "Africa",
    "stability": 2,
    "adjacent_countries": ["West_African_States", "Nigeria"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Saharan_States = {
    "country_name": "Saharan_States",
    "country_index": 54,
    "region": "Africa",
    "stability": 1,
    "adjacent_countries": ["Algeria", "Nigeria"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Nigeria = {
    "country_name": "Nigeria",
    "country_index": 55,
    "region": "Africa",
    "stability": 1,
    "battleground": True,
    "adjacent_countries": ["Ivory_Coast", "Saharan_States", "Cameroon"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Cameroon = {
    "country_name": "Cameroon",
    "country_index": 56,
    "region": "Africa",
    "stability": 1,
    "adjacent_countries": ["Nigeria", "Zaire"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Zaire = {
    "country_name": "Zaire",
    "country_index": 57,
    "region": "Africa",
    "stability": 1,
    "battleground": True,
    "adjacent_countries": ["Cameroon", "Angola", "Zimbabwe"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Angola = {
    "country_name": "Angola",
    "country_index": 58,
    "region": "Africa",
    "stability": 1,
    "battleground": True,
    "adjacent_countries": ["Zaire", "Botswana", "South_Africa"],
    "us_influence": 0,
    "ussr_influence": 0,
}


South_Africa = {
    "country_name": "South_Africa",
    "country_index": 59,
    "region": "Africa",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["Angola", "Botswana"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Botswana = {
    "country_name": "Botswana",
    "country_index": 60,
    "region": "Africa",
    "stability": 2,
    "adjacent_countries": ["Angola", "South_Africa", "Zimbabwe"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Zimbabwe = {
    "country_name": "Zimbabwe",
    "country_index": 61,
    "region": "Africa",
    "stability": 1,
    "adjacent_countries": ["Zaire", "Botswana", "SE_African_States"],
    "us_influence": 0,
    "ussr_influence": 0,
}


SE_African_States = {
    "country_name": "SE_African_States",
    "country_index": 62,
    "region": "Africa",
    "stability": 1,
    "adjacent_countries": ["Zimbabwe", "Kenya"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Kenya = {
    "country_name": "Kenya",
    "country_index": 63,
    "region": "Africa",
    "stability": 2,
    "adjacent_countries": ["SE_African_States", "Somalia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Somalia = {
    "country_name": "Somalia",
    "country_index": 64,
    "region": "Africa",
    "stability": 2,
    "adjacent_countries": ["Kenya", "Ethiopia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Ethiopia = {
    "country_name": "Ethiopia",
    "country_index": 65,
    "region": "Africa",
    "stability": 1,
    "adjacent_countries": ["Somalia", "Sudan"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Sudan = {
    "country_name": "Sudan",
    "country_index": 66,
    "region": "Africa",
    "stability": 1,
    "adjacent_countries": ["Ethiopia", "Egypt"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Mexico = {
    "country_name": "Mexico",
    "country_index": 67,
    "region": "Central America",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Guatemala", "USA"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Guatemala = {
    "country_name": "Guatemala",
    "country_index": 68,
    "region": "Central America",
    "stability": 1,
    "adjacent_countries": ["Mexico", "El_Salvador", "Honduras"],
    "us_influence": 0,
    "ussr_influence": 0,
}


El_Salvador = {
    "country_name": "El_Salvador",
    "country_index": 69,
    "region": "Central America",
    "stability": 1,
    "adjacent_countries": ["Guatemala", "Honduras"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Honduras = {
    "country_name": "Honduras",
    "country_index": 70,
    "region": "Central America",
    "stability": 2,
    "adjacent_countries": ["Guatemala", "El_Salvador", "Costa_Rica", "Nicaragua"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Costa_Rica = {
    "country_name": "Costa_Rica",
    "country_index": 71,
    "region": "Central America",
    "stability": 3,
    "adjacent_countries": ["Honduras", "Nicaragua", "Panama"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Panama = {
    "country_name": "Panama",
    "country_index": 72,
    "region": "Central America",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Costa_Rica", "Colombia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Nicaragua = {
    "country_name": "Nicaragua",
    "country_index": 73,
    "region": "Central America",
    "stability": 1,
    "adjacent_countries": ["Costa_Rica", "Honduras", "Cuba"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Cuba = {
    "country_name": "Cuba",
    "country_index": 74,
    "region": "Central America",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["Nicaragua", "Haiti", "USA"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Haiti = {
    "country_name": "Haiti",
    "country_index": 75,
    "region": "Central America",
    "stability": 1,
    "adjacent_countries": ["Cuba", "Dominican_Republic"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Dominican_Republic = {
    "country_name": "Dominican_Republic",
    "country_index": 76,
    "region": "Central America",
    "stability": 1,
    "adjacent_countries": ["Haiti"],
    "us_influence": 0,
    "ussr_influence": 0,
}

Colombia = {
    "country_name": "Colombia",
    "country_index": 77,
    "region": "South America",
    "stability": 1,
    "adjacent_countries": ["Panama", "Ecuador", "Venezuela"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Ecuador = {
    "country_name": "Ecuador",
    "country_index": 78,
    "region": "South America",
    "stability": 2,
    "adjacent_countries": ["Colombia", "Peru"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Peru = {
    "country_name": "Peru",
    "country_index": 79,
    "region" : "South America",
    "stability": 2,
    "adjacent_countries": ["Ecuador", "Bolivia", "Chile"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Chile = {
    "country_name": "Chile",
    "country_index": 80,
    "region": "South America",
    "stability": 3,
    "battleground": True,
    "adjacent_countries": ["Peru", "Argentina"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Argentina = {
    "country_name": "Argentina",
    "country_index": 81,
    "region": "South America",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Chile", "Uruguay", "Paraguay"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Uruguay = {
    "country_name": "Uruguay",
    "country_index": 82,
    "region": "South America",
    "stability": 2,
    "adjacent_countries": ["Argentina", "Paraguay", "Brazil"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Paraguay = {
    "country_name": "Paraguay",
    "country_index": 83,
    "region": "South America",
    "stability": 2,
    "adjacent_countries": ["Argentina", "Uruguay", "Bolivia"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Bolivia = {
    "country_name": "Bolivia",
    "country_index": 84,
    "region": "South America",
    "stability": 2,
    "adjacent_countries": ["Peru", "Paraguay"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Brazil = {
    "country_name": "Brazil",
    "country_index": 85,
    "region": "South America",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Uruguay", "Venezuela"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Venezuela = {
    "country_name": "Venezuela",
    "country_index": 86,
    "region": "South America",
    "stability": 2,
    "battleground": True,
    "adjacent_countries": ["Colombia", "Brazil"],
    "us_influence": 0,
    "ussr_influence": 0,
}


Chinese_Civil_War = {
    "country_name": "Chinese_Civil_War",
    "country_index": 87,
    "chinese_civil_war": True,
    "region": "Asia",
    "stability": 3,
    "adjacent_countries": ["USSR"],
    "us_influence": 0,
    "ussr_influence": 0,
}

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

build_standard_map()
