from twilight_map import *


class CardBase:
    def __init__(self):
        self.ops = 0
        self.may_be_held = True
        self.optional_card = False
        self.remove_if_used_as_event = False
        self.resolve_headline_first = False
        self.can_headline = True

class CardInstant(CardBase):
    def next_state():
        pass

class CardMultistep(CardBase):
    pass


class CardInfo:
    """
    Cards should be able to be used for:
    1. Event
    2. Realignment
    3. Coup
    4. Placing influence
    5. Space race
    6. Trigger event first >> realignment/coup/influence
    """

    ALL = dict()

    def __init__(self):
        CardInfo.ALL[self.name] = self
        self.ops = 0
        self.may_be_held = True
        self.optional_card = False
        self.remove_if_used_as_event = False
        self.resolve_headline_first = False
        self.can_headline = True

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
        pass

    def use_for_coup(self):
        pass

    def use_for_realignment(self):
        pass

    def possible_actions(self):
        pass


class GameCards:
    def __init__(self):
        self.ALL = dict()
        self.index_card_map = dict() # Create mapping of (k,v) = (card_index, name)
        self.early_war = []
        self.mid_war = []
        self.late_war = []

        for name in CardInfo.ALL.keys():
            self.ALL[name] = Card(name)
            if self.ALL[name].info.stage == 'Early War':
                self.early_war.append(self.ALL[name])
            if self.ALL[name].info.stage == 'Mid War':
                self.mid_war.append(self.ALL[name])
            if self.ALL[name].info.stage == 'Late War':
                self.late_war.append(self.ALL[name])
            self.index_card_map[self.ALL[name].info.card_index] = self.ALL[name].info.name

    def __getitem__(self, item):
        return self.ALL[item]


class Card(CardInfo):
    def __init__(self, name):
        self.info = CardInfo.ALL[name]
        self.can_play = True # flipped means unavailable for use

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


class Asia_Scoring(CardInfo):
    def __init__(self):
        self.name = 'Asia_Scoring'
        super().__init__()
        self.type = 'Scoring'
        self.stage = 'Early War'
        self.card_index = 1
        self.scoring_region = 'Asia',
        self.event_text = 'Both sides score: Presence: 3, Domination: 7, Control: 9. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
        self.may_be_held = False

    def event(self):
        ScoreAsia()

class Europe_Scoring(CardInfo):
    def __init__(self):
        self.name = 'Europe_Scoring'
        super().__init__()
        self.type = 'Scoring'
        self.stage = 'Early War'
        self.card_index = 2
        self.scoring_region = 'Europe',
        self.event_text = 'Both sides score: Presence: 3, Domination: 7, Control: VICTORY. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
        self.may_be_held = False,


class Middle_East_Scoring(CardInfo):
    def __init__(self):
        self.name = 'Middle_East_Scoring'
        super().__init__()
        self.type = 'Scoring'
        self.stage = 'Early War'
        self.card_index = 3
        self.scoring_region = 'Middle East',
        self.event_text = 'Both sides score: Presence: 3, Domination: 5, Control: 7. +1 per controlled Battleground Country in Region'
        self.may_be_held = False,


class Duck_and_Cover(CardInfo):
    def __init__(self):
        self.name = 'Duck_and_Cover'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 4
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'Degrade DEFCON one level. Then US player earns VPs equal to 5 minus current DEFCON level.'


class Five_Year_Plan(CardInfo):
    def __init__(self):
        self.name = 'Five_Year_Plan'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 5
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'USSR player must randomly discard one card. If the card is a US associated Event, the Event occurs immediately. If the card is a USSR associated Event or and Event applicable to both players, then the card must be discarded without triggering the Event.'


class The_China_Card(CardInfo):
    def __init__(self):
        self.name = 'The_China_Card'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 6
        self.ops = 4
        self.event_owner = 'NEUTRAL'
        self.can_headline = False
        self.event_text = 'Begins the game with the USSR player. +1 Operations value when all points are used in Asia. Pass to opponent after play. +1 VP for the player holding this card at the end of Turn 10. Cancels effect of \'Formosan Resolution\' if this card is played by the US player.'


class Socialist_Governments(CardInfo):
    def __init__(self):
        self.name = 'Socialist_Governments'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 7
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'Unplayable as an event if \'The Iron Lady\' is in effect. Remove US Influence in Western Europe by a total of 3 Influence points, removing no more than 2 per country.'


class Fidel(CardInfo):
    def __init__(self):
        self.name = 'Fidel'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 8
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'Remove all US Influence in Cuba. USSR gains sufficient Influence in Cuba for Control.'
        self.remove_if_used_as_event = True


class Vietnam_Revolts(CardInfo):
    def __init__(self):
        self.name = 'Vietnam_Revolts'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 9
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'Add 2 USSR Influence in Vietnam. For the remainder of the turn, the Soviet player may add 1 Operations point to any card that uses all points in Southeast Asia.'
        self.remove_if_used_as_event = True


class Blockade(CardInfo):
    def __init__(self):
        self.name = 'Blockade'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 10
        self.ops = 1
        self.event_owner = 'USSR'
        self.event_text = 'Unless US Player immediately discards a \'3\' or more value Operations card, eliminate all US Influence in West Germany.'
        self.remove_if_used_as_event = True


class Korean_War(CardInfo):
    def __init__(self):
        self.name = 'Korean_War'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 11
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'North Korea invades South Korea. Roll one die and subtract 1 for every US Controlled country adjacent to South Korea. USSR Victory on modified die roll 4-6. USSR add 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in South Korea with USSR Influence.'
        self.remove_if_used_as_event = True


