from twilight_map import MapRegion, CountryInfo
from twilight_enums import Side, MapRegion, InputType, CardAction


class CardInfo:
    '''
    Cards should be able to be used for:
    1. Event
    2. Realignment
    3. Coup
    4. Placing influence
    5. Space race
    6. Trigger event first >> realignment/coup/influence
    '''

    ALL = dict()

    def __init__(self, name='', type='', stage='', card_index=0,
                 optional_card=False, ops=0,
                 event_text='', scoring_region='', may_be_held=True,
                 owner='NEUTRAL', remove_if_used_as_event=False,
                 resolve_headline_first=False, can_headline=True,
                 **kwargs):
        self.name = name
        self.type = type
        self.stage = stage
        self.card_index = card_index
        self.ops = ops
        self.text = event_text
        self.owner = Side[owner]
        self.optional = optional_card

        self.event_unique = remove_if_used_as_event
        self.scoring_region = scoring_region
        self.may_be_held = may_be_held
        self.resolve_headline_first = resolve_headline_first
        self.can_headline = can_headline

        CardInfo.ALL[self.name] = self

    def __repr__(self):
        if self.ops == 0:
            return self.name
        else:
            return f'{self.name} - {self.ops}'

    def __eq__(self, other):
        return self.name == other

    def __deepcopy__(self, memo):
        return self


class GameCards:

    def __init__(self):

        self.ALL = dict()
        self.index_card_mapping = dict()  # Create mapping of (k,v) = (card_index, name)
        self.early_war = []
        self.mid_war = []
        self.late_war = []

        for name in CardInfo.ALL.keys():
            self.ALL[name] = Card(name)
            if self.ALL[name].info.stage == 'Early War':
                self.early_war.append(name)
            if self.ALL[name].info.stage == 'Mid War':
                self.mid_war.append(name)
            if self.ALL[name].info.stage == 'Late War':
                self.late_war.append(name)
            self.index_card_mapping[self.ALL[name].info.card_index] = name

    def __getitem__(self, item):
        return self.ALL[item]


class Card():
    def __init__(self, name):
        self.info = CardInfo.ALL[name]
        self.is_playable = True

    def __repr__(self):
        if self.info.ops == 0:
            return self.info.name
        else:
            return f'{self.info.name} - {self.info.ops}'

    def __eq__(self, other):
        return self.info.name == other


# --
# -- EARLY WAR
# --
Asia_Scoring = {
    'name': 'Asia_Scoring',
    'type': 'Scoring',
    'stage': 'Early War',
    'card_index': 1,
    'scoring_region': 'Asia',
    'event_text': 'Both sides score: Presence: 3, Domination: 7, Control: 9. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower',
    'may_be_held': False
}


Europe_Scoring = {
    'name': 'Europe_Scoring',
    'type': 'Scoring',
    'stage': 'Early War',
    'card_index': 2,
    'scoring_region': 'Europe',
    'event_text': 'Both sides score: Presence: 3, Domination: 7, Control: VICTORY. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower',
    'may_be_held': False,
}


Middle_East_Scoring = {
    'name': 'Middle_East_Scoring',
    'type': 'Scoring',
    'stage': 'Early War',
    'card_index': 3,
    'scoring_region': 'Middle East',
    'event_text': 'Both sides score: Presence: 3, Domination: 5, Control: 7. +1 per controlled Battleground Country in Region',
    'may_be_held': False,
}


Duck_and_Cover = {
    'name': 'Duck_and_Cover',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 4,
    'ops': 3,
    'owner': 'US',
    'event_text': 'Degrade DEFCON one level. Then US player earns VPs equal to 5 minus current DEFCON level.',
}

Five_Year_Plan = {
    'name': 'Five_Year_Plan',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 5,
    'ops': 3,
    'owner': 'US',
    'event_text': 'USSR player must randomly discard one card. If the card is a US associated Event, the Event occurs immediately. If the card is a USSR associated Event or and Event applicable to both players, then the card must be discarded without triggering the Event.',
}

The_China_Card = {
    'name': 'The_China_Card',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 6,
    'ops': 4,
    'owner': 'NEUTRAL',
    'can_headline': False,
    'event_text': 'Begins the game with the USSR player. +1 Operations value when all points are used in Asia. Pass to opponent after play. +1 VP for the player holding this card at the end of Turn 10. Cancels effect of \'Formosan Resolution\' if this card is played by the US player.',
}

Socialist_Governments = {
    'name': 'Socialist_Governments',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 7,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'Unplayable as an event if \'The Iron Lady\' is in effect. Remove US Influence in Western Europe by a total of 3 Influence points, removing no more than 2 per country.',
}

Fidel = {
    'name': 'Fidel',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 8,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'Remove all US Influence in Cuba. USSR gains sufficient Influence in Cuba for Control.',
    'remove_if_used_as_event': True,
}


Vietnam_Revolts = {
    'name': 'Vietnam_Revolts',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 9,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'Add 2 USSR Influence in Vietnam. For the remainder of the turn, the Soviet player may add 1 Operations point to any card that uses all points in Southeast Asia.',
    'remove_if_used_as_event': True,
}


Blockade = {
    'name': 'Blockade',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 10,
    'ops': 1,
    'owner': 'USSR',
    'event_text': 'Unless US Player immediately discards a \'3\' or more value Operations card, eliminate all US Influence in West Germany.',
    'remove_if_used_as_event': True,
}


Korean_War = {
    'name': 'Korean_War',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 11,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'North Korea invades South Korea. Roll one die and subtract 1 for every US Controlled country adjacent to South Korea. USSR Victory on modified die roll 4-6. USSR add 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in South Korea with USSR Influence.',
    'remove_if_used_as_event': True,
}


