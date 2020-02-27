from abc import ABC, abstractmethod
from twilight_map import MapRegion, CountryInfo
from twilight_enums import Side, MapRegion, InputType, CardAction


class GameCards:

    def __init__(self):

        self.ALL = dict()
        self.early_war = []
        self.mid_war = []
        self.late_war = []

        for name in Card.ALL.keys():
            if Card.ALL[name].stage == 'Early War':
                self.early_war.append(name)
            if Card.ALL[name].stage == 'Mid War':
                self.mid_war.append(name)
            if Card.ALL[name].stage == 'Late War':
                self.late_war.append(name)

    def __getitem__(self, item):
        return Card.ALL[item]


class Card:

    ALL = dict()
    INDEX = dict()

    @abstractmethod
    def __init__(self):
        self.card_index = 0
        self.name = ''
        self.card_type = ''
        self.stage = ''
        self.ops = 0
        self.event_text = ''
        self.owner = Side.NEUTRAL
        self.optional = False

        self.event_unique = False
        self.scoring_region = ''
        self.may_be_held = True
        self.resolve_headline_first = False
        self.can_headline = True
        self.is_playable = True

    @property
    def info(self):
        return self

    def _add_to_card(self):
        Card.ALL[self.name] = self
        Card.INDEX[self.card_index] = self

    def __repr__(self):
        if self.card_type == 'Scoring':
            return self.name
        else:
            return f'{self.name} - {self.ops}'

    def __eq__(self, other: str):
        return self.name == other

    def can_event(self, game_instance, side: Side):
        return True if self.owner != side.opp else False

    def dispose(self, game, side):
        pass

    def available_actions(self, game, side):
        pass

    def use_event(self, game, side):
        pass

    def use_space(self, side):
        pass

    def use_coup(self, game, side):
        pass

    def use_influence(self, game, side):
        pass

    def use_realignment(self, game, side):
        pass


# --
# -- EARLY WAR
# --