class Romanian_Abdication(CardInfo):
    def __init__(self):
        self.name = 'Romanian_Abdication'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 12
        self.ops = 1
        self.event_owner = 'USSR'
        self.event_text = 'Remove all US Influence in Romania. USSR gains sufficient Influence in Romania for Control.'
        self.remove_if_used_as_event = True


class Arab_Israeli_War(CardInfo):
    def __init__(self):
        self.name = 'Arab_Israeli_War'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 13
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'A Pan-Arab Coalition invades Israel. Roll one die and subtract 1 for US Control of Israel and for US-controlled country adjacent to Israel. USSR Victory on modified die roll 4-6. USSR adds 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in Israel with USSR Influence.'


class COMECON(CardInfo):
    def __init__(self):
        self.name = 'COMECON'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 14
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'Add 1 USSR Influence in each of four non-US Controlled countries in Eastern Europe.'
        self.remove_if_used_as_event = True


class Nasser(CardInfo):
    def __init__(self):
        self.name = 'Nasser'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 15
        self.ops = 1
        self.event_owner = 'USSR'
        self.event_text = 'Add 2 USSR Influence in Egypt. Remove half (rounded up) of the US Influence in Egypt.'
        self.remove_if_used_as_event = True


class Warsaw_Pact_Formed(CardInfo):
    def __init__(self):
        self.name = 'Warsaw_Pact_Formed'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 16
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'Remove all US Influence from four countries in Eastern Europe, or add 5 USSR Influence in Eastern Europe, adding no more than 2 per country. Allow play of NATO.'
        self.remove_if_used_as_event = True


class De_Gaulle_Leads_France(CardInfo):
    def __init__(self):
        self.name = 'De_Gaulle_Leads_France'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 17
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'Remove 2 US Influence in France, add 1 USSR Influence. Cancels effects of NATO for France.'
        self.remove_if_used_as_event = True


class Captured_Nazi_Scientist(CardInfo):
    def __init__(self):
        self.name = 'Captured_Nazi_Scientist'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 18
        self.ops = 1
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Advance player\'s Space Race marker one box.'
        self.remove_if_used_as_event = True


class Truman_Doctrine(CardInfo):
    def __init__(self):
        self.name = 'Truman_Doctrine'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 19
        self.ops = 1
        self.event_owner = 'US'
        self.event_text = 'Remove all USSR Influence markers in one uncontrolled country in Europe.'
        self.remove_if_used_as_event = True


class Olympic_Games(CardInfo):
    def __init__(self):
        self.name = 'Olympic_Games'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 20
        self.ops = 2
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Player sponsors Olympics. Opponent may participate or boycott. If Opponent participates, each player rolls one die, with the sponsor adding 2 to his roll. High roll gains 2 VP. Reroll ties If Opponent boycotts, degrade DEFCON one level and the Sponsor may Conduct Operations as if they played a 4 Ops card.'


class NATO(CardInfo):
    def __init__(self):
        self.name = 'NATO'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 21
        self.ops = 4
        self.event_owner = 'US'
        self.event_text = 'Play after \'Marshall Plan\' or \'Warsaw Pact\'. USSR player may no longer make Coup or Realignment rolls in any US Controlled countries in Europe. US Controlled countries in Europe may not be attacked by play of the Brush War event.'
        self.remove_if_used_as_event = True


class Independent_Reds(CardInfo):
    def __init__(self):
        self.name = 'Independent_Reds'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 22
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'Adds sufficient US Influence in either Yugoslavia, Romania, Bulgaria, Hungary, or Czechoslavakia to equal USSR Influence.'
        self.remove_if_used_as_event = True


class Marshall_Plan(CardInfo):
    def __init__(self):
        self.name = 'Marshall_Plan'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 23
        self.ops = 4
        self.event_owner = 'US'
        self.event_text = 'Allows play of NATO. Add one US Influence in each of seven non-USSR Controlled Western European countries.'
        self.remove_if_used_as_event = True


class Indo_Pakistani_War(CardInfo):
    def __init__(self):
        self.name = 'Indo_Pakistani_War'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 24
        self.ops = 2
        self.event_owner = 'NEUTRAL'
        self.event_text = 'India or Pakistan invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to the target of the invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track. Effects of Victory: Player gains 2 VP and replaces all opponent\'s Influence in target country with his Influence.'


class Containment(CardInfo):
    def __init__(self):
        self.name = 'Containment'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 25
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'All further Operations cards played by US this turn add one to their value (to a maximum of 4).'
        self.remove_if_used_as_event = True


class CIA_Created(CardInfo):
    def __init__(self):
        self.name = 'CIA_Created'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 26
        self.ops = 1
        self.event_owner = 'US'
        self.event_text = 'USSR reveals hand this turn. Then the US may Conduct Operations as if they played a 1 Op card.'
        self.remove_if_used_as_event = True


class US_Japan_Mutual_Defense_Pact(CardInfo):
    def __init__(self):
        self.name = 'US_Japan_Mutual_Defense_Pact'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 27
        self.ops = 4
        self.event_owner = 'US'
        self.event_text = 'US gains sufficient Influence in Japan for Control. USSR may no longer make Coup or Realignment rolls in Japan.'
        self.remove_if_used_as_event = True


class Suez_Crisis(CardInfo):
    def __init__(self):
        self.name = 'Suez_Crisis'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 28
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'Remove a total of 4 US Influence from France, the United Kingdom or Israel. Remove no more than 2 Influence per country.'
        self.remove_if_used_as_event = True