Romanian_Abdication = {
    'name': 'Romanian_Abdication',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 12,
    'ops': 1,
    'owner': 'USSR',
    'event_text': 'Remove all US Influence in Romania. USSR gains sufficient Influence in Romania for Control.',
    'remove_if_used_as_event': True,
}


Arab_Israeli_War = {
    'name': 'Arab_Israeli_War',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 13,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'A Pan-Arab Coalition invades Israel. Roll one die and subtract 1 for US Control of Israel and for US-controlled country adjacent to Israel. USSR Victory on modified die roll 4-6. USSR adds 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in Israel with USSR Influence.',
}


COMECON = {
    'name': 'COMECON',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 14,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'Add 1 USSR Influence in each of four non-US Controlled countries in Eastern Europe.',
    'remove_if_used_as_event': True,
}


Nasser = {
    'name': 'Nasser',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 15,
    'ops': 1,
    'owner': 'USSR',
    'event_text': 'Add 2 USSR Influence in Egypt. Remove half (rounded up) of the US Influence in Egypt.',
    'remove_if_used_as_event': True,
}


Warsaw_Pact_Formed = {
    'name': 'Warsaw_Pact_Formed',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 16,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'Remove all US Influence from four countries in Eastern Europe, or add 5 USSR Influence in Eastern Europe, adding no more than 2 per country. Allow play of NATO.',
    'remove_if_used_as_event': True,
}


De_Gaulle_Leads_France = {
    'name': 'De_Gaulle_Leads_France',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 17,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'Remove 2 US Influence in France, add 1 USSR Influence. Cancels effects of NATO for France.',
    'remove_if_used_as_event': True,
}


Captured_Nazi_Scientist = {
    'name': 'Captured_Nazi_Scientist',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 18,
    'ops': 1,
    'owner': 'NEUTRAL',
    'event_text': 'Advance player\'s Space Race marker one box.',
    'remove_if_used_as_event': True,
}


Truman_Doctrine = {
    'name': 'Truman_Doctrine',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 19,
    'ops': 1,
    'owner': 'US',
    'event_text': 'Remove all USSR Influence markers in one uncontrolled country in Europe.',
    'remove_if_used_as_event': True,
}


Olympic_Games = {
    'name': 'Olympic_Games',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 20,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'Player sponsors Olympics. Opponent may participate or boycott. If Opponent participates, each player rolls one die, with the sponsor adding 2 to his roll. High roll gains 2 VP. Reroll ties If Opponent boycotts, degrade DEFCON one level and the Sponsor may Conduct Operations as if they played a 4 Ops card.',
}


NATO = {
    'name': 'NATO',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 21,
    'ops': 4,
    'owner': 'US',
    'event_text': 'Play after \'Marshall Plan\' or \'Warsaw Pact\'. USSR player may no longer make Coup or Realignment rolls in any US Controlled countries in Europe. US Controlled countries in Europe may not be attacked by play of the Brush War event.',
    'remove_if_used_as_event': True,
}


Independent_Reds = {
    'name': 'Independent_Reds',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 22,
    'ops': 2,
    'owner': 'US',
    'event_text': 'Adds sufficient US Influence in either Yugoslavia, Romania, Bulgaria, Hungary, or Czechoslavakia to equal USSR Influence.',
    'remove_if_used_as_event': True,
}


Marshall_Plan = {
    'name': 'Marshall_Plan',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 23,
    'ops': 4,
    'owner': 'US',
    'event_text': 'Allows play of NATO. Add one US Influence in each of seven non-USSR Controlled Western European countries.',
    'remove_if_used_as_event': True,
}


Indo_Pakistani_War = {
    'name': 'Indo_Pakistani_War',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 24,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'India or Pakistan invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to the target of the invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track. Effects of Victory: Player gains 2 VP and replaces all opponent\'s Influence in target country with his Influence.',
}


Containment = {
    'name': 'Containment',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 25,
    'ops': 3,
    'owner': 'US',
    'event_text': 'All further Operations cards played by US this turn add one to their value (to a maximum of 4).',
    'remove_if_used_as_event': True,
}


CIA_Created = {
    'name': 'CIA_Created',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 26,
    'ops': 1,
    'owner': 'US',
    'event_text': 'USSR reveals hand this turn. Then the US may Conduct Operations as if they played a 1 Op card.',
    'remove_if_used_as_event': True,
}


US_Japan_Mutual_Defense_Pact = {
    'name': 'US_Japan_Mutual_Defense_Pact',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 27,
    'ops': 4,
    'owner': 'US',
    'event_text': 'US gains sufficient Influence in Japan for Control. USSR may no longer make Coup or Realignment rolls in Japan.',
    'remove_if_used_as_event': True,
}


Suez_Crisis = {
    'name': 'Suez_Crisis',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 28,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'Remove a total of 4 US Influence from France, the United Kingdom or Israel. Remove no more than 2 Influence per country.',
    'remove_if_used_as_event': True,
}


East_European_Unrest = {
    'name': 'East_European_Unrest',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 29,
    'ops': 3,
    'owner': 'US',
    'event_text': 'In Early or Mid War: Remove 1 USSR Influence from three countries in Eastern Europe. In Late War: Remove 2 USSR Influence from three countries in Eastern Europe.',
}


Decolonization = {
    'name': 'Decolonization',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 30,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'Add one USSR Influence in each of any four African and/or SE Asian countries.',
}


Red_Scare_Purge = {
    'name': 'Red_Scare_Purge',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 31,
    'ops': 4,
    'owner': 'NEUTRAL',
    'event_text': 'All further Operations cards played by your opponent this turn are -1 to their value (to a minimum of 1 Op).',
}