class Asia_Scoring(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Asia_Scoring'
        self.card_index = 1
        self._add_to_card()
        self.card_type = 'Scoring'
        self.stage = 'Early War'
        self.scoring_region = 'Asia'
        self.event_text = 'Both sides score: Presence: 3, Domination: 7, Control: 9. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
        self.may_be_held = False


class Europe_Scoring(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Europe_Scoring'
        self.card_index = 2
        self._add_to_card()
        self.card_type = 'Scoring'
        self.stage = 'Early War'
        self.scoring_region = 'Europe'
        self.event_text = 'Both sides score: Presence: 3, Domination: 7, Control: VICTORY. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
        self.may_be_held = False


class Middle_East_Scoring(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Middle_East_Scoring'
        self.card_index = 3
        self._add_to_card()
        self.card_type = 'Scoring'
        self.stage = 'Early War'
        self.scoring_region = 'Middle East'
        self.event_text = 'Both sides score: Presence: 3, Domination: 5, Control: 7. +1 per controlled Battleground Country in Region'
        self.may_be_held = False


class Duck_and_Cover(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Duck_and_Cover'
        self.card_index = 4
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'Degrade DEFCON one level. Then US player earns VPs equal to 5 minus current DEFCON level.'


class Five_Year_Plan(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Five_Year_Plan'
        self.card_index = 5
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'USSR player must randomly discard one card. If the card is a US associated Event, the Event occurs immediately. If the card is a USSR associated Event or and Event applicable to both players, then the card must be discarded without triggering the Event.'


class The_China_Card(Card):
    def __init__(self):
        super().__init__()
        self.name = 'The_China_Card'
        self.card_index = 6
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 4
        self.owner = Side.NEUTRAL
        self.can_headline = False
        self.event_text = 'Begins the game with the USSR player. +1 Operations value when all points are used in Asia. Pass to opponent after play. +1 VP for the player holding this card at the end of Turn 10. Cancels effect of \'Formosan Resolution\' if this card is played by the US player.'

    def can_event(self, game_instance, side):
        return False


class Socialist_Governments(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Socialist_Governments'
        self.card_index = 7
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'Unplayable as an event if \'The Iron Lady\' is in effect. Remove US Influence in Western Europe by a total of 3 Influence points, removing no more than 2 per country.'

    def can_event(self, game_instance, side):
        return False if 'The_Iron_Lady' in game_instance.basket[Side.US] else True


class Fidel(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Fidel'
        self.card_index = 8
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'Remove all US Influence in Cuba. USSR gains sufficient Influence in Cuba for Control.'
        self.event_unique = True


class Vietnam_Revolts(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Vietnam_Revolts'
        self.card_index = 9
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'Add 2 USSR Influence in Vietnam. For the remainder of the turn, the Soviet player may add 1 Operations point to any card that uses all points in Southeast Asia.'
        self.event_unique = True


class Blockade(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Blockade'
        self.card_index = 10
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 1
        self.owner = Side.USSR
        self.event_text = 'Unless US Player immediately discards a \'3\' or more value Operations card, eliminate all US Influence in West Germany.'
        self.event_unique = True


class Korean_War(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Korean_War'
        self.card_index = 11
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'North Korea invades South Korea. Roll one die and subtract 1 for every US Controlled country adjacent to South Korea. USSR Victory on modified die roll 4-6. USSR add 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in South Korea with USSR Influence.'
        self.event_unique = True


class Romanian_Abdication(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Romanian_Abdication'
        self.card_index = 12
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 1
        self.owner = Side.USSR
        self.event_text = 'Remove all US Influence in Romania. USSR gains sufficient Influence in Romania for Control.'
        self.event_unique = True


class Arab_Israeli_War(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Arab_Israeli_War'
        self.card_index = 13
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'A Pan-Arab Coalition invades Israel. Roll one die and subtract 1 for US Control of Israel and for US-controlled country adjacent to Israel. USSR Victory on modified die roll 4-6. USSR adds 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in Israel with USSR Influence.'

    def can_event(self, game_instance, side):
        return False if 'Camp_David_Accords' in game_instance.basket[Side.US] else True


class COMECON(Card):
    def __init__(self):
        super().__init__()
        self.name = 'COMECON'
        self.card_index = 14
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'Add 1 USSR Influence in each of four non-US Controlled countries in Eastern Europe.'
        self.event_unique = True


class Nasser(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Nasser'
        self.card_index = 15
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 1
        self.owner = Side.USSR
        self.event_text = 'Add 2 USSR Influence in Egypt. Remove half (rounded up) of the US Influence in Egypt.'
        self.event_unique = True


class Warsaw_Pact_Formed(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Warsaw_Pact_Formed'
        self.card_index = 16
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'Remove all US Influence from four countries in Eastern Europe, or add 5 USSR Influence in Eastern Europe, adding no more than 2 per country. Allow play of NATO.'
        self.event_unique = True


class De_Gaulle_Leads_France(Card):
    def __init__(self):
        super().__init__()
        self.name = 'De_Gaulle_Leads_France'
        self.card_index = 17
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'Remove 2 US Influence in France, add 1 USSR Influence. Cancels effects of NATO for France.'
        self.event_unique = True


class Captured_Nazi_Scientist(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Captured_Nazi_Scientist'
        self.card_index = 18
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 1
        self.owner = Side.NEUTRAL
        self.event_text = 'Advance player\'s Space Race marker one box.'
        self.event_unique = True


class Truman_Doctrine(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Truman_Doctrine'
        self.card_index = 19
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 1
        self.owner = Side.US
        self.event_text = 'Remove all USSR Influence markers in one uncontrolled country in Europe.'
        self.event_unique = True


class Olympic_Games(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Olympic_Games'
        self.card_index = 20
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'Player sponsors Olympics. Opponent may participate or boycott. If Opponent participates, each player rolls one die, with the sponsor adding 2 to his roll. High roll gains 2 VP. Reroll ties If Opponent boycotts, degrade DEFCON one level and the Sponsor may Conduct Operations as if they played a 4 Ops card.'


class NATO(Card):
    def __init__(self):
        super().__init__()
        self.name = 'NATO'
        self.card_index = 21
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 4
        self.owner = Side.US
        self.event_text = 'Play after \'Marshall Plan\' or \'Warsaw Pact\'. USSR player may no longer make Coup or Realignment rolls in any US Controlled countries in Europe. US Controlled countries in Europe may not be attacked by play of the Brush War event.'
        self.event_unique = True

    def can_event(self, game_instance, side):
        return True if 'Warsaw_Pact_Formed' in game_instance.basket[
            Side.US] or 'Marshall_Plan' in game_instance.basket[Side.US] else False


class Independent_Reds(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Independent_Reds'
        self.card_index = 22
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'Adds sufficient US Influence in either Yugoslavia, Romania, Bulgaria, Hungary, or Czechoslavakia to equal USSR Influence.'
        self.event_unique = True


class Marshall_Plan(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Marshall_Plan'
        self.card_index = 23
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 4
        self.owner = Side.US
        self.event_text = 'Allows play of NATO. Add one US Influence in each of seven non-USSR Controlled Western European countries.'
        self.event_unique = True


class Indo_Pakistani_War(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Indo_Pakistani_War'
        self.card_index = 24
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'India or Pakistan invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to the target of the invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track. Effects of Victory: Player gains 2 VP and replaces all opponent\'s Influence in target country with his Influence.'


class Containment(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Containment'
        self.card_index = 25
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'All further Operations cards played by US this turn add one to their value (to a maximum of 4).'
        self.event_unique = True


class CIA_Created(Card):
    def __init__(self):
        super().__init__()
        self.name = 'CIA_Created'
        self.card_index = 26
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 1
        self.owner = Side.US
        self.event_text = 'USSR reveals hand this turn. Then the US may Conduct Operations as if they played a 1 Op card.'
        self.event_unique = True


class US_Japan_Mutual_Defense_Pact(Card):
    def __init__(self):
        super().__init__()
        self.name = 'US_Japan_Mutual_Defense_Pact'
        self.card_index = 27
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 4
        self.owner = Side.US
        self.event_text = 'US gains sufficient Influence in Japan for Control. USSR may no longer make Coup or Realignment rolls in Japan.'
        self.event_unique = True


class Suez_Crisis(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Suez_Crisis'
        self.card_index = 28
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'Remove a total of 4 US Influence from France, the United Kingdom or Israel. Remove no more than 2 Influence per country.'
        self.event_unique = True


class East_European_Unrest(Card):
    def __init__(self):
        super().__init__()
        self.name = 'East_European_Unrest'
        self.card_index = 29
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'In Early or Mid War: Remove 1 USSR Influence from three countries in Eastern Europe. In Late War: Remove 2 USSR Influence from three countries in Eastern Europe.'


class Decolonization(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Decolonization'
        self.card_index = 30
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'Add one USSR Influence in each of any four African and/or SE Asian countries.'


class Red_Scare_Purge(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Red_Scare_Purge'
        self.card_index = 31
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 4
        self.owner = Side.NEUTRAL
        self.event_text = 'All further Operations cards played by your opponent this turn are -1 to their value (to a minimum of 1 Op).'


class UN_Intervention(Card):
    def __init__(self):
        super().__init__()
        self.name = 'UN_Intervention'
        self.card_index = 32
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 1
        self.owner = Side.NEUTRAL
        self.can_headline = False
        self.event_text = 'Play this card simultaneously with a card containing your opponent\'s associated Event. The Event is cancelled, but you may use its Operations value to Conduct Operations. The cancelled event returns to the discard pile. May not be played during headline phase.'

    def can_event(self, game_instance, side):
        return any((game_instance.cards[c].info.owner == side.opp for c in game_instance.hand[side]))


class De_Stalinization(Card):
    def __init__(self):
        super().__init__()
        self.name = 'De_Stalinization'
        self.card_index = 33
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'USSR may relocate up to 4 Influence points to non-US controlled countries. No more than 2 Influence may be placed in the same country.'
        self.event_unique = True


class Nuclear_Test_Ban(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Nuclear_Test_Ban'
        self.card_index = 34
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 4
        self.owner = Side.NEUTRAL
        self.event_text = 'Player earns VPs equal to the current DEFCON level minus 2, then improve DEFCON two levels.'


class Formosan_Resolution(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Formosan_Resolution'
        self.card_index = 35
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'Taiwan shall be treated as a Battleground country for scoring purposes, if the US controls Taiwan when the Asia Scoring Card is played or during Final Scoring at the end of Turn 10. Taiwan is not a battleground country for any other game purpose. This card is discarded after US play of \'The China Card\'.'
        self.event_unique = True


class Defectors(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Defectors'
        self.card_index = 103
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.ops = 2
        self.owner = Side.US
        self.resolve_headline_first = True
        self.event_text = 'Play in Headline Phase to cancel USSR Headline event, including Scoring Card. Cancelled card returns to the Discard Pile. If Defectors played by USSR during Soviet action round, US gains 1 VP (unless played on the Space Race).'

    def can_event(self, game_instance, side):
        return False

# -- OPTIONAL


class The_Cambridge_Five(Card):
    def __init__(self):
        super().__init__()
        self.name = 'The_Cambridge_Five'
        self.card_index = 104
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.optional = True
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'The US player exposes all scoring cards in their hand. The USSR player may then add 1 Influence in any single region named on one of those scoring cards (USSR choice). Cannot be played as an event in Late War.'

    def can_event(self, game_instance, side):
        return False if game_instance.turn_track >= 8 else True


# -- OPTIONAL
class Special_Relationship(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Special_Relationship'
        self.card_index = 105
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.optional = True
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'If UK is US controlled but NATO is not in effect, US adds 1 Influence to any country adjacent to the UK. If UK is US controlled and NATO is in effect, US adds 2 Influence to any Western European country and gains 2 VPs.'

    def can_event(self, game_instance, side):
        return True if game_instance.map['UK'].control == Side.US else False


# -- OPTIONAL
class NORAD(Card):
    def __init__(self):
        super().__init__()
        self.name = 'NORAD'
        self.card_index = 106
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Early War'
        self.optional = True
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'If the US controls Canada, the US may add 1 Influence to any country already containing US Influence at the conclusion of any Action Round in which the DEFCON marker moves to the \'2\' box. This event cancelled by \'Quagmire\'.'
        self.event_unique = True


# --
# -- MID WAR
# --
#
#

class Brush_War(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Brush_War'
        self.card_index = 36
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.NEUTRAL
        self.event_text = 'Attack any country with a stability of 1 or 2. Roll a die and subtract 1 for every adjacent enemy controlled country. Success on 3-6. Player adds 3 to his Military Ops Track. Effects of Victory: Player gains 1 VP and replaces all opponent\'s Influence with his Influence.'


class Central_America_Scoring(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Central_America_Scoring'
        self.card_index = 37
        self._add_to_card()
        self.card_type = 'Scoring'
        self.stage = 'Mid War'
        self.scoring_region = 'Central America'
        self.event_text = 'Both sides score: Presence: 1, Domination: 3, Control: 5. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
        self.may_be_held = False


class Southeast_Asia_Scoring(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Southeast_Asia_Scoring'
        self.card_index = 38
        self._add_to_card()
        self.card_type = 'Scoring'
        self.stage = 'Mid War'
        self.may_be_held = False
        self.scoring_region = 'Southeast Asia'
        self.event_text = 'Both sides score: 1 VP each for Control of: Burma, Cambodia/Laos, Vietnam, Malaysia, Indonesia, the Phillipines, 2 VP for Control of Thailand'
        self.event_unique = True


class Arms_Race(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Arms_Race'
        self.card_index = 39
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.NEUTRAL
        self.event_text = 'Compare each player\'s status on the Military Operations Track. If Phasing Player has more Military Operations points, he scores 1 VP. If Phasing Player has more Military Operations points and has met the Required Military Operations amount, he scores 3 VP instead.'


class Cuban_Missile_Crisis(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Cuban_Missile_Crisis'
        self.card_index = 40
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.NEUTRAL
        self.event_text = 'Set DEFCON to Level 2. Any further Coup attempt by your opponent this turn, anywhere on the board, will result in Global Thermonuclear War. Your opponent will lose the game. This event may be cancelled at any time if the USSR player removes two Influence from Cuba or the US player removes 2 Influence from either West Germany or Turkey.'
        self.event_unique = True


class Nuclear_Subs(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Nuclear_Subs'
        self.card_index = 41
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'US Coup attempts in Battleground Countries do not affect the DEFCON track for the remainder of the turn (does not affect Cuban Missile Crisis).'
        self.event_unique = True


class Quagmire(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Quagmire'
        self.card_index = 42
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'On next action round, US player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each US player Action round until successful or no appropriate cards remain. If out of appropriate cards, the US player may only play scoring cards until the next turn.'
        self.event_unique = True


class Salt_Negotiations(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Salt_Negotiations'
        self.card_index = 43
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.NEUTRAL
        self.event_text = 'Improve DEFCON two levels. Further Coup attempts incur -1 die roll modifier for both players for the remainder of the turn. Player may sort through discard pile and reclaim one non-scoring card, after revealing it to their opponent.'
        self.event_unique = True


class Bear_Trap(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Bear_Trap'
        self.card_index = 44
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'On next action round, USSR player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each USSR player Action Round until successful or no appropriate cards remain. If out of appropriate cards, the USSR player may only play scoring cards until the next turn.'
        self.event_unique = True


class Summit(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Summit'
        self.card_index = 45
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 1
        self.owner = Side.NEUTRAL
        self.event_text = 'Both players roll a die.  Each adds 1 for each Region they Dominate or Control. High roller gains 2 VP and may move DEFCON marker one level in either direction. Do not reroll ties.'


class How_I_Learned_to_Stop_Worrying(Card):
    def __init__(self):
        super().__init__()
        self.name = 'How_I_Learned_to_Stop_Worrying'
        self.card_index = 46
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'Set the DEFCON at any level you want (1-5). This event counts as 5 Military Operations for the purpose of required Military Operations.'
        self.event_unique = True


class Junta(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Junta'
        self.card_index = 47
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'Place 2 Influence in any one Central or South American country. Then you may make a free Coup attempt or Realignment roll in one of these regions (using this card\'s Operations Value).'


class Kitchen_Debates(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Kitchen_Debates'
        self.card_index = 48
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 1
        self.owner = Side.US
        self.event_text = 'If the US controls more Battleground countries than the USSR, poke opponent in chest and gain 2 VP!'
        self.event_unique = True

    def can_event(self, game_instance, side):
        us_count = sum(1 for n in CountryInfo.ALL if game_instance.map[n].control ==
                       Side.US and game_instance.map[n].info.battleground)
        ussr_count = sum(1 for n in CountryInfo.ALL if game_instance.map[n].control ==
                         Side.USSR and game_instance.map[n].info.battleground)
        return us_count > ussr_count


class Missile_Envy(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Missile_Envy'
        self.card_index = 49
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'Exchange this card for your opponent\'s highest valued Operations card in his hand. If two or more cards are tied, opponent chooses. If the exchanged card contains your event, or an event applicable to both players, it occurs immediately. If it contains opponent\'s event, use Operations value without triggering event. Opponent must use this card for Operations during his next action round.'


class We_Will_Bury_You(Card):
    def __init__(self):
        super().__init__()
        self.name = 'We_Will_Bury_You'
        self.card_index = 50
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 4
        self.owner = Side.USSR
        self.event_text = 'Unless UN Invervention is played as an Event on the US player\'s next round, USSR gains 3 VP prior to any US VP award. Degrade DEFCON one level.'
        self.event_unique = True


class Brezhnev_Doctrine(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Brezhnev_Doctrine'
        self.card_index = 51
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'All further Operations cards played by the USSR this turn increase their Ops value by one (to a maximum of 4).'
        self.event_unique = True


class Portuguese_Empire_Crumbles(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Portuguese_Empire_Crumbles'
        self.card_index = 52
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'Add 2 USSR Influence in both SE African States and Angola.'
        self.event_unique = True


class South_African_Unrest(Card):
    def __init__(self):
        super().__init__()
        self.name = 'South_African_Unrest'
        self.card_index = 53
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'USSR either adds 2 Influence in South Africa or adds 1 Influence in South Africa and 2 Influence in any countries adjacent to South Africa.'


class Allende(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Allende'
        self.card_index = 54
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 1
        self.owner = Side.USSR
        self.event_text = 'USSR receives 2 Influence in Chile.'
        self.event_unique = True


class Willy_Brandt(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Willy_Brandt'
        self.card_index = 55
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'USSR receives gains 1 VP. USSR receives 1 Influence in West Germany. Cancels NATO for West Germany. This event unplayable and/or cancelled by Tear Down This Wall.'
        self.event_unique = True

    def can_event(self, game_instance, side):
        return False if 'Tear_Down_This_Wall' in game_instance.basket[Side.US] else True


class Muslim_Revolution(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Muslim_Revolution'
        self.card_index = 56
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 4
        self.owner = Side.USSR
        self.event_text = 'Remove all US Influence in two of the following countries: Sudan, Iran, Iraq, Egypt, Libya, Saudi Arabia, Syria, Jordan.'

    def can_event(self, game_instance, side):
        return False if 'AWACS_Sale_to_Saudis' in game_instance.basket[Side.US] else True


class ABM_Treaty(Card):
    def __init__(self):
        super().__init__()
        self.name = 'ABM_Treaty'
        self.card_index = 57
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 4
        self.owner = Side.NEUTRAL
        self.event_text = 'Improve DEFCON one level. Then player may Conduct Operations as if they played a 4 Ops card.'


class Cultural_Revolution(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Cultural_Revolution'
        self.card_index = 58
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'If the US has \'The China Card\', claim it face up and available for play. If the USSR already had it, USSR gains 1 VP.'
        self.event_unique = True


class Flower_Power(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Flower_Power'
        self.card_index = 59
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 4
        self.owner = Side.USSR
        self.event_text = 'USSR gains 2 VP for every subsequently US played \'war card\' (played as an Event or Operations) unless played on the Space Race. War Cards: Arab-Israeli War, Korean War, Brush War, Indo-Pakistani War or Iran-Iraq War. This event cancelled by \'An Evil Empire\'.'
        self.event_unique = True

    def can_event(self, game_instance, side):
        return False if 'An_Evil_Empire' in game_instance.basket[Side.US] else True


class U2_Incident(Card):
    def __init__(self):
        super().__init__()
        self.name = 'U2_Incident'
        self.card_index = 60
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'USSR gains 1 VP. If UN Intervention played later this turn as an Event, either by US or USSR, gain 1 additional VP.'
        self.event_unique = True


class OPEC(Card):
    def __init__(self):
        super().__init__()
        self.name = 'OPEC'
        self.card_index = 61
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'USSR gains 1VP for each of the following countries he controls: Egypt, Iran, Libya, Saudi Arabia, Iraq, Gulf States, and Venezuela. Unplayable as an event if \'North Sea Oil\' is in effect.'

    def can_event(self, game_instance, side):
        return False if 'North_Sea_Oil' in game_instance.basket[Side.US] or 'North_Sea_Oil' in game_instance.removed_pile else True


class Lone_Gunman(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Lone_Gunman'
        self.card_index = 62
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 1
        self.owner = Side.USSR
        self.event_text = 'US player reveals his hand. Then the USSR may Conduct Operations as if they played a 1 Op card.'
        self.event_unique = True


class Colonial_Rear_Guards(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Colonial_Rear_Guards'
        self.card_index = 63
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'Add 1 US Influence in each of four different African and/or Southeast Asian countries.'


class Panama_Canal_Returned(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Panama_Canal_Returned'
        self.card_index = 64
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 1
        self.owner = Side.US
        self.event_text = 'Add 1 US Influence in Panama, Costa Rica, and Venezuela.'
        self.event_unique = True


class Camp_David_Accords(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Camp_David_Accords'
        self.card_index = 65
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'US gains 1 VP. US receives 1 Influence in Israel, Jordan and Egypt. Arab-Israeli War event no longer playable.'
        self.event_unique = True


class Puppet_Governments(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Puppet_Governments'
        self.card_index = 66
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'US may add 1 Influence in three countries that currently contain no Influence from either power.'
        self.event_unique = True


class Grain_Sales_to_Soviets(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Grain_Sales_to_Soviets'
        self.card_index = 67
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'Randomly choose one card from USSR hand. Play it or return it. If Soviet player has no cards, or returned, use this card to conduct Operations normally.'


class John_Paul_II_Elected_Pope(Card):
    def __init__(self):
        super().__init__()
        self.name = 'John_Paul_II_Elected_Pope'
        self.card_index = 68
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'Remove 2 USSR Influence in Poland and then add 1 US Influence in Poland. Allows play of \'Solidarity\'.'
        self.event_unique = True


class Latin_American_Death_Squads(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Latin_American_Death_Squads'
        self.card_index = 69
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'All of the player\'s Coup attempts in Central and South America are +1 for the remainder of the turn, while all opponent\'s Coup attempts are -1 for the remainder of the turn.'


class OAS_Founded(Card):
    def __init__(self):
        super().__init__()
        self.name = 'OAS_Founded'
        self.card_index = 70
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 1
        self.owner = Side.US
        self.event_text = 'Add 2 US Influence in Central America and/or South America.'
        self.event_unique = True


class Nixon_Plays_The_China_Card(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Nixon_Plays_The_China_Card'
        self.card_index = 71
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'If US has \'The China Card\', gain 2 VP. Otherwise, US player receives \'The China Card\' now, face down and unavailable for immediate play.'
        self.event_unique = True


class Sadat_Expels_Soviets(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Sadat_Expels_Soviets'
        self.card_index = 72
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 1
        self.owner = Side.US
        self.event_text = 'Remove all USSR Influence in Egypt and add one US Influence.'
        self.event_unique = True


class Shuttle_Diplomacy(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Shuttle_Diplomacy'
        self.card_index = 73
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'Play in front of US player. During the next scoring of the Middle East or Asia (whichever comes first), subtract one Battleground country from USSR total, then put this card in the discard pile. Does not count for Final Scoring at the end of Turn 10.'


class The_Voice_Of_America(Card):
    def __init__(self):
        super().__init__()
        self.name = 'The_Voice_Of_America'
        self.card_index = 74
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'Remove 4 USSR Influence from non-European countries. No more than 2 may be removed from any one country.'


class Liberation_Theology(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Liberation_Theology'
        self.card_index = 75
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'Add 3 USSR Influence in Central America, no more than 2 per country.'


class Ussuri_River_Skirmish(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Ussuri_River_Skirmish'
        self.card_index = 76
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'If the USSR has \'The China Card\', claim it face up and available for play. If the US already has \'The China Card\', add 4 US Influence in Asia, no more than 2 per country.'
        self.event_unique = True


class Ask_Not_What_Your_Country_Can_Do_For_You(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Ask_Not_What_Your_Country_Can_Do_For_You'
        self.card_index = 77
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'US player may discard up to entire hand (including Scoring cards) and draw replacements from the deck. The number of cards discarded must be decided prior to drawing any replacements.'
        self.event_unique = True


class Alliance_for_Progress(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Alliance_for_Progress'
        self.card_index = 78
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'US gains 1 VP for each US controlled Battleground country in Central America and South America.'
        self.event_unique = True


class Africa_Scoring(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Africa_Scoring'
        self.card_index = 79
        self._add_to_card()
        self.card_type = 'Scoring'
        self.stage = 'Mid War'
        self.scoring_region = 'Africa'
        self.event_text = 'Both sides score: Presence: 1, Domination: 4, Control: 6. +1 per controlled Battleground Country in Region'
        self.may_be_held = False


class One_Small_Step(Card):
    def __init__(self):
        super().__init__()
        self.name = 'One_Small_Step'
        self.card_index = 80
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'If you are behind on the Space Race Track, play this card to move your marker two boxes forward on the Space Rack Track, gaining the VP value of the second box only.'

    def can_event(self, game_instance, side):
        return True if game_instance.space_track[side] < game_instance.space_track[side.opp] else False


class South_America_Scoring(Card):
    def __init__(self):
        super().__init__()
        self.name = 'South_America_Scoring'
        self.card_index = 81
        self._add_to_card()
        self.card_type = 'Scoring'
        self.stage = 'Mid War'
        self.scoring_region = 'South America'
        self.event_text = 'Both sides score: Presence: 2, Domination: 5, Control: 6. +1 per controlled Battleground Country in Region'
        self.may_be_held = False


# -- OPTIONAL
class Che(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Che'
        self.card_index = 107
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.optional = True
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'USSR may immediately make a Coup attempt using this card\'s Operations value against a non-battleground country in Central America, South America, or Africa. If the Coup removes any US Influence, USSR may make a second Coup attempt against a different target under the same restrictions.'


# -- OPTIONAL
class Our_Man_In_Tehran(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Our_Man_In_Tehran'
        self.card_index = 108
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Mid War'
        self.optional = True
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'If the US controls at least one Middle East country, the US player draws the top 5 cards from the draw pile. They may reveal and then discard any or all of these drawn cards without triggering the Event. Any remaining drawn cards are returned to the draw deck, and it is reshuffled.'
        self.event_unique = True

    def can_event(self, game_instance, side):
        return any(game_instance.map[n].control == Side.US for n in CountryInfo.REGION_ALL[MapRegion.MIDDLE_EAST])


# --
# -- LATE WAR
# --


class Iranian_Hostage_Crisis(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Iranian_Hostage_Crisis'
        self.card_index = 82
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'Remove all US Influence in Iran. Add 2 USSR Influence in Iran. Doubles the effect of Terrorism card against US.'
        self.event_unique = True


class The_Iron_Lady(Card):
    def __init__(self):
        super().__init__()
        self.name = 'The_Iron_Lady'
        self.card_index = 83
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'US gains 1 VP. Add 1 USSR Influence in Argentina. Remove all USSR Influence from UK. Socialist Governments event no longer playable.'
        self.event_unique = True


class Reagan_Bombs_Libya(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Reagan_Bombs_Libya'
        self.card_index = 84
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'US gains 1 VP for every 2 USSR Influence in Libya.'
        self.event_unique = True


class Star_Wars(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Star_Wars'
        self.card_index = 85
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'If the US is ahead on the Space Race Track, play this card to search through the discard pile for a non-scoring card of your choice. Event occurs immediately.'
        self.event_unique = True

    def can_event(self, game_instance, side):
        return True if game_instance.space_track[Side.US] > game_instance.space_track[Side.USSR] else False


class North_Sea_Oil(Card):
    def __init__(self):
        super().__init__()
        self.name = 'North_Sea_Oil'
        self.card_index = 86
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'OPEC event is no longer playable. US may play 8 cards this turn.'
        self.event_unique = True


class The_Reformer(Card):
    def __init__(self):
        super().__init__()
        self.name = 'The_Reformer'
        self.card_index = 87
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'Add 4 Influence in Europe (no more than 2 per country). If USSR is ahead of US in VP, then 6 Influence may be added instead. USSR may no longer conduct Coup attempts in Europe. Improves effect of Glasnost event.'
        self.event_unique = True


class Marine_Barracks_Bombing(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Marine_Barracks_Bombing'
        self.card_index = 88
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'Remove all US Influence in Lebanon plus remove 2 additional US Influence from anywhere in the Middle East.'
        self.event_unique = True


class Soviets_Shoot_Down_KAL_007(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Soviets_Shoot_Down_KAL_007'
        self.card_index = 89
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 4
        self.owner = Side.US
        self.event_text = 'Degrade DEFCON one level. US gains 2 VP. If South Korea is US Controlled, then the US may place Influence or attempt Realignment as if they played a 4 Ops card.'
        self.event_unique = True


class Glasnost(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Glasnost'
        self.card_index = 90
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 4
        self.owner = Side.USSR
        self.event_text = 'USSR gains 2 VP. Improve DEFCON one level. If The Reformer is in effect, then the USSR may place Influence or attempt Realignments as if they played a 4 Ops card.'
        self.event_unique = True


class Ortega_Elected_in_Nicaragua(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Ortega_Elected_in_Nicaragua'
        self.card_index = 91
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'Remove all US Influence from Nicaragua. Then USSR may make one free Coup attempt (with this card\'s Operations value) in a country adjacent to Nicaragua.'
        self.event_unique = True


class Terrorism(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Terrorism'
        self.card_index = 92
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'Opponent must randomly discard one card. If played by USSR and Iranian Hostage Crisis is in effect, the US player must randomly discard two cards. (Events on discards do not occur.)'


class Iran_Contra_Scandal(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Iran_Contra_Scandal'
        self.card_index = 93
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'All US Realignment rolls have a -1 die roll modifier for the remainder of the turn.'
        self.event_unique = True


class Chernobyl(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Chernobyl'
        self.card_index = 94
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'The US player may designate one Region. For the remainder of the turn the USSR may not add additional Influence to that Region by the play of Operations Points via placing Influence.'
        self.event_unique = True


class Latin_American_Debt_Crisis(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Latin_American_Debt_Crisis'
        self.card_index = 95
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'Unless the US Player immediately discards a \'3\' or greater Operations card, double USSR Influence in two countries in South America.'
        self.event_unique = True


class Tear_Down_This_Wall(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Tear_Down_This_Wall'
        self.card_index = 96
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'Cancels/prevent Willy Brandt. Add 3 US Influence in East Germany. Then US may make a free Coup attempt or Realignment rolls in Europe using this card\'s Ops Value.'
        self.event_unique = True


class An_Evil_Empire(Card):
    def __init__(self):
        super().__init__()
        self.name = 'An_Evil_Empire'
        self.card_index = 97
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'Cancels/Prevents Flower Power. US gains 1 VP.'
        self.event_unique = True


class Aldrich_Ames_Remix(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Aldrich_Ames_Remix'
        self.card_index = 98
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'US player exposes his hand to USSR player for remainder of turn. USSR then chooses one card from US hand, this card is discarded.'
        self.event_unique = True


class Pershing_II_Deployed(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Pershing_II_Deployed'
        self.card_index = 99
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 3
        self.owner = Side.USSR
        self.event_text = 'USSR gains 1 VP. Remove 1 US Influence from up to three countries in Western Europe.'
        self.event_unique = True


class Wargames(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Wargames'
        self.card_index = 100
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 4
        self.owner = Side.NEUTRAL
        self.event_text = 'If DEFCON Status 2, you may immediately end the game (without Final Scoring Phase) after giving opponent 6 VPs. How about a nice game of chess?'
        self.event_unique = True

    def can_event(self, game_instance, side):
        return True if game_instance.defcon_track == 2 else False


class Solidarity(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Solidarity'
        self.card_index = 101
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 2
        self.owner = Side.US
        self.event_text = 'Playable as an event only if John Paul II Elected Pope is in effect. Add 3 US Influence in Poland.'
        self.event_unique = True

    def can_event(self, game_instance, side):
        return False if 'John_Paul_II_Elected_Pope' in game_instance.basket[Side.US] else True


class Iran_Iraq_War(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Iran_Iraq_War'
        self.card_index = 102
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'Iran or Iraq invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to target of invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track Effects of Victory: Player gains 2 VP and replaces opponent\'s Influence in target country with his own.'
        self.event_unique = True


# -- OPTIONAL
class Yuri_and_Samantha(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Yuri_and_Samantha'
        self.card_index = 109
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.optional = True
        self.ops = 2
        self.owner = Side.USSR
        self.event_text = 'USSR receives 1 VP for each US coup attempt made for the remainder of the current turn.'
        self.event_unique = True


# -- OPTIONAL
class AWACS_Sale_to_Saudis(Card):
    def __init__(self):
        super().__init__()
        self.name = 'AWACS_Sale_to_Saudis'
        self.card_index = 110
        self._add_to_card()
        self.card_type = 'Event'
        self.stage = 'Late War'
        self.optional = True
        self.ops = 3
        self.owner = Side.US
        self.event_text = 'US receives 2 Influence in Saudi Arabia. Muslim Revolution may no longer be played as an event.'
        self.event_unique = True


class Blank_1_Op_Card(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Blank_1_Op_Card'
        self.card_index = 150
        self._add_to_card()
        self.card_type = 'Template'
        self.stage = 'Template'
        self.optional = False
        self.ops = 1
        self.owner = Side.NEUTRAL
        self.event_text = 'This is a blank card worth 1 operations points.'
        self.event_unique = False

    def can_event(self, game_instance, side):
        return False


class Blank_2_Op_Card(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Blank_2_Op_Card'
        self.card_index = 151
        self._add_to_card()
        self.card_type = 'Template'
        self.stage = 'Template'
        self.optional = False
        self.ops = 2
        self.owner = Side.NEUTRAL
        self.event_text = 'This is a blank card worth 2 operations points.'
        self.event_unique = False

    def can_event(self, game_instance, side):
        return False


class Blank_3_Op_Card(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Blank_3_Op_Card'
        self.card_index = 152
        self._add_to_card()
        self.card_type = 'Template'
        self.stage = 'Template'
        self.optional = False
        self.ops = 3
        self.owner = Side.NEUTRAL
        self.event_text = 'This is a blank card worth 3 operations points.'
        self.event_unique = False

    def can_event(self, game_instance, side):
        return False


class Blank_4_Op_Card(Card):
    def __init__(self):
        super().__init__()
        self.name = 'Blank_4_Op_Card'
        self.card_index = 153
        self._add_to_card()
        self.card_type = 'Template'
        self.stage = 'Template'
        self.optional = False
        self.ops = 4
        self.owner = Side.NEUTRAL
        self.event_text = 'This is a blank card worth 4 operations points.'
        self.event_unique = False

    def can_event(self, game_instance, side):
        return False


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
Soviets_Shoot_Down_KAL_007 = Soviets_Shoot_Down_KAL_007()
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
Blank_1_Op_Card = Blank_1_Op_Card()
Blank_2_Op_Card = Blank_2_Op_Card()
Blank_3_Op_Card = Blank_3_Op_Card()
Blank_4_Op_Card = Blank_4_Op_Card()