class East_European_Unrest(CardInfo):
    def __init__(self):
        self.name = 'East_European_Unrest'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 29
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'In Early or Mid War: Remove 1 USSR Influence from three countries in Eastern Europe. In Late War: Remove 2 USSR Influence from three countries in Eastern Europe.'


class Decolonization(CardInfo):
    def __init__(self):
        self.name = 'Decolonization'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 30
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'Add one USSR Influence in each of any four African and/or SE Asian countries.'


class Red_Scare_Purge(CardInfo):
    def __init__(self):
        self.name = 'Red_Scare_Purge'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 31
        self.ops = 4
        self.event_owner = 'NEUTRAL'
        self.event_text = 'All further Operations cards played by your opponent this turn are -1 to their value (to a minimum of 1 Op).'


class UN_Intervention(CardInfo):
    def __init__(self):
        self.name = 'UN_Intervention'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 32
        self.ops = 1
        self.event_owner = 'NEUTRAL'
        self.can_headline = False,
        self.event_text = 'Play this card simultaneously with a card containing your opponent\'s associated Event. The Event is cancelled, but you may use its Operations value to Conduct Operations. The cancelled event returns to the discard pile. May not be played during headline phase.'


class De_Stalinization(CardInfo):
    def __init__(self):
        self.name = 'De_Stalinization'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 33
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'USSR may relocate up to 4 Influence points to non-US controlled countries. No more than 2 Influence may be placed in the same country.'
        self.remove_if_used_as_event = True


class Nuclear_Test_Ban(CardInfo):
    def __init__(self):
        self.name = 'Nuclear_Test_Ban'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 34
        self.ops = 4
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Player earns VPs equal to the current DEFCON level minus 2, then improve DEFCON two levels.'


class Formosan_Resolution(CardInfo):
    def __init__(self):
        self.name = 'Formosan_Resolution'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 35
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'Taiwan shall be treated as a Battleground country for scoring purposes, if the US controls Taiwan when the Asia Scoring Card is played or during Final Scoring at the end of Turn 10. Taiwan is not a battleground country for any other game purpose. This card is discarded after US play of \'The China Card\'.'
        self.remove_if_used_as_event = True


class Defectors(CardInfo):
    def __init__(self):
        self.name = 'Defectors'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 103
        self.ops = 2
        self.event_owner = 'US'
        self.resolve_headline_first = True,
        self.event_text = 'Play in Headline Phase to cancel USSR Headline event, including Scoring Card. Cancelled card returns to the Discard Pile. If Defectors played by USSR during Soviet action round, US gains 1 VP (unless played on the Space Race).'


# -- OPTIONAL
class The_Cambridge_Five(CardInfo):
    def __init__(self):
        self.name = 'The_Cambridge_Five'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 104
        self.optional_card = True,
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'The US player exposes all scoring cards in their hand. The USSR player may then add 1 Influence in any single region self.named on one of those scoring cards (USSR choice). Cannot be played as an event in Late War.'


# -- OPTIONAL
class Special_Relationship(CardInfo):
    def __init__(self):
        self.name = 'Special_Relationship'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 105
        self.optional_card = True,
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'If UK is US controlled but NATO is not in effect, US adds 1 Influence to any country adjacent to the UK. If UK is US controlled and NATO is in effect, US adds 2 Influence to any Western European country and gains 2 VPs.'


# -- OPTIONAL
class NORAD(CardInfo):
    def __init__(self):
        self.name = 'NORAD'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Early War'
        self.card_index = 106
        self.optional_card = True,
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'If the US controls Canada, the US may add 1 Influence to any country already containing US Influence at the conclusion of any Action Round in which the DEFCON marker moves to the \'2\' box. This event cancelled by \'Quagmire\'.'
        self.remove_if_used_as_event = True


# --
# -- MID WAR
# --
#
#

class Brush_War(CardInfo):
    def __init__(self):
        self.name = 'Brush_War'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 36
        self.ops = 3
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Attack any country with a stability of 1 or 2. Roll a die and subtract 1 for every adjacent enemy controlled country. Success on 3-6. Player adds 3 to his Military Ops Track. Effects of Victory: Player gains 1 VP and replaces all opponent\'s Influence with his Influence.'


class Central_America_Scoring(CardInfo):
    def __init__(self):
        self.name = 'Central_America_Scoring'
        super().__init__()
        self.type = 'Scoring'
        self.stage = 'Mid War'
        self.card_index = 37
        self.scoring_region = 'Central America',
        self.event_text = 'Both sides score: Presence: 1, Domination: 3, Control: 5, +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
        self.may_be_held = False,


class Southeast_Asia_Scoring(CardInfo):
    def __init__(self):
        self.name = 'Southeast_Asia_Scoring'
        super().__init__()
        self.type = 'Scoring'
        self.stage = 'Mid War'
        self.card_index = 38
        self.may_be_held = False,
        self.scoring_region = 'Southeast Asia',
        self.event_text = 'Both sides score: 1 VP each for Control of: Burma, Cambodia/Laos, Vietnam, Malaysia, Indonesia, the Phillipines, 2 VP for Control of Thailand'
        self.remove_if_used_as_event = True


class Arms_Race(CardInfo):
    def __init__(self):
        self.name = 'Arms_Race'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 39
        self.ops = 3
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Compare each player\'s status on the Military Operations Track. If Phasing Player has more Military Operations points, he scores 1 VP. If Phasing Player has more Military Operations points and has met the Required Military Operations amount, he scores 3 VP instead.'