UN_Intervention = {
    'name': 'UN_Intervention',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 32,
    'ops': 1,
    'owner': 'NEUTRAL',
    'can_headline': False,
    'event_text': 'Play this card simultaneously with a card containing your opponent\'s associated Event. The Event is cancelled, but you may use its Operations value to Conduct Operations. The cancelled event returns to the discard pile. May not be played during headline phase.',
}


De_Stalinization = {
    'name': 'De_Stalinization',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 33,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'USSR may relocate up to 4 Influence points to non-US controlled countries. No more than 2 Influence may be placed in the same country.',
    'remove_if_used_as_event': True,
}


Nuclear_Test_Ban = {
    'name': 'Nuclear_Test_Ban',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 34,
    'ops': 4,
    'owner': 'NEUTRAL',
    'event_text': 'Player earns VPs equal to the current DEFCON level minus 2, then improve DEFCON two levels.',
}


Formosan_Resolution = {
    'name': 'Formosan_Resolution',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 35,
    'ops': 2,
    'owner': 'US',
    'event_text': 'Taiwan shall be treated as a Battleground country for scoring purposes, if the US controls Taiwan when the Asia Scoring Card is played or during Final Scoring at the end of Turn 10. Taiwan is not a battleground country for any other game purpose. This card is discarded after US play of \'The China Card\'.',
    'remove_if_used_as_event': True,
}


Defectors = {
    'name': 'Defectors',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 103,
    'ops': 2,
    'owner': 'US',
    'resolve_headline_first': True,
    'event_text': 'Play in Headline Phase to cancel USSR Headline event, including Scoring Card. Cancelled card returns to the Discard Pile. If Defectors played by USSR during Soviet action round, US gains 1 VP (unless played on the Space Race).',
}


# -- OPTIONAL
The_Cambridge_Five = {
    'name': 'The_Cambridge_Five',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 104,
    'optional_card': True,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'The US player exposes all scoring cards in their hand. The USSR player may then add 1 Influence in any single region named on one of those scoring cards (USSR choice). Cannot be played as an event in Late War.',
}


# -- OPTIONAL
Special_Relationship = {
    'name': 'Special_Relationship',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 105,
    'optional_card': True,
    'ops': 2,
    'owner': 'US',
    'event_text': 'If UK is US controlled but NATO is not in effect, US adds 1 Influence to any country adjacent to the UK. If UK is US controlled and NATO is in effect, US adds 2 Influence to any Western European country and gains 2 VPs.',
}


# -- OPTIONAL
NORAD = {
    'name': 'NORAD',
    'type': 'Event',
    'stage': 'Early War',
    'card_index': 106,
    'optional_card': True,
    'ops': 3,
    'owner': 'US',
    'event_text': 'If the US controls Canada, the US may add 1 Influence to any country already containing US Influence at the conclusion of any Action Round in which the DEFCON marker moves to the \'2\' box. This event cancelled by \'Quagmire\'.',
    'remove_if_used_as_event': True,
}


# --
# -- MID WAR
# --
#
#

Brush_War = {
    'name': 'Brush_War',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 36,
    'ops': 3,
    'owner': 'NEUTRAL',
    'event_text': 'Attack any country with a stability of 1 or 2. Roll a die and subtract 1 for every adjacent enemy controlled country. Success on 3-6. Player adds 3 to his Military Ops Track. Effects of Victory: Player gains 1 VP and replaces all opponent\'s Influence with his Influence.',
}


Central_America_Scoring = {
    'name': 'Central_America_Scoring',
    'type': 'Scoring',
    'stage': 'Mid War',
    'card_index': 37,
    'scoring_region': 'Central America',
    'event_text': 'Both sides score: Presence: 1, Domination: 3, Control: 5, +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower',
    'may_be_held': False,
}


Southeast_Asia_Scoring = {
    'name': 'Southeast_Asia_Scoring',
    'type': 'Scoring',
    'stage': 'Mid War',
    'card_index': 38,
    'may_be_held': False,
    'scoring_region': 'Southeast Asia',
    'event_text': 'Both sides score: 1 VP each for Control of: Burma, Cambodia/Laos, Vietnam, Malaysia, Indonesia, the Phillipines, 2 VP for Control of Thailand',
    'remove_if_used_as_event': True,
}


Arms_Race = {
    'name': 'Arms_Race',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 39,
    'ops': 3,
    'owner': 'NEUTRAL',
    'event_text': 'Compare each player\'s status on the Military Operations Track. If Phasing Player has more Military Operations points, he scores 1 VP. If Phasing Player has more Military Operations points and has met the Required Military Operations amount, he scores 3 VP instead.',
}


Cuban_Missile_Crisis = {
    'name': 'Cuban_Missile_Crisis',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 40,
    'ops': 3,
    'owner': 'NEUTRAL',
    'event_text': 'Set DEFCON to Level 2. Any further Coup attempt by your opponent this turn, anywhere on the board, will result in Global Thermonuclear War. Your opponent will lose the game. This event may be cancelled at any time if the USSR player removes two Influence from Cuba or the US player removes 2 Influence from either West Germany or Turkey.',
    'remove_if_used_as_event': True,
}


Nuclear_Subs = {
    'name': 'Nuclear_Subs',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 41,
    'ops': 2,
    'owner': 'US',
    'event_text': 'US Coup attempts in Battleground Countries do not affect the DEFCON track for the remainder of the turn (does not affect Cuban Missile Crisis).',
    'remove_if_used_as_event': True,
}


Quagmire = {
    'name': 'Quagmire',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 42,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'On next action round, US player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each US player Action round until successful or no appropriate cards remain. If out of appropriate cards, the US player may only play scoring cards until the next turn.',
    'remove_if_used_as_event': True,
}


Salt_Negotiations = {
    'name': 'Salt_Negotiations',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 43,
    'ops': 3,
    'owner': 'NEUTRAL',
    'event_text': 'Improve DEFCON two levels. Further Coup attempts incur -1 die roll modifier for both players for the remainder of the turn. Player may sort through discard pile and reclaim one non-scoring card, after revealing it to their opponent.',
    'remove_if_used_as_event': True,
}


Bear_Trap = {
    'name': 'Bear_Trap',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 44,
    'ops': 3,
    'owner': 'US',
    'event_text': 'On next action round, USSR player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each USSR player Action Round until successful or no appropriate cards remain. If out of appropriate cards, the USSR player may only play scoring cards until the next turn.',
    'remove_if_used_as_event': True,
}


Summit = {
    'name': 'Summit',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 45,
    'ops': 1,
    'owner': 'NEUTRAL',
    'event_text': 'Both players roll a die.  Each adds 1 for each Region they Dominate or Control. High roller gains 2 VP and may move DEFCON marker one level in either direction. o not reroll ties.',
}


How_I_Learned_to_Stop_Worrying = {
    'name': 'How_I_Learned_to_Stop_Worrying',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 46,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'Set the DEFCON at any level you want (1-5). This event counts as 5 Military Operations for the purpose of required Military Operations.',
    'remove_if_used_as_event': True,
}


Junta = {
    'name': 'Junta',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 47,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'Place 2 Influence in any one Central or South American country. Then you may make a free Coup attempt or Realignment roll in one of these regions (using this card\'s Operations Value).',
}


Kitchen_Debates = {
    'name': 'Kitchen_Debates',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 48,
    'ops': 1,
    'owner': 'US',
    'event_text': 'If the US controls more Battleground countries than the USSR, poke opponent in chest and gain 2 VP!',
    'remove_if_used_as_event': True,
}


Missile_Envy = {
    'name': 'Missile_Envy',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 49,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'Exchange this card for your opponent\'s highest valued Operations card in his hand. If two or more cards are tied, opponent chooses. If the exchanged card contains your event, or an event applicable to both players, it occurs immediately. If it contains opponent\'s event, use Operations value without triggering event. Opponent must use this card for Operations during his next action round.',
}


We_Will_Bury_You = {
    'name': 'We_Will_Bury_You',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 50,
    'ops': 4,
    'owner': 'USSR',
    'event_text': 'Unless UN Invervention is played as an Event on the US player\'s next round, USSR gains 3 VP prior to any US VP award. Degrade DEFCON one level.',
    'remove_if_used_as_event': True,
}


Brezhnev_Doctrine = {
    'name': 'Brezhnev_Doctrine',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 51,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'All further Operations cards played by the USSR this turn increase their Ops value by one (to a maximum of 4).',
    'remove_if_used_as_event': True,
}


Portuguese_Empire_Crumbles = {
    'name': 'Portuguese_Empire_Crumbles',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 52,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'Add 2 USSR Influence in both SE African States and Angola.',
    'remove_if_used_as_event': True,
}


South_African_Unrest = {
    'name': 'South_African_Unrest',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 53,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'USSR either adds 2 Influence in South Africa or adds 1 Influence in South Africa and 2 Influence in any countries adjacent to South Africa.',
}


Allende = {
    'name': 'Allende',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 54,
    'ops': 1,
    'owner': 'USSR',
    'event_text': 'USSR receives 2 Influence in Chile.',
    'remove_if_used_as_event': True,
}


Willy_Brandt = {
    'name': 'Willy_Brandt',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 55,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'USSR receives gains 1 VP. USSR receives 1 Influence in West Germany. Cancels NATO for West Germany. This event unplayable and/or cancelled by Tear Down This Wall.',
    'remove_if_used_as_event': True,
}


Muslim_Revolution = {
    'name': 'Muslim_Revolution',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 56,
    'ops': 4,
    'owner': 'USSR',
    'event_text': 'Remove all US Influence in two of the following countries: Sudan, Iran, Iraq, Egypt, Libya, Saudi Arabia, Syria, Jordan.',
}


ABM_Treaty = {
    'name': 'ABM_Treaty',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 57,
    'ops': 4,
    'owner': 'NEUTRAL',
    'event_text': 'Improve DEFCON one level. Then player may Conduct Operations as if they played a 4 Ops card.',
}


Cultural_Revolution = {
    'name': 'Cultural_Revolution',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 58,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'If the US has \'The China Card\', claim it face up and available for play. If the USSR already had it, USSR gains 1 VP.',
    'remove_if_used_as_event': True,
}


Flower_Power = {
    'name': 'Flower_Power',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 59,
    'ops': 4,
    'owner': 'USSR',
    'event_text': 'USSR gains 2 VP for every subsequently US played \'war card\' (played as an Event or Operations) unless played on the Space Race. War Cards: Arab-Israeli War, Korean War, Brush War, Indo-Pakistani War or Iran-Iraq War. This event cancelled by \'An Evil Empire\'.',
    'remove_if_used_as_event': True,
}


U2_Incident = {
    'name': 'U2_Incident',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 60,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'USSR gains 1 VP. If UN Intervention played later this turn as an Event, either by US or USSR, gain 1 additional VP.',
    'remove_if_used_as_event': True,
}


OPEC = {
    'name': 'OPEC',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 61,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'USSR gains 1VP for each of the following countries he controls: Egypt, Iran, Libya, Saudi Arabia, Iraq, Gulf States, and Venezuela. Unplayable as an event if \'North Sea Oil\' is in effect.',
}


Lone_Gunman = {
    'name': 'Lone_Gunman',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 62,
    'ops': 1,
    'owner': 'USSR',
    'event_text': 'US player reveals his hand. Then the USSR may Conduct Operations as if they played a 1 Op card.',
    'remove_if_used_as_event': True,
}