class Cuban_Missile_Crisis(CardInfo):
    def __init__(self):
        self.name = 'Cuban_Missile_Crisis'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 40
        self.ops = 3
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Set DEFCON to Level 2. Any further Coup attempt by your opponent this turn, anywhere on the board, will result in Global Thermonuclear War. Your opponent will lose the game. This event may be cancelled at any time if the USSR player removes two Influence from Cuba or the US player removes 2 Influence from either West Germany or Turkey.'
        self.remove_if_used_as_event = True


class Nuclear_Subs(CardInfo):
    def __init__(self):
        self.name = 'Nuclear_Subs'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 41
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'US Coup attempts in Battleground Countries do not affect the DEFCON track for the remainder of the turn (does not affect Cuban Missile Crisis).'
        self.remove_if_used_as_event = True


class Quagmire(CardInfo):
    def __init__(self):
        self.name = 'Quagmire'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 42
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'On next action round, US player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each US player Action round until successful or no appropriate cards remain. If out of appropriate cards, the US player may only play scoring cards until the next turn.'
        self.remove_if_used_as_event = True


class Salt_Negotiations(CardInfo):
    def __init__(self):
        self.name = 'Salt_Negotiations'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 43
        self.ops = 3
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Improve DEFCON two levels. Further Coup attempts incur -1 die roll modifier for both players for the remainder of the turn. Player may sort through discard pile and reclaim one non-scoring card, after revealing it to their opponent.'
        self.remove_if_used_as_event = True


class Bear_Trap(CardInfo):
    def __init__(self):
        self.name = 'Bear_Trap'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 44
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'On next action round, USSR player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each USSR player Action Round until successful or no appropriate cards remain. If out of appropriate cards, the USSR player may only play scoring cards until the next turn.'
        self.remove_if_used_as_event = True


class Summit(CardInfo):
    def __init__(self):
        self.name = 'Summit'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 45
        self.ops = 1
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Both players roll a die.  Each adds 1 for each Region they Dominate or Control. High roller gains 2 VP and may move DEFCON marker one level in either direction. o not reroll ties.'


class How_I_Learned_to_Stop_Worrying(CardInfo):
    def __init__(self):
        self.name = 'How_I_Learned_to_Stop_Worrying'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 46
        self.ops = 2
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Set the DEFCON at any level you want (1-5). This event counts as 5 Military Operations for the purpose of required Military Operations.'
        self.remove_if_used_as_event = True