Colonial_Rear_Guards = {
    'name': 'Colonial_Rear_Guards',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 63,
    'ops': 2,
    'owner': 'US',
    'event_text': 'Add 1 US Influence in each of four different African and/or Southeast Asian countries.',
}


Panama_Canal_Returned = {
    'name': 'Panama_Canal_Returned',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 64,
    'ops': 1,
    'owner': 'US',
    'event_text': 'Add 1 US Influence in Panama, Costa Rica, and Venezuela.',
    'remove_if_used_as_event': True,
}


Camp_David_Accords = {
    'name': 'Camp_David_Accords',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 65,
    'ops': 2,
    'owner': 'US',
    'event_text': 'US gains 1 VP. US receives 1 Influence in Israel, Jordan and Egypt. Arab-Israeli War event no longer playable.',
    'remove_if_used_as_event': True,
}


Puppet_Governments = {
    'name': 'Puppet_Governments',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 66,
    'ops': 2,
    'owner': 'US',
    'event_text': 'US may add 1 Influence in three countries that currently contain no Influence from either power.',
    'remove_if_used_as_event': True,
}


Grain_Sales_to_Soviets = {
    'name': 'Grain_Sales_to_Soviets',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 67,
    'ops': 2,
    'owner': 'US',
    'event_text': 'Randomly choose one card from USSR hand. Play it or return it. If Soviet player has no cards, or returned, use this card to conduct Operations normally.',
}


John_Paul_II_Elected_Pope = {
    'name': 'John_Paul_II_Elected_Pope',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 68,
    'ops': 2,
    'owner': 'US',
    'event_text': 'Remove 2 USSR Influence in Poland and then add 1 US Influence in Poland. Allows play of \'Solidarity\'.',
    'remove_if_used_as_event': True,
}


Latin_American_Death_Squads = {
    'name': 'Latin_American_Death_Squads',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 69,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'All of the player\'s Coup attempts in Central and South America are +1 for the remainder of the turn, while all opponent\'s Coup attempts are -1 for the remainder of the turn.',
}


OAS_Founded = {
    'name': 'OAS_Founded',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 70,
    'ops': 1,
    'owner': 'US',
    'event_text': 'Add 2 US Influence in Central America and/or South America.',
    'remove_if_used_as_event': True,
}


Nixon_Plays_The_China_Card = {
    'name': 'Nixon_Plays_The_China_Card',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 71,
    'ops': 2,
    'owner': 'US',
    'event_text': 'If US has \'The China Card\', gain 2 VP. Otherwise, US player receives \'The China Card\' now, face down and unavailable for immediate play.',
    'remove_if_used_as_event': True,
}


Sadat_Expels_Soviets = {
    'name': 'Sadat_Expels_Soviets',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 72,
    'ops': 1,
    'owner': 'US',
    'event_text': 'Remove all USSR Influence in Egypt and add one US Influence.',
    'remove_if_used_as_event': True,
}


Shuttle_Diplomacy = {
    'name': 'Shuttle_Diplomacy',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 73,
    'ops': 3,
    'owner': 'US',
    'event_text': 'Play in front of US player. During the next scoring of the Middle East or Asia (whichever comes first), subtract one Battleground country from USSR total, then put this card in the discard pile. Does not count for Final Scoring at the end of Turn 10.',
}


The_Voice_Of_America = {
    'name': 'The_Voice_Of_America',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 74,
    'ops': 2,
    'owner': 'US',
    'event_text': 'Remove 4 USSR Influence from non-European countries. No more than 2 may be removed from any one country.',
}


Liberation_Theology = {
    'name': 'Liberation_Theology',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 75,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'Add 3 USSR Influence in Central America, no more than 2 per country.',
}


Ussuri_River_Skirmish = {
    'name': 'Ussuri_River_Skirmish',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 76,
    'ops': 3,
    'owner': 'US',
    'event_text': 'If the USSR has \'The China Card\', claim it face up and available for play. If the US already has \'The China Card\', add 4 US Influence in Asia, no more than 2 per country.',
    'remove_if_used_as_event': True,
}


Ask_Not_What_Your_Country_Can_Do_For_You = {
    'name': 'Ask_Not_What_Your_Country_Can_Do_For_You',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 77,
    'ops': 3,
    'owner': 'US',
    'event_text': 'US player may discard up to entire hand (including Scoring cards) and draw replacements from the deck. The number of cards discarded must be decided prior to drawing any replacements.',
    'remove_if_used_as_event': True,
}


Alliance_for_Progress = {
    'name': 'Alliance_for_Progress',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 78,
    'ops': 3,
    'owner': 'US',
    'event_text': 'US gains 1 VP for each US controlled Battleground country in Central America and South America.',
    'remove_if_used_as_event': True,
}


Africa_Scoring = {
    'name': 'Africa_Scoring',
    'type': 'Scoring',
    'stage': 'Mid War',
    'card_index': 79,
    'scoring_region': 'Africa',
    'event_text': 'Both sides score: Presence: 1, Domination: 4, Control: 6, +1 per controlled Battleground Country in Region',
    'may_be_held': False,
}


One_Small_Step = {
    'name': 'One_Small_Step',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 80,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'If you are behind on the Space Race Track, play this card to move your marker two boxes forward on the Space Rack Track, gaining the VP value of the second box only.',
}


South_America_Scoring = {
    'name': 'South_America_Scoring',
    'type': 'Scoring',
    'stage': 'Mid War',
    'card_index': 81,
    'scoring_region': 'South America',
    'event_text': 'Both sides score: Presence: 2, Domination: 5, Control: 6, +1 per controlled Battleground Country in Region',
    'may_be_held': False,
}


# -- OPTIONAL
Che = {
    'name': 'Che',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 107,
    'optional_card': True,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'USSR may immediately make a Coup attempt using this card\'s Operations value against a non-battleground country in Central America, South America, or Africa. If the Coup removes any US Influence, USSR may make a second Coup attempt against a different target under the same restrictions.',
}


# -- OPTIONAL
Our_Man_In_Tehran = {
    'name': 'Our_Man_In_Tehran',
    'type': 'Event',
    'stage': 'Mid War',
    'card_index': 108,
    'optional_card': True,
    'ops': 2,
    'owner': 'US',
    'event_text': 'If the US controls at least one Middle East country, the US player draws the top 5 cards from the draw pile. They may reveal and then discard any or all of these drawn cards without triggering the Event. Any remaining drawn cards are returned to the draw deck, and it is reshuffled.',
    'remove_if_used_as_event': True,
}


# --
# -- LATE WAR
# --


Iranian_Hostage_Crisis = {
    'name': 'Iranian_Hostage_Crisis',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 82,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'Remove all US Influence in Iran. Add 2 USSR Influence in Iran. Doubles the effect of Terrorism card against US.',
    'remove_if_used_as_event': True,
}


The_Iron_Lady = {
    'name': 'The_Iron_Lady',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 83,
    'ops': 3,
    'owner': 'US',
    'event_text': 'US gains 1 VP. Add 1 USSR Influence in Argentina. Remove all USSR Influence from UK. Socialist Governments event no longer playable.',
    'remove_if_used_as_event': True,
}


Reagan_Bombs_Libya = {
    'name': 'Reagan_Bombs_Libya',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 84,
    'ops': 2,
    'owner': 'US',
    'event_text': 'US gains 1 VP for every 2 USSR Influence in Libya.',
    'remove_if_used_as_event': True,
}


Star_Wars = {
    'name': 'Star_Wars',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 85,
    'ops': 2,
    'owner': 'US',
    'event_text': 'If the US is ahead on the Space Race Track, play this card to search through the discard pile for a non-scoring card of your choice. Event occurs immediately.',
    'remove_if_used_as_event': True,
}


North_Sea_Oil = {
    'name': 'North_Sea_Oil',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 86,
    'ops': 3,
    'owner': 'US',
    'event_text': 'OPEC event is no longer playable. US may play 8 cards this turn.',
    'remove_if_used_as_event': True,
}


The_Reformer = {
    'name': 'The_Reformer',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 87,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'Add 4 Influence in Europe (no more than 2 per country). If USSR is ahead of US in VP, then 6 Influence may be added instead. USSR may no longer conduct Coup attempts in Europe. Improves effect of Glasnost event.',
    'remove_if_used_as_event': True,
}


Marine_Barracks_Bombing = {
    'name': 'Marine_Barracks_Bombing',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 88,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'Remove all US Influence in Lebanon plus remove 2 additional US Influence from anywhere in the Middle East.',
    'remove_if_used_as_event': True,
}


Soviets_Shoot_Down_KAL = {
    'name': 'Soviets_Shoot_Down_KAL_007',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 89,
    'ops': 4,
    'owner': 'US',
    'event_text': 'Degrade DEFCON one level. US gains 2 VP. If South Korea is US Controlled, then the US may place Influence or attempt Realignment as if they played a 4 Ops card.',
    'remove_if_used_as_event': True,
}


Glasnost = {
    'name': 'Glasnost',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 90,
    'ops': 4,
    'owner': 'USSR',
    'event_text': 'USSR gains 2 VP. Improve DEFCON one level. If The Reformer is in effect, then the USSR may place Influence or attempt Realignments as if they played a 4 Ops card.',
    'remove_if_used_as_event': True,
}


Ortega_Elected_in_Nicaragua = {
    'name': 'Ortega_Elected_in_Nicaragua',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 91,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'Remove all US Influence from Nicaragua. Then USSR may make one free Coup attempt (with this card\'s Operations value) in a country adjacent to Nicaragua.',
    'remove_if_used_as_event': True,
}


Terrorism = {
    'name': 'Terrorism',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 92,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'Opponent must randomly discard one card. If played by USSR and Iranian Hostage Crisis is in effect, the US player must randomly discard two cards. (Events on discards do not occur.)',
}


Iran_Contra_Scandal = {
    'name': 'Iran_Contra_Scandal',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 93,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'All US Realignment rolls have a -1 die roll modifier for the remainder of the turn.',
    'remove_if_used_as_event': True,
}


Chernobyl = {
    'name': 'Chernobyl',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 94,
    'ops': 3,
    'owner': 'US',
    'event_text': 'The US player may designate one Region. For the remainder of the turn the USSR may not add additional Influence to that Region by the play of Operations Points via placing Influence.',
    'remove_if_used_as_event': True,
}


Latin_American_Debt_Crisis = {
    'name': 'Latin_American_Debt_Crisis',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 95,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'Unless the US Player immediately discards a \'3\' or greater Operations card, double USSR Influence in two countries in South America.',
    'remove_if_used_as_event': True,
}


Tear_Down_This_Wall = {
    'name': 'Tear_Down_This_Wall',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 96,
    'ops': 3,
    'owner': 'US',
    'event_text': 'Cancels/prevent Willy Brandt. Add 3 US Influence in East Germany. Then US may make a free Coup attempt or Realignment rolls in Europe using this card\'s Ops Value.',
    'remove_if_used_as_event': True,
}


An_Evil_Empire = {
    'name': 'An_Evil_Empire',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 97,
    'ops': 3,
    'owner': 'US',
    'event_text': 'Cancels/Prevents Flower Power. US gains 1 VP.',
    'remove_if_used_as_event': True,
}


Aldrich_Ames_Remix = {
    'name': 'Aldrich_Ames_Remix',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 98,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'US player exposes his hand to USSR player for remainder of turn. USSR then chooses one card from US hand, this card is discarded.',
    'remove_if_used_as_event': True,
}