class Junta(CardInfo):
    def __init__(self):
        self.name = 'Junta'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 47
        self.ops = 2
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Place 2 Influence in any one Central or South American country. Then you may make a free Coup attempt or Realignment roll in one of these regions (using this card\'s Operations Value).'


class Kitchen_Debates(CardInfo):
    def __init__(self):
        self.name = 'Kitchen_Debates'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 48
        self.ops = 1
        self.event_owner = 'US'
        self.event_text = 'If the US controls more Battleground countries than the USSR, poke opponent in chest and gain 2 VP!'
        self.remove_if_used_as_event = True


class Missile_Envy(CardInfo):
    def __init__(self):
        self.name = 'Missile_Envy'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 49
        self.ops = 2
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Exchange this card for your opponent\'s highest valued Operations card in his hand. If two or more cards are tied, opponent chooses. If the exchanged card contains your event, or an event applicable to both players, it occurs immediately. If it contains opponent\'s event, use Operations value without triggering event. Opponent must use this card for Operations during his next action round.'


class We_Will_Bury_You(CardInfo):
    def __init__(self):
        self.name = 'We_Will_Bury_You'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 50
        self.ops = 4
        self.event_owner = 'USSR'
        self.event_text = 'Unless UN Invervention is played as an Event on the US player\'s next round, USSR gains 3 VP prior to any US VP award. Degrade DEFCON one level.'
        self.remove_if_used_as_event = True


class Brezhnev_Doctrine(CardInfo):
    def __init__(self):
        self.name = 'Brezhnev_Doctrine'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 51
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'All further Operations cards played by the USSR this turn increase their Ops value by one (to a maximum of 4).'
        self.remove_if_used_as_event = True


class Portuguese_Empire_Crumbles(CardInfo):
    def __init__(self):
        self.name = 'Portuguese_Empire_Crumbles'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 52
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'Add 2 USSR Influence in both SE African States and Angola.'
        self.remove_if_used_as_event = True


class South_African_Unrest(CardInfo):
    def __init__(self):
        self.name = 'South_African_Unrest'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 53
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'USSR either adds 2 Influence in South Africa or adds 1 Influence in South Africa and 2 Influence in any countries adjacent to South Africa.'


class Allende(CardInfo):
    def __init__(self):
        self.name = 'Allende'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 54
        self.ops = 1
        self.event_owner = 'USSR'
        self.event_text = 'USSR receives 2 Influence in Chile.'
        self.remove_if_used_as_event = True


class Willy_Brandt(CardInfo):
    def __init__(self):
        self.name = 'Willy_Brandt'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 55
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'USSR receives gains 1 VP. USSR receives 1 Influence in West Germany. Cancels NATO for West Germany. This event unplayable and/or cancelled by Tear Down This Wall.'
        self.remove_if_used_as_event = True


class Muslim_Revolution(CardInfo):
    def __init__(self):
        self.name = 'Muslim_Revolution'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 56
        self.ops = 4
        self.event_owner = 'USSR'
        self.event_text = 'Remove all US Influence in two of the following countries: Sudan, Iran, Iraq, Egypt, Libya, Saudi Arabia, Syria, Jordan.'


class ABM_Treaty(CardInfo):
    def __init__(self):
        self.name = 'ABM_Treaty'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 57
        self.ops = 4
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Improve DEFCON one level. Then player may Conduct Operations as if they played a 4 Ops card.'


class Cultural_Revolution(CardInfo):
    def __init__(self):
        self.name = 'Cultural_Revolution'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 58
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'If the US has \'The China Card\', claim it face up and available for play. If the USSR already had it, USSR gains 1 VP.'
        self.remove_if_used_as_event = True


class Flower_Power(CardInfo):
    def __init__(self):
        self.name = 'Flower_Power'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 59
        self.ops = 4
        self.event_owner = 'USSR'
        self.event_text = 'USSR gains 2 VP for every subsequently US played \'war card\' (played as an Event or Operations) unless played on the Space Race. War Cards: Arab-Israeli War, Korean War, Brush War, Indo-Pakistani War or Iran-Iraq War. This event cancelled by \'An Evil Empire\'.'
        self.remove_if_used_as_event = True


class U2_Incident(CardInfo):
    def __init__(self):
        self.name = 'U2_Incident'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 60
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'USSR gains 1 VP. If UN Intervention played later this turn as an Event, either by US or USSR, gain 1 additional VP.'
        self.remove_if_used_as_event = True


class OPEC(CardInfo):
    def __init__(self):
        self.name = 'OPEC'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 61
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'USSR gains 1VP for each of the following countries he controls: Egypt, Iran, Libya, Saudi Arabia, Iraq, Gulf States, and Venezuela. Unplayable as an event if \'North Sea Oil\' is in effect.'


class Lone_Gunman(CardInfo):
    def __init__(self):
        self.name = 'Lone_Gunman'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 62
        self.ops = 1
        self.event_owner = 'USSR'
        self.event_text = 'US player reveals his hand. Then the USSR may Conduct Operations as if they played a 1 Op card.'
        self.remove_if_used_as_event = True


class Colonial_Rear_Guards(CardInfo):
    def __init__(self):
        self.name = 'Colonial_Rear_Guards'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 63
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'Add 1 US Influence in each of four different African and/or Southeast Asian countries.'


class Panama_Canal_Returned(CardInfo):
    def __init__(self):
        self.name = 'Panama_Canal_Returned'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 64
        self.ops = 1
        self.event_owner = 'US'
        self.event_text = 'Add 1 US Influence in Panama, Costa Rica, and Venezuela.'
        self.remove_if_used_as_event = True


class Camp_David_Accords(CardInfo):
    def __init__(self):
        self.name = 'Camp_David_Accords'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 65
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'US gains 1 VP. US receives 1 Influence in Israel, Jordan and Egypt. Arab-Israeli War event no longer playable.'
        self.remove_if_used_as_event = True


class Puppet_Governments(CardInfo):
    def __init__(self):
        self.name = 'Puppet_Governments'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 66
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'US may add 1 Influence in three countries that currently contain no Influence from either power.'
        self.remove_if_used_as_event = True


class Grain_Sales_to_Soviets(CardInfo):
    def __init__(self):
        self.name = 'Grain_Sales_to_Soviets'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 67
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'Randomly choose one card from USSR hand. Play it or return it. If Soviet player has no cards, or returned, use this card to conduct Operations normally.'


class John_Paul_II_Elected_Pope(CardInfo):
    def __init__(self):
        self.name = 'John_Paul_II_Elected_Pope'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 68
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'Remove 2 USSR Influence in Poland and then add 1 US Influence in Poland. Allows play of \'Solidarity\'.'
        self.remove_if_used_as_event = True


class Latin_American_Death_Squads(CardInfo):
    def __init__(self):
        self.name = 'Latin_American_Death_Squads'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 69
        self.ops = 2
        self.event_owner = 'NEUTRAL'
        self.event_text = 'All of the player\'s Coup attempts in Central and South America are +1 for the remainder of the turn, while all opponent\'s Coup attempts are -1 for the remainder of the turn.'


class OAS_Founded(CardInfo):
    def __init__(self):
        self.name = 'OAS_Founded'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 70
        self.ops = 1
        self.event_owner = 'US'
        self.event_text = 'Add 2 US Influence in Central America and/or South America.'
        self.remove_if_used_as_event = True


class Nixon_Plays_The_China_Card(CardInfo):
    def __init__(self):
        self.name = 'Nixon_Plays_The_China_Card'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 71
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'If US has \'The China Card\', gain 2 VP. Otherwise, US player receives \'The China Card\' now, face down and unavailable for immediate play.'
        self.remove_if_used_as_event = True


class Sadat_Expels_Soviets(CardInfo):
    def __init__(self):
        self.name = 'Sadat_Expels_Soviets'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 72
        self.ops = 1
        self.event_owner = 'US'
        self.event_text = 'Remove all USSR Influence in Egypt and add one US Influence.'
        self.remove_if_used_as_event = True


class Shuttle_Diplomacy(CardInfo):
    def __init__(self):
        self.name = 'Shuttle_Diplomacy'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 73
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'Play in front of US player. During the next scoring of the Middle East or Asia (whichever comes first), subtract one Battleground country from USSR total, then put this card in the discard pile. Does not count for Final Scoring at the end of Turn 10.'


class The_Voice_Of_America(CardInfo):
    def __init__(self):
        self.name = 'The_Voice_Of_America'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 74
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'Remove 4 USSR Influence from non-European countries. No more than 2 may be removed from any one country.'


class Liberation_Theology(CardInfo):
    def __init__(self):
        self.name = 'Liberation_Theology'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 75
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'Add 3 USSR Influence in Central America, no more than 2 per country.'


class Ussuri_River_Skirmish(CardInfo):
    def __init__(self):
        self.name = 'Ussuri_River_Skirmish'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 76
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'If the USSR has \'The China Card\', claim it face up and available for play. If the US already has \'The China Card\', add 4 US Influence in Asia, no more than 2 per country.'
        self.remove_if_used_as_event = True


class Ask_Not_What_Your_Country_Can_Do_For_You(CardInfo):
    def __init__(self):
        self.name = 'Ask_Not_What_Your_Country_Can_Do_For_You'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 77
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'US player may discard up to entire hand (including Scoring cards) and draw replacements from the deck. The number of cards discarded must be decided prior to drawing any replacements.'
        self.remove_if_used_as_event = True



class Alliance_for_Progress(CardInfo):
    def __init__(self):
        self.name = 'Alliance_for_Progress'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 78
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'US gains 1 VP for each US controlled Battleground country in Central America and South America.'
        self.remove_if_used_as_event = True



class Africa_Scoring(CardInfo):
    def __init__(self):
        self.name = 'Africa_Scoring'
        super().__init__()
        self.type = 'Scoring'
        self.stage = 'Mid War'
        self.card_index = 79
        self.scoring_region = 'Africa',
        self.event_text = 'Both sides score: Presence: 1, Domination: 4, Control: 6, +1 per controlled Battleground Country in Region'
        self.may_be_held = False,



class One_Small_Step(CardInfo):
    def __init__(self):
        self.name = 'One_Small_Step'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 80
        self.ops = 2
        self.event_owner = 'NEUTRAL'
        self.event_text = 'If you are behind on the Space Race Track, play this card to move your marker two boxes forward on the Space Rack Track, gaining the VP value of the second box only.'



class South_America_Scoring(CardInfo):
    def __init__(self):
        self.name = 'South_America_Scoring'
        super().__init__()
        self.type = 'Scoring'
        self.stage = 'Mid War'
        self.card_index = 81
        self.scoring_region = 'South America',
        self.event_text = 'Both sides score: Presence: 2, Domination: 5, Control: 6, +1 per controlled Battleground Country in Region'
        self.may_be_held = False,



# -- OPTIONAL
class Che(CardInfo):
    def __init__(self):
        self.name = 'Che'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 107
        self.optional_card = True,
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'USSR may immediately make a Coup attempt using this card\'s Operations value against a non-battleground country in Central America, South America, or Africa. If the Coup removes any US Influence, USSR may make a second Coup attempt against a different target under the same restrictions.'



# -- OPTIONAL
class Our_Man_In_Tehran(CardInfo):
    def __init__(self):
        self.name = 'Our_Man_In_Tehran'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Mid War'
        self.card_index = 108
        self.optional_card = True,
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'If the US controls at least one Middle East country, the US player draws the top 5 cards from the draw pile. They may reveal and then discard any or all of these drawn cards without triggering the Event. Any remaining drawn cards are returned to the draw deck, and it is reshuffled.'
        self.remove_if_used_as_event = True





# --
# -- LATE WAR
# --


class Iranian_Hostage_Crisis(CardInfo):
    def __init__(self):
        self.name = 'Iranian_Hostage_Crisis'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 82
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'Remove all US Influence in Iran. Add 2 USSR Influence in Iran. Doubles the effect of Terrorism card against US.'
        self.remove_if_used_as_event = True



class The_Iron_Lady(CardInfo):
    def __init__(self):
        self.name = 'The_Iron_Lady'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 83
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'US gains 1 VP. Add 1 USSR Influence in Argentina. Remove all USSR Influence from UK. Socialist Governments event no longer playable.'
        self.remove_if_used_as_event = True



class Reagan_Bombs_Libya(CardInfo):
    def __init__(self):
        self.name = 'Reagan_Bombs_Libya'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 84
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'US gains 1 VP for every 2 USSR Influence in Libya.'
        self.remove_if_used_as_event = True



class Star_Wars(CardInfo):
    def __init__(self):
        self.name = 'Star_Wars'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 85
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'If the US is ahead on the Space Race Track, play this card to search through the discard pile for a non-scoring card of your choice. Event occurs immediately.'
        self.remove_if_used_as_event = True



class North_Sea_Oil(CardInfo):
    def __init__(self):
        self.name = 'North_Sea_Oil'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 86
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'OPEC event is no longer playable. US may play 8 cards this turn.'
        self.remove_if_used_as_event = True



class The_Reformer(CardInfo):
    def __init__(self):
        self.name = 'The_Reformer'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 87
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'Add 4 Influence in Europe (no more than 2 per country). If USSR is ahead of US in VP, then 6 Influence may be added instead. USSR may no longer conduct Coup attempts in Europe. Improves effect of Glasnost event.'
        self.remove_if_used_as_event = True



class Marine_Barracks_Bombing(CardInfo):
    def __init__(self):
        self.name = 'Marine_Barracks_Bombing'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 88
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'Remove all US Influence in Lebanon plus remove 2 additional US Influence from anywhere in the Middle East.'
        self.remove_if_used_as_event = True



class Soviets_Shoot_Down_KAL(CardInfo):
    def __init__(self):
        self.name = 'Soviets_Shoot_Down_KAL_007'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 89
        self.ops = 4
        self.event_owner = 'US'
        self.event_text = 'Degrade DEFCON one level. US gains 2 VP. If South Korea is US Controlled, then the US may place Influence or attempt Realignment as if they played a 4 Ops card.'
        self.remove_if_used_as_event = True


class Glasnost(CardInfo):
    def __init__(self):
        self.name = 'Glasnost'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 90
        self.ops = 4
        self.event_owner = 'USSR'
        self.event_text = 'USSR gains 2 VP. Improve DEFCON one level. If The Reformer is in effect, then the USSR may place Influence or attempt Realignments as if they played a 4 Ops card.'
        self.remove_if_used_as_event = True


class Ortega_Elected_in_Nicaragua(CardInfo):
    def __init__(self):
        self.name = 'Ortega_Elected_in_Nicaragua'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 91
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'Remove all US Influence from Nicaragua. Then USSR may make one free Coup attempt (with this card\'s Operations value) in a country adjacent to Nicaragua.'
        self.remove_if_used_as_event = True


class Terrorism(CardInfo):
    def __init__(self):
        self.name = 'Terrorism'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 92
        self.ops = 2
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Opponent must randomly discard one card. If played by USSR and Iranian Hoself.stage Crisis is in effect, the US player must randomly discard two cards. (Events on discards do not occur.)'


class Iran_Contra_Scandal(CardInfo):
    def __init__(self):
        self.name = 'Iran_Contra_Scandal'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 93
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'All US Realignment rolls have a -1 die roll modifier for the remainder of the turn.'
        self.remove_if_used_as_event = True



class Chernobyl(CardInfo):
    def __init__(self):
        self.name = 'Chernobyl'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 94
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'The US player may designate one Region. For the remainder of the turn the USSR may not add additional Influence to that Region by the play of Operations Points via placing Influence.'
        self.remove_if_used_as_event = True


class Latin_American_Debt_Crisis(CardInfo):
    def __init__(self):
        self.name = 'Latin_American_Debt_Crisis'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 95
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'Unless the US Player immediately discards a \'3\' or greater Operations card, double USSR Influence in two countries in South America.'
        self.remove_if_used_as_event = True



class Tear_Down_This_Wall(CardInfo):
    def __init__(self):
        self.name = 'Tear_Down_This_Wall'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 96
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'Cancels/prevent Willy Brandt. Add 3 US Influence in East Germany. Then US may make a free Coup attempt or Realignment rolls in Europe using this card\'s Ops Value.'
        self.remove_if_used_as_event = True



class An_Evil_Empire(CardInfo):
    def __init__(self):
        self.name = 'An_Evil_Empire'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 97
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'Cancels/Prevents Flower Power. US gains 1 VP.'
        self.remove_if_used_as_event = True



class Aldrich_Ames_Remix(CardInfo):
    def __init__(self):
        self.name = 'Aldrich_Ames_Remix'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 98
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'US player exposes his hand to USSR player for remainder of turn. USSR then chooses one card from US hand, this card is discarded.'
        self.remove_if_used_as_event = True


class Pershing_II_Deployed(CardInfo):
    def __init__(self):
        self.name = 'Pershing_II_Deployed'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 99
        self.ops = 3
        self.event_owner = 'USSR'
        self.event_text = 'USSR gains 1 VP. Remove 1 US Influence from up to three countries in Western Europe.'
        self.remove_if_used_as_event = True



class Wargames(CardInfo):
    def __init__(self):
        self.name = 'Wargames'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 100
        self.ops = 4
        self.event_owner = 'NEUTRAL'
        self.event_text = 'If DEFCON Status 2, you may immediately end the game (without Final Scoring Phase) after giving opponent 6 VPs. How about a nice game of chess?'
        self.remove_if_used_as_event = True



class Solidarity(CardInfo):
    def __init__(self):
        self.name = 'Solidarity'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 101
        self.ops = 2
        self.event_owner = 'US'
        self.event_text = 'Playable as an event only if John Paul II Elected Pope is in effect. Add 3 US Influence in Poland.'
        self.remove_if_used_as_event = True



class Iran_Iraq_War(CardInfo):
    def __init__(self):
        self.name = 'Iran_Iraq_War'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 102
        self.ops = 2
        self.event_owner = 'NEUTRAL'
        self.event_text = 'Iran or Iraq invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to target of invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track Effects of Victory: Player gains 2 VP and replaces opponent\'s Influence in target country with his own.'
        self.remove_if_used_as_event = True



# -- OPTIONAL
class Yuri_and_Samantha(CardInfo):
    def __init__(self):
        self.name = 'Yuri_and_Samantha'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 109
        self.optional_card = True,
        self.ops = 2
        self.event_owner = 'USSR'
        self.event_text = 'USSR receives 1 VP for each US coup attempt made for the remainder of the current turn.'
        self.remove_if_used_as_event = True



# -- OPTIONAL
class AWACS_Sale_to_Saudis(CardInfo):
    def __init__(self):
        self.name = 'AWACS_Sale_to_Saudis'
        super().__init__()
        self.type = 'Event'
        self.stage = 'Late War'
        self.card_index = 110
        self.optional_card = True,
        self.ops = 3
        self.event_owner = 'US'
        self.event_text = 'US receives 2 Influence in Saudi Arabia. Muslim Revolution may no longer be played as an event.'
        self.remove_if_used_as_event = True

Asia_Scoring = Asia_Scoring()
Europe_Scoring = Europe_Scoring()
Middle_East_Scoring = Middle_East_Scoring()
Duck_and_Cover = Duck_and_Cover()
Five_Year_Plan = Five_Year_Plan()
The_China_Card = The_China_Card()
Socialist_Governments = Socialist_Governments()
Fidel = Fidel()
Vietnam_Revolts = Vietnam_Revolts()
Blockade = Blockade()
Korean_War = Korean_War()
Romanian_Abdication = Romanian_Abdication()
Arab_Israeli_War = Arab_Israeli_War()
COMECON = COMECON()
Nasser = Nasser()
Warsaw_Pact_Formed = Warsaw_Pact_Formed()
De_Gaulle_Leads_France = De_Gaulle_Leads_France()
Captured_Nazi_Scientist = Captured_Nazi_Scientist()
Truman_Doctrine = Truman_Doctrine()
Olympic_Games = Olympic_Games()
NATO = NATO()
Independent_Reds = Independent_Reds()
Marshall_Plan = Marshall_Plan()
Indo_Pakistani_War = Indo_Pakistani_War()
Containment = Containment()
CIA_Created = CIA_Created()
US_Japan_Mutual_Defense_Pact = US_Japan_Mutual_Defense_Pact()
Suez_Crisis = Suez_Crisis()
East_European_Unrest = East_European_Unrest()
Decolonization = Decolonization()
Red_Scare_Purge = Red_Scare_Purge()
UN_Intervention = UN_Intervention()
De_Stalinization = De_Stalinization()
Nuclear_Test_Ban = Nuclear_Test_Ban()
Formosan_Resolution = Formosan_Resolution()
Defectors = Defectors()
The_Cambridge_Five = The_Cambridge_Five()
Special_Relationship = Special_Relationship()
NORAD = NORAD()
Brush_War = Brush_War()
Central_America_Scoring = Central_America_Scoring()
Southeast_Asia_Scoring = Southeast_Asia_Scoring()
Arms_Race = Arms_Race()
Cuban_Missile_Crisis = Cuban_Missile_Crisis()
Nuclear_Subs = Nuclear_Subs()
Quagmire = Quagmire()
Salt_Negotiations = Salt_Negotiations()
Bear_Trap = Bear_Trap()
Summit = Summit()
How_I_Learned_to_Stop_Worrying = How_I_Learned_to_Stop_Worrying()
Junta = Junta()
Kitchen_Debates = Kitchen_Debates()
Missile_Envy = Missile_Envy()
We_Will_Bury_You = We_Will_Bury_You()
Brezhnev_Doctrine = Brezhnev_Doctrine()
Portuguese_Empire_Crumbles = Portuguese_Empire_Crumbles()
South_African_Unrest = South_African_Unrest()
Allende = Allende()
Willy_Brandt = Willy_Brandt()
Muslim_Revolution = Muslim_Revolution()
ABM_Treaty = ABM_Treaty()
Cultural_Revolution = Cultural_Revolution()
Flower_Power = Flower_Power()
U2_Incident = U2_Incident()
OPEC = OPEC()
Lone_Gunman = Lone_Gunman()
Colonial_Rear_Guards = Colonial_Rear_Guards()
Panama_Canal_Returned = Panama_Canal_Returned()
Camp_David_Accords = Camp_David_Accords()
Puppet_Governments = Puppet_Governments()
Grain_Sales_to_Soviets = Grain_Sales_to_Soviets()
John_Paul_II_Elected_Pope = John_Paul_II_Elected_Pope()
Latin_American_Death_Squads = Latin_American_Death_Squads()
OAS_Founded = OAS_Founded()
Nixon_Plays_The_China_Card = Nixon_Plays_The_China_Card()
Sadat_Expels_Soviets = Sadat_Expels_Soviets()
Shuttle_Diplomacy = Shuttle_Diplomacy()
The_Voice_Of_America = The_Voice_Of_America()
Liberation_Theology = Liberation_Theology()
Ussuri_River_Skirmish = Ussuri_River_Skirmish()
Ask_Not_What_Your_Country_Can_Do_For_You = Ask_Not_What_Your_Country_Can_Do_For_You()
Alliance_for_Progress = Alliance_for_Progress()
Africa_Scoring = Africa_Scoring()
One_Small_Step = One_Small_Step()
South_America_Scoring = South_America_Scoring()
Che = Che()
Our_Man_In_Tehran = Our_Man_In_Tehran()
Iranian_Hostage_Crisis = Iranian_Hostage_Crisis()
The_Iron_Lady = The_Iron_Lady()
Reagan_Bombs_Libya = Reagan_Bombs_Libya()
Star_Wars = Star_Wars()
North_Sea_Oil = North_Sea_Oil()
The_Reformer = The_Reformer()
Marine_Barracks_Bombing = Marine_Barracks_Bombing()
Soviets_Shoot_Down_KAL = Soviets_Shoot_Down_KAL()
Glasnost = Glasnost()
Ortega_Elected_in_Nicaragua = Ortega_Elected_in_Nicaragua()
Terrorism = Terrorism()
Iran_Contra_Scandal = Iran_Contra_Scandal()
Chernobyl = Chernobyl()
Latin_American_Debt_Crisis = Latin_American_Debt_Crisis()
Tear_Down_This_Wall = Tear_Down_This_Wall()
An_Evil_Empire = An_Evil_Empire()
Aldrich_Ames_Remix = Aldrich_Ames_Remix()
Pershing_II_Deployed = Pershing_II_Deployed()
Wargames = Wargames()
Solidarity = Solidarity()
Iran_Iraq_War = Iran_Iraq_War()
Yuri_and_Samantha = Yuri_and_Samantha()
AWACS_Sale_to_Saudis = AWACS_Sale_to_Saudis()