Pershing_II_Deployed = {
    'name': 'Pershing_II_Deployed',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 99,
    'ops': 3,
    'owner': 'USSR',
    'event_text': 'USSR gains 1 VP. Remove 1 US Influence from up to three countries in Western Europe.',
    'remove_if_used_as_event': True,
}


Wargames = {
    'name': 'Wargames',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 100,
    'ops': 4,
    'owner': 'NEUTRAL',
    'event_text': 'If DEFCON Status 2, you may immediately end the game (without Final Scoring Phase) after giving opponent 6 VPs. How about a nice game of chess?',
    'remove_if_used_as_event': True,
}


Solidarity = {
    'name': 'Solidarity',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 101,
    'ops': 2,
    'owner': 'US',
    'event_text': 'Playable as an event only if John Paul II Elected Pope is in effect. Add 3 US Influence in Poland.',
    'remove_if_used_as_event': True,
}


Iran_Iraq_War = {
    'name': 'Iran_Iraq_War',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 102,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'Iran or Iraq invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to target of invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track Effects of Victory: Player gains 2 VP and replaces opponent\'s Influence in target country with his own.',
    'remove_if_used_as_event': True,
}


# -- OPTIONAL
Yuri_and_Samantha = {
    'name': 'Yuri_and_Samantha',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 109,
    'optional_card': True,
    'ops': 2,
    'owner': 'USSR',
    'event_text': 'USSR receives 1 VP for each US coup attempt made for the remainder of the current turn.',
    'remove_if_used_as_event': True,
}


# -- OPTIONAL
AWACS_Sale_to_Saudis = {
    'name': 'AWACS_Sale_to_Saudis',
    'type': 'Event',
    'stage': 'Late War',
    'card_index': 110,
    'optional_card': True,
    'ops': 3,
    'owner': 'US',
    'event_text': 'US receives 2 Influence in Saudi Arabia. Muslim Revolution may no longer be played as an event.',
    'remove_if_used_as_event': True,
}


Blank_1_Op_Card = {
    'name': 'Blank_1_Op_Card',
    'type': 'Template',
    'stage': 'Template',
    'card_index': 150,
    'optional_card': False,
    'ops': 1,
    'owner': 'NEUTRAL',
    'event_text': 'This is a blank card worth 1 operations points.',
    'remove_if_used_as_event': False,
}


Blank_2_Op_Card = {
    'name': 'Blank_2_Op_Card',
    'type': 'Template',
    'stage': 'Template',
    'card_index': 151,
    'optional_card': False,
    'ops': 2,
    'owner': 'NEUTRAL',
    'event_text': 'This is a blank card worth 2 operations points.',
    'remove_if_used_as_event': False,
}


Blank_3_Op_Card = {
    'name': 'Blank_3_Op_Card',
    'type': 'Template',
    'stage': 'Template',
    'card_index': 152,
    'optional_card': False,
    'ops': 3,
    'owner': 'NEUTRAL',
    'event_text': 'This is a blank card worth 3 operations points.',
    'remove_if_used_as_event': False,
}


Blank_4_Op_Card = {
    'name': 'Blank_4_Op_Card',
    'type': 'Template',
    'stage': 'Template',
    'card_index': 153,
    'optional_card': False,
    'ops': 4,
    'owner': 'NEUTRAL',
    'event_text': 'This is a blank card worth 4 operations points.',
    'remove_if_used_as_event': False,
}


Asia_Scoring = CardInfo(**Asia_Scoring)
Europe_Scoring = CardInfo(**Europe_Scoring)
Middle_East_Scoring = CardInfo(**Middle_East_Scoring)
Duck_and_Cover = CardInfo(**Duck_and_Cover)
Five_Year_Plan = CardInfo(**Five_Year_Plan)
The_China_Card = CardInfo(**The_China_Card)
Socialist_Governments = CardInfo(**Socialist_Governments)
Fidel = CardInfo(**Fidel)
Vietnam_Revolts = CardInfo(**Vietnam_Revolts)
Blockade = CardInfo(**Blockade)
Korean_War = CardInfo(**Korean_War)
Romanian_Abdication = CardInfo(**Romanian_Abdication)
Arab_Israeli_War = CardInfo(**Arab_Israeli_War)
COMECON = CardInfo(**COMECON)
Nasser = CardInfo(**Nasser)
Warsaw_Pact_Formed = CardInfo(**Warsaw_Pact_Formed)
De_Gaulle_Leads_France = CardInfo(**De_Gaulle_Leads_France)
Captured_Nazi_Scientist = CardInfo(**Captured_Nazi_Scientist)
Truman_Doctrine = CardInfo(**Truman_Doctrine)
Olympic_Games = CardInfo(**Olympic_Games)
NATO = CardInfo(**NATO)
Independent_Reds = CardInfo(**Independent_Reds)
Marshall_Plan = CardInfo(**Marshall_Plan)
Indo_Pakistani_War = CardInfo(**Indo_Pakistani_War)
Containment = CardInfo(**Containment)
CIA_Created = CardInfo(**CIA_Created)
US_Japan_Mutual_Defense_Pact = CardInfo(**US_Japan_Mutual_Defense_Pact)
Suez_Crisis = CardInfo(**Suez_Crisis)
East_European_Unrest = CardInfo(**East_European_Unrest)
Decolonization = CardInfo(**Decolonization)
Red_Scare_Purge = CardInfo(**Red_Scare_Purge)
UN_Intervention = CardInfo(**UN_Intervention)
De_Stalinization = CardInfo(**De_Stalinization)
Nuclear_Test_Ban = CardInfo(**Nuclear_Test_Ban)
Formosan_Resolution = CardInfo(**Formosan_Resolution)
Defectors = CardInfo(**Defectors)
The_Cambridge_Five = CardInfo(**The_Cambridge_Five)
Special_Relationship = CardInfo(**Special_Relationship)
NORAD = CardInfo(**NORAD)
Brush_War = CardInfo(**Brush_War)
Central_America_Scoring = CardInfo(**Central_America_Scoring)
Southeast_Asia_Scoring = CardInfo(**Southeast_Asia_Scoring)
Arms_Race = CardInfo(**Arms_Race)
Cuban_Missile_Crisis = CardInfo(**Cuban_Missile_Crisis)
Nuclear_Subs = CardInfo(**Nuclear_Subs)
Quagmire = CardInfo(**Quagmire)
Salt_Negotiations = CardInfo(**Salt_Negotiations)
Bear_Trap = CardInfo(**Bear_Trap)
Summit = CardInfo(**Summit)
How_I_Learned_to_Stop_Worrying = CardInfo(**How_I_Learned_to_Stop_Worrying)
Junta = CardInfo(**Junta)
Kitchen_Debates = CardInfo(**Kitchen_Debates)
Missile_Envy = CardInfo(**Missile_Envy)
We_Will_Bury_You = CardInfo(**We_Will_Bury_You)
Brezhnev_Doctrine = CardInfo(**Brezhnev_Doctrine)
Portuguese_Empire_Crumbles = CardInfo(**Portuguese_Empire_Crumbles)
South_African_Unrest = CardInfo(**South_African_Unrest)
Allende = CardInfo(**Allende)
Willy_Brandt = CardInfo(**Willy_Brandt)
Muslim_Revolution = CardInfo(**Muslim_Revolution)
ABM_Treaty = CardInfo(**ABM_Treaty)
Cultural_Revolution = CardInfo(**Cultural_Revolution)
Flower_Power = CardInfo(**Flower_Power)
U2_Incident = CardInfo(**U2_Incident)
OPEC = CardInfo(**OPEC)
Lone_Gunman = CardInfo(**Lone_Gunman)
Colonial_Rear_Guards = CardInfo(**Colonial_Rear_Guards)
Panama_Canal_Returned = CardInfo(**Panama_Canal_Returned)
Camp_David_Accords = CardInfo(**Camp_David_Accords)
Puppet_Governments = CardInfo(**Puppet_Governments)
Grain_Sales_to_Soviets = CardInfo(**Grain_Sales_to_Soviets)
John_Paul_II_Elected_Pope = CardInfo(**John_Paul_II_Elected_Pope)
Latin_American_Death_Squads = CardInfo(**Latin_American_Death_Squads)
OAS_Founded = CardInfo(**OAS_Founded)
Nixon_Plays_The_China_Card = CardInfo(**Nixon_Plays_The_China_Card)
Sadat_Expels_Soviets = CardInfo(**Sadat_Expels_Soviets)
Shuttle_Diplomacy = CardInfo(**Shuttle_Diplomacy)
The_Voice_Of_America = CardInfo(**The_Voice_Of_America)
Liberation_Theology = CardInfo(**Liberation_Theology)
Ussuri_River_Skirmish = CardInfo(**Ussuri_River_Skirmish)
Ask_Not_What_Your_Country_Can_Do_For_You = CardInfo(
    **Ask_Not_What_Your_Country_Can_Do_For_You)
Alliance_for_Progress = CardInfo(**Alliance_for_Progress)
Africa_Scoring = CardInfo(**Africa_Scoring)
One_Small_Step = CardInfo(**One_Small_Step)
South_America_Scoring = CardInfo(**South_America_Scoring)
Che = CardInfo(**Che)
Our_Man_In_Tehran = CardInfo(**Our_Man_In_Tehran)
Iranian_Hostage_Crisis = CardInfo(**Iranian_Hostage_Crisis)
The_Iron_Lady = CardInfo(**The_Iron_Lady)
Reagan_Bombs_Libya = CardInfo(**Reagan_Bombs_Libya)
Star_Wars = CardInfo(**Star_Wars)
North_Sea_Oil = CardInfo(**North_Sea_Oil)
The_Reformer = CardInfo(**The_Reformer)
Marine_Barracks_Bombing = CardInfo(**Marine_Barracks_Bombing)
Soviets_Shoot_Down_KAL = CardInfo(**Soviets_Shoot_Down_KAL)
Glasnost = CardInfo(**Glasnost)
Ortega_Elected_in_Nicaragua = CardInfo(**Ortega_Elected_in_Nicaragua)
Terrorism = CardInfo(**Terrorism)
Iran_Contra_Scandal = CardInfo(**Iran_Contra_Scandal)
Chernobyl = CardInfo(**Chernobyl)
Latin_American_Debt_Crisis = CardInfo(**Latin_American_Debt_Crisis)
Tear_Down_This_Wall = CardInfo(**Tear_Down_This_Wall)
An_Evil_Empire = CardInfo(**An_Evil_Empire)
Aldrich_Ames_Remix = CardInfo(**Aldrich_Ames_Remix)
Pershing_II_Deployed = CardInfo(**Pershing_II_Deployed)
Wargames = CardInfo(**Wargames)
Solidarity = CardInfo(**Solidarity)
Iran_Iraq_War = CardInfo(**Iran_Iraq_War)
Yuri_and_Samantha = CardInfo(**Yuri_and_Samantha)
AWACS_Sale_to_Saudis = CardInfo(**AWACS_Sale_to_Saudis)
Blank_1_Op_Card = CardInfo(**Blank_1_Op_Card)
Blank_2_Op_Card = CardInfo(**Blank_2_Op_Card)
Blank_3_Op_Card = CardInfo(**Blank_3_Op_Card)
Blank_4_Op_Card = CardInfo(**Blank_4_Op_Card)
