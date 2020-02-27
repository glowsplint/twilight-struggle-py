from abc import ABC, abstractmethod
from twilight_map import MapRegion, CountryInfo
from twilight_enums import Side, MapRegion, InputType, CardAction


class GameCards:

    def __init__(self):

        self.ALL = dict()
        self.early_war = []
        self.mid_war = []
        self.late_war = []

        # for name in CardInfo.ALL.keys():
        #     self.ALL[name] = Card(name)
        #     if self.ALL[name].info.stage == 'Early War':
        #         self.early_war.append(name)
        #     if self.ALL[name].info.stage == 'Mid War':
        #         self.mid_war.append(name)
        #     if self.ALL[name].info.stage == 'Late War':
        #         self.late_war.append(name)

    def __getitem__(self, item):
        return self.ALL[item]


class Card:

    name = ''
    card_type = ''
    stage = ''
    card_index = 0
    ops = 0
    text = ''
    owner = 'NEUTRAL'
    optional = False

    event_unique = False
    scoring_region = ''
    may_be_held = True
    resolve_headline_first = False
    can_headline = True

    # def __init__(self, name):
    #     self.info = CardInfo.ALL[name]
    #     self.is_playable = True

    def __repr__(self):
        if self.info.card_type == 'Scoring':
            return self.info.name
        else:
            return f'{self.info.name} - {self.info.ops}'

    def __eq__(self, other: str):
        return self.info.name == other

    def can_event(self):
        pass

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
    name = 'Asia_Scoring'
    card_type = 'Scoring'
    stage = 'Early War'
    card_index = 1
    scoring_region = 'Asia'
    event_text = 'Both sides score: Presence: 3, Domination: 7, Control: 9. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
    may_be_held = False


class Europe_Scoring(Card):
    name = 'Europe_Scoring'
    card_type = 'Scoring'
    stage = 'Early War'
    card_index = 2
    scoring_region = 'Europe'
    event_text = 'Both sides score: Presence: 3, Domination: 7, Control: VICTORY. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
    may_be_held = False


class Middle_East_Scoring(Card):
    name = 'Middle_East_Scoring'
    card_type = 'Scoring'
    stage = 'Early War'
    card_index = 3
    scoring_region = 'Middle East'
    event_text = 'Both sides score: Presence: 3, Domination: 5, Control: 7. +1 per controlled Battleground Country in Region'
    may_be_held = False


class Duck_and_Cover(Card):
    name = 'Duck_and_Cover'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 4
    ops = 3
    owner = 'US'
    event_text = 'Degrade DEFCON one level. Then US player earns VPs equal to 5 minus current DEFCON level.'


class Five_Year_Plan(Card):
    name = 'Five_Year_Plan'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 5
    ops = 3
    owner = 'US'
    event_text = 'USSR player must randomly discard one card. If the card is a US associated Event, the Event occurs immediately. If the card is a USSR associated Event or and Event applicable to both players, then the card must be discarded without triggering the Event.'


class The_China_Card(Card):
    name = 'The_China_Card'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 6
    ops = 4
    owner = 'NEUTRAL'
    can_headline = False
    event_text = 'Begins the game with the USSR player. +1 Operations value when all points are used in Asia. Pass to opponent after play. +1 VP for the player holding this card at the end of Turn 10. Cancels effect of \'Formosan Resolution\' if this card is played by the US player.'


class Socialist_Governments(Card):
    name = 'Socialist_Governments'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 7
    ops = 3
    owner = 'USSR'
    event_text = 'Unplayable as an event if \'The Iron Lady\' is in effect. Remove US Influence in Western Europe by a total of 3 Influence points, removing no more than 2 per country.'


class Fidel(Card):
    name = 'Fidel'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 8
    ops = 2
    owner = 'USSR'
    event_text = 'Remove all US Influence in Cuba. USSR gains sufficient Influence in Cuba for Control.'
    event_unique = True


class Vietnam_Revolts(Card):
    name = 'Vietnam_Revolts'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 9
    ops = 2
    owner = 'USSR'
    event_text = 'Add 2 USSR Influence in Vietnam. For the remainder of the turn, the Soviet player may add 1 Operations point to any card that uses all points in Southeast Asia.'
    event_unique = True


class Blockade(Card):
    name = 'Blockade'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 10
    ops = 1
    owner = 'USSR'
    event_text = 'Unless US Player immediately discards a \'3\' or more value Operations card, eliminate all US Influence in West Germany.'
    event_unique = True


class Korean_War(Card):
    name = 'Korean_War'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 11
    ops = 2
    owner = 'USSR'
    event_text = 'North Korea invades South Korea. Roll one die and subtract 1 for every US Controlled country adjacent to South Korea. USSR Victory on modified die roll 4-6. USSR add 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in South Korea with USSR Influence.'
    event_unique = True


class Romanian_Abdication(Card):
    name = 'Romanian_Abdication'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 12
    ops = 1
    owner = 'USSR'
    event_text = 'Remove all US Influence in Romania. USSR gains sufficient Influence in Romania for Control.'
    event_unique = True


class Arab_Israeli_War(Card):
    name = 'Arab_Israeli_War'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 13
    ops = 2
    owner = 'USSR'
    event_text = 'A Pan-Arab Coalition invades Israel. Roll one die and subtract 1 for US Control of Israel and for US-controlled country adjacent to Israel. USSR Victory on modified die roll 4-6. USSR adds 2 to Military Ops Track. Effects of Victory: USSR gains 2 VP and replaces all US Influence in Israel with USSR Influence.'


class COMECON(Card):
    name = 'COMECON'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 14
    ops = 3
    owner = 'USSR'
    event_text = 'Add 1 USSR Influence in each of four non-US Controlled countries in Eastern Europe.'
    event_unique = True


class Nasser(Card):
    name = 'Nasser'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 15
    ops = 1
    owner = 'USSR'
    event_text = 'Add 2 USSR Influence in Egypt. Remove half (rounded up) of the US Influence in Egypt.'
    event_unique = True


class Warsaw_Pact_Formed(Card):
    name = 'Warsaw_Pact_Formed'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 16
    ops = 3
    owner = 'USSR'
    event_text = 'Remove all US Influence from four countries in Eastern Europe, or add 5 USSR Influence in Eastern Europe, adding no more than 2 per country. Allow play of NATO.'
    event_unique = True


class De_Gaulle_Leads_France(Card):
    name = 'De_Gaulle_Leads_France'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 17
    ops = 3
    owner = 'USSR'
    event_text = 'Remove 2 US Influence in France, add 1 USSR Influence. Cancels effects of NATO for France.'
    event_unique = True


class Captured_Nazi_Scientist(Card):
    name = 'Captured_Nazi_Scientist'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 18
    ops = 1
    owner = 'NEUTRAL'
    event_text = 'Advance player\'s Space Race marker one box.'
    event_unique = True


class Truman_Doctrine(Card):
    name = 'Truman_Doctrine'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 19
    ops = 1
    owner = 'US'
    event_text = 'Remove all USSR Influence markers in one uncontrolled country in Europe.'
    event_unique = True


class Olympic_Games(Card):
    name = 'Olympic_Games'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 20
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'Player sponsors Olympics. Opponent may participate or boycott. If Opponent participates, each player rolls one die, with the sponsor adding 2 to his roll. High roll gains 2 VP. Reroll ties If Opponent boycotts, degrade DEFCON one level and the Sponsor may Conduct Operations as if they played a 4 Ops card.'


class NATO(Card):
    name = 'NATO'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 21
    ops = 4
    owner = 'US'
    event_text = 'Play after \'Marshall Plan\' or \'Warsaw Pact\'. USSR player may no longer make Coup or Realignment rolls in any US Controlled countries in Europe. US Controlled countries in Europe may not be attacked by play of the Brush War event.'
    event_unique = True


class Independent_Reds(Card):
    name = 'Independent_Reds'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 22
    ops = 2
    owner = 'US'
    event_text = 'Adds sufficient US Influence in either Yugoslavia, Romania, Bulgaria, Hungary, or Czechoslavakia to equal USSR Influence.'
    event_unique = True


class Marshall_Plan(Card):
    name = 'Marshall_Plan'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 23
    ops = 4
    owner = 'US'
    event_text = 'Allows play of NATO. Add one US Influence in each of seven non-USSR Controlled Western European countries.'
    event_unique = True


class Indo_Pakistani_War(Card):
    name = 'Indo_Pakistani_War'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 24
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'India or Pakistan invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to the target of the invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track. Effects of Victory: Player gains 2 VP and replaces all opponent\'s Influence in target country with his Influence.'


class Containment(Card):
    name = 'Containment'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 25
    ops = 3
    owner = 'US'
    event_text = 'All further Operations cards played by US this turn add one to their value (to a maximum of 4).'
    event_unique = True


class CIA_Created(Card):
    name = 'CIA_Created'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 26
    ops = 1
    owner = 'US'
    event_text = 'USSR reveals hand this turn. Then the US may Conduct Operations as if they played a 1 Op card.'
    event_unique = True


class US_Japan_Mutual_Defense_Pact(Card):
    name = 'US_Japan_Mutual_Defense_Pact'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 27
    ops = 4
    owner = 'US'
    event_text = 'US gains sufficient Influence in Japan for Control. USSR may no longer make Coup or Realignment rolls in Japan.'
    event_unique = True


class Suez_Crisis(Card):
    name = 'Suez_Crisis'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 28
    ops = 3
    owner = 'USSR'
    event_text = 'Remove a total of 4 US Influence from France, the United Kingdom or Israel. Remove no more than 2 Influence per country.'
    event_unique = True


class East_European_Unrest(Card):
    name = 'East_European_Unrest'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 29
    ops = 3
    owner = 'US'
    event_text = 'In Early or Mid War: Remove 1 USSR Influence from three countries in Eastern Europe. In Late War: Remove 2 USSR Influence from three countries in Eastern Europe.'


class Decolonization(Card):
    name = 'Decolonization'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 30
    ops = 2
    owner = 'USSR'
    event_text = 'Add one USSR Influence in each of any four African and/or SE Asian countries.'


class Red_Scare_Purge(Card):
    name = 'Red_Scare_Purge'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 31
    ops = 4
    owner = 'NEUTRAL'
    event_text = 'All further Operations cards played by your opponent this turn are -1 to their value (to a minimum of 1 Op).'


class UN_Intervention(Card):
    name = 'UN_Intervention'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 32
    ops = 1
    owner = 'NEUTRAL'
    can_headline = False
    event_text = 'Play this card simultaneously with a card containing your opponent\'s associated Event. The Event is cancelled, but you may use its Operations value to Conduct Operations. The cancelled event returns to the discard pile. May not be played during headline phase.'


class De_Stalinization(Card):
    name = 'De_Stalinization'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 33
    ops = 3
    owner = 'USSR'
    event_text = 'USSR may relocate up to 4 Influence points to non-US controlled countries. No more than 2 Influence may be placed in the same country.'
    event_unique = True


class Nuclear_Test_Ban(Card):
    name = 'Nuclear_Test_Ban'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 34
    ops = 4
    owner = 'NEUTRAL'
    event_text = 'Player earns VPs equal to the current DEFCON level minus 2, then improve DEFCON two levels.'


class Formosan_Resolution(Card):
    name = 'Formosan_Resolution'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 35
    ops = 2
    owner = 'US'
    event_text = 'Taiwan shall be treated as a Battleground country for scoring purposes, if the US controls Taiwan when the Asia Scoring Card is played or during Final Scoring at the end of Turn 10. Taiwan is not a battleground country for any other game purpose. This card is discarded after US play of \'The China Card\'.'
    event_unique = True


class Defectors(Card):
    name = 'Defectors'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 103
    ops = 2
    owner = 'US'
    resolve_headline_first = True
    event_text = 'Play in Headline Phase to cancel USSR Headline event, including Scoring Card. Cancelled card returns to the Discard Pile. If Defectors played by USSR during Soviet action round, US gains 1 VP (unless played on the Space Race).'


# -- OPTIONAL
class The_Cambridge_Five(Card):
    name = 'The_Cambridge_Five'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 104
    optional_card = True
    ops = 2
    owner = 'USSR'
    event_text = 'The US player exposes all scoring cards in their hand. The USSR player may then add 1 Influence in any single region named on one of those scoring cards (USSR choice). Cannot be played as an event in Late War.'


# -- OPTIONAL
class Special_Relationship(Card):
    name = 'Special_Relationship'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 105
    optional_card = True
    ops = 2
    owner = 'US'
    event_text = 'If UK is US controlled but NATO is not in effect, US adds 1 Influence to any country adjacent to the UK. If UK is US controlled and NATO is in effect, US adds 2 Influence to any Western European country and gains 2 VPs.'


# -- OPTIONAL
class NORAD(Card):
    name = 'NORAD'
    card_type = 'Event'
    stage = 'Early War'
    card_index = 106
    optional_card = True
    ops = 3
    owner = 'US'
    event_text = 'If the US controls Canada, the US may add 1 Influence to any country already containing US Influence at the conclusion of any Action Round in which the DEFCON marker moves to the \'2\' box. This event cancelled by \'Quagmire\'.'
    event_unique = True


# --
# -- MID WAR
# --
#
#

class Brush_War(Card):
    name = 'Brush_War'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 36
    ops = 3
    owner = 'NEUTRAL'
    event_text = 'Attack any country with a stability of 1 or 2. Roll a die and subtract 1 for every adjacent enemy controlled country. Success on 3-6. Player adds 3 to his Military Ops Track. Effects of Victory: Player gains 1 VP and replaces all opponent\'s Influence with his Influence.'


class Central_America_Scoring(Card):
    name = 'Central_America_Scoring'
    card_type = 'Scoring'
    stage = 'Mid War'
    card_index = 37
    scoring_region = 'Central America'
    event_text = 'Both sides score: Presence: 1, Domination: 3, Control: 5. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower'
    may_be_held = False


class Southeast_Asia_Scoring(Card):
    name = 'Southeast_Asia_Scoring'
    card_type = 'Scoring'
    stage = 'Mid War'
    card_index = 38
    may_be_held = False
    scoring_region = 'Southeast Asia'
    event_text = 'Both sides score: 1 VP each for Control of: Burma, Cambodia/Laos, Vietnam, Malaysia, Indonesia, the Phillipines, 2 VP for Control of Thailand'
    event_unique = True


class Arms_Race(Card):
    name = 'Arms_Race'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 39
    ops = 3
    owner = 'NEUTRAL'
    event_text = 'Compare each player\'s status on the Military Operations Track. If Phasing Player has more Military Operations points, he scores 1 VP. If Phasing Player has more Military Operations points and has met the Required Military Operations amount, he scores 3 VP instead.'


class Cuban_Missile_Crisis(Card):
    name = 'Cuban_Missile_Crisis'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 40
    ops = 3
    owner = 'NEUTRAL'
    event_text = 'Set DEFCON to Level 2. Any further Coup attempt by your opponent this turn, anywhere on the board, will result in Global Thermonuclear War. Your opponent will lose the game. This event may be cancelled at any time if the USSR player removes two Influence from Cuba or the US player removes 2 Influence from either West Germany or Turkey.'
    event_unique = True


class Nuclear_Subs(Card):
    name = 'Nuclear_Subs'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 41
    ops = 2
    owner = 'US'
    event_text = 'US Coup attempts in Battleground Countries do not affect the DEFCON track for the remainder of the turn (does not affect Cuban Missile Crisis).'
    event_unique = True


class Quagmire(Card):
    name = 'Quagmire'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 42
    ops = 3
    owner = 'USSR'
    event_text = 'On next action round, US player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each US player Action round until successful or no appropriate cards remain. If out of appropriate cards, the US player may only play scoring cards until the next turn.'
    event_unique = True


class Salt_Negotiations(Card):
    name = 'Salt_Negotiations'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 43
    ops = 3
    owner = 'NEUTRAL'
    event_text = 'Improve DEFCON two levels. Further Coup attempts incur -1 die roll modifier for both players for the remainder of the turn. Player may sort through discard pile and reclaim one non-scoring card, after revealing it to their opponent.'
    event_unique = True


class Bear_Trap(Card):
    name = 'Bear_Trap'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 44
    ops = 3
    owner = 'US'
    event_text = 'On next action round, USSR player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each USSR player Action Round until successful or no appropriate cards remain. If out of appropriate cards, the USSR player may only play scoring cards until the next turn.'
    event_unique = True


class Summit(Card):
    name = 'Summit'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 45
    ops = 1
    owner = 'NEUTRAL'
    event_text = 'Both players roll a die.  Each adds 1 for each Region they Dominate or Control. High roller gains 2 VP and may move DEFCON marker one level in either direction. Do not reroll ties.'


class How_I_Learned_to_Stop_Worrying(Card):
    name = 'How_I_Learned_to_Stop_Worrying'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 46
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'Set the DEFCON at any level you want (1-5). This event counts as 5 Military Operations for the purpose of required Military Operations.'
    event_unique = True


class Junta(Card):
    name = 'Junta'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 47
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'Place 2 Influence in any one Central or South American country. Then you may make a free Coup attempt or Realignment roll in one of these regions (using this card\'s Operations Value).'


class Kitchen_Debates(Card):
    name = 'Kitchen_Debates'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 48
    ops = 1
    owner = 'US'
    event_text = 'If the US controls more Battleground countries than the USSR, poke opponent in chest and gain 2 VP!'
    event_unique = True


class Missile_Envy(Card):
    name = 'Missile_Envy'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 49
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'Exchange this card for your opponent\'s highest valued Operations card in his hand. If two or more cards are tied, opponent chooses. If the exchanged card contains your event, or an event applicable to both players, it occurs immediately. If it contains opponent\'s event, use Operations value without triggering event. Opponent must use this card for Operations during his next action round.'


class We_Will_Bury_You(Card):
    name = 'We_Will_Bury_You'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 50
    ops = 4
    owner = 'USSR'
    event_text = 'Unless UN Invervention is played as an Event on the US player\'s next round, USSR gains 3 VP prior to any US VP award. Degrade DEFCON one level.'
    event_unique = True


class Brezhnev_Doctrine(Card):
    name = 'Brezhnev_Doctrine'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 51
    ops = 3
    owner = 'USSR'
    event_text = 'All further Operations cards played by the USSR this turn increase their Ops value by one (to a maximum of 4).'
    event_unique = True


class Portuguese_Empire_Crumbles(Card):
    name = 'Portuguese_Empire_Crumbles'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 52
    ops = 2
    owner = 'USSR'
    event_text = 'Add 2 USSR Influence in both SE African States and Angola.'
    event_unique = True


class South_African_Unrest(Card):
    name = 'South_African_Unrest'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 53
    ops = 2
    owner = 'USSR'
    event_text = 'USSR either adds 2 Influence in South Africa or adds 1 Influence in South Africa and 2 Influence in any countries adjacent to South Africa.'


class Allende(Card):
    name = 'Allende'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 54
    ops = 1
    owner = 'USSR'
    event_text = 'USSR receives 2 Influence in Chile.'
    event_unique = True


class Willy_Brandt(Card):
    name = 'Willy_Brandt'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 55
    ops = 2
    owner = 'USSR'
    event_text = 'USSR receives gains 1 VP. USSR receives 1 Influence in West Germany. Cancels NATO for West Germany. This event unplayable and/or cancelled by Tear Down This Wall.'
    event_unique = True


class Muslim_Revolution(Card):
    name = 'Muslim_Revolution'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 56
    ops = 4
    owner = 'USSR'
    event_text = 'Remove all US Influence in two of the following countries: Sudan, Iran, Iraq, Egypt, Libya, Saudi Arabia, Syria, Jordan.'


class ABM_Treaty(Card):
    name = 'ABM_Treaty'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 57
    ops = 4
    owner = 'NEUTRAL'
    event_text = 'Improve DEFCON one level. Then player may Conduct Operations as if they played a 4 Ops card.'


class Cultural_Revolution(Card):
    name = 'Cultural_Revolution'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 58
    ops = 3
    owner = 'USSR'
    event_text = 'If the US has \'The China Card\', claim it face up and available for play. If the USSR already had it, USSR gains 1 VP.'
    event_unique = True


class Flower_Power(Card):
    name = 'Flower_Power'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 59
    ops = 4
    owner = 'USSR'
    event_text = 'USSR gains 2 VP for every subsequently US played \'war card\' (played as an Event or Operations) unless played on the Space Race. War Cards: Arab-Israeli War, Korean War, Brush War, Indo-Pakistani War or Iran-Iraq War. This event cancelled by \'An Evil Empire\'.'
    event_unique = True


class U2_Incident(Card):
    name = 'U2_Incident'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 60
    ops = 3
    owner = 'USSR'
    event_text = 'USSR gains 1 VP. If UN Intervention played later this turn as an Event, either by US or USSR, gain 1 additional VP.'
    event_unique = True


class OPEC(Card):
    name = 'OPEC'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 61
    ops = 3
    owner = 'USSR'
    event_text = 'USSR gains 1VP for each of the following countries he controls: Egypt, Iran, Libya, Saudi Arabia, Iraq, Gulf States, and Venezuela. Unplayable as an event if \'North Sea Oil\' is in effect.'


class Lone_Gunman(Card):
    name = 'Lone_Gunman'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 62
    ops = 1
    owner = 'USSR'
    event_text = 'US player reveals his hand. Then the USSR may Conduct Operations as if they played a 1 Op card.'
    event_unique = True


class Colonial_Rear_Guards(Card):
    name = 'Colonial_Rear_Guards'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 63
    ops = 2
    owner = 'US'
    event_text = 'Add 1 US Influence in each of four different African and/or Southeast Asian countries.'


class Panama_Canal_Returned(Card):
    name = 'Panama_Canal_Returned'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 64
    ops = 1
    owner = 'US'
    event_text = 'Add 1 US Influence in Panama, Costa Rica, and Venezuela.'
    event_unique = True


class Camp_David_Accords(Card):
    name = 'Camp_David_Accords'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 65
    ops = 2
    owner = 'US'
    event_text = 'US gains 1 VP. US receives 1 Influence in Israel, Jordan and Egypt. Arab-Israeli War event no longer playable.'
    event_unique = True


class Puppet_Governments(Card):
    name = 'Puppet_Governments'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 66
    ops = 2
    owner = 'US'
    event_text = 'US may add 1 Influence in three countries that currently contain no Influence from either power.'
    event_unique = True


class Grain_Sales_to_Soviets(Card):
    name = 'Grain_Sales_to_Soviets'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 67
    ops = 2
    owner = 'US'
    event_text = 'Randomly choose one card from USSR hand. Play it or return it. If Soviet player has no cards, or returned, use this card to conduct Operations normally.'


class John_Paul_II_Elected_Pope(Card):
    name = 'John_Paul_II_Elected_Pope'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 68
    ops = 2
    owner = 'US'
    event_text = 'Remove 2 USSR Influence in Poland and then add 1 US Influence in Poland. Allows play of \'Solidarity\'.'
    event_unique = True


class Latin_American_Death_Squads(Card):
    name = 'Latin_American_Death_Squads'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 69
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'All of the player\'s Coup attempts in Central and South America are +1 for the remainder of the turn, while all opponent\'s Coup attempts are -1 for the remainder of the turn.'


class OAS_Founded(Card):
    name = 'OAS_Founded'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 70
    ops = 1
    owner = 'US'
    event_text = 'Add 2 US Influence in Central America and/or South America.'
    event_unique = True


class Nixon_Plays_The_China_Card(Card):
    name = 'Nixon_Plays_The_China_Card'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 71
    ops = 2
    owner = 'US'
    event_text = 'If US has \'The China Card\', gain 2 VP. Otherwise, US player receives \'The China Card\' now, face down and unavailable for immediate play.'
    event_unique = True


class Sadat_Expels_Soviets(Card):
    name = 'Sadat_Expels_Soviets'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 72
    ops = 1
    owner = 'US'
    event_text = 'Remove all USSR Influence in Egypt and add one US Influence.'
    event_unique = True


class Shuttle_Diplomacy(Card):
    name = 'Shuttle_Diplomacy'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 73
    ops = 3
    owner = 'US'
    event_text = 'Play in front of US player. During the next scoring of the Middle East or Asia (whichever comes first), subtract one Battleground country from USSR total, then put this card in the discard pile. Does not count for Final Scoring at the end of Turn 10.'


class The_Voice_Of_America(Card):
    name = 'The_Voice_Of_America'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 74
    ops = 2
    owner = 'US'
    event_text = 'Remove 4 USSR Influence from non-European countries. No more than 2 may be removed from any one country.'


class Liberation_Theology(Card):
    name = 'Liberation_Theology'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 75
    ops = 2
    owner = 'USSR'
    event_text = 'Add 3 USSR Influence in Central America, no more than 2 per country.'


class Ussuri_River_Skirmish(Card):
    name = 'Ussuri_River_Skirmish'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 76
    ops = 3
    owner = 'US'
    event_text = 'If the USSR has \'The China Card\', claim it face up and available for play. If the US already has \'The China Card\', add 4 US Influence in Asia, no more than 2 per country.'
    event_unique = True


class Ask_Not_What_Your_Country_Can_Do_For_You(Card):
    name = 'Ask_Not_What_Your_Country_Can_Do_For_You'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 77
    ops = 3
    owner = 'US'
    event_text = 'US player may discard up to entire hand (including Scoring cards) and draw replacements from the deck. The number of cards discarded must be decided prior to drawing any replacements.'
    event_unique = True


class Alliance_for_Progress(Card):
    name = 'Alliance_for_Progress'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 78
    ops = 3
    owner = 'US'
    event_text = 'US gains 1 VP for each US controlled Battleground country in Central America and South America.'
    event_unique = True


class Africa_Scoring(Card):
    name = 'Africa_Scoring'
    card_type = 'Scoring'
    stage = 'Mid War'
    card_index = 79
    scoring_region = 'Africa'
    event_text = 'Both sides score: Presence: 1, Domination: 4, Control: 6. +1 per controlled Battleground Country in Region'
    may_be_held = False


class One_Small_Step(Card):
    name = 'One_Small_Step'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 80
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'If you are behind on the Space Race Track, play this card to move your marker two boxes forward on the Space Rack Track, gaining the VP value of the second box only.'


class South_America_Scoring(Card):
    name = 'South_America_Scoring'
    card_type = 'Scoring'
    stage = 'Mid War'
    card_index = 81
    scoring_region = 'South America'
    event_text = 'Both sides score: Presence: 2, Domination: 5, Control: 6. +1 per controlled Battleground Country in Region'
    may_be_held = False


# -- OPTIONAL
class Che(Card):
    name = 'Che'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 107
    optional_card = True
    ops = 3
    owner = 'USSR'
    event_text = 'USSR may immediately make a Coup attempt using this card\'s Operations value against a non-battleground country in Central America, South America, or Africa. If the Coup removes any US Influence, USSR may make a second Coup attempt against a different target under the same restrictions.'


# -- OPTIONAL
class Our_Man_In_Tehran(Card):
    name = 'Our_Man_In_Tehran'
    card_type = 'Event'
    stage = 'Mid War'
    card_index = 108
    optional_card = True
    ops = 2
    owner = 'US'
    event_text = 'If the US controls at least one Middle East country, the US player draws the top 5 cards from the draw pile. They may reveal and then discard any or all of these drawn cards without triggering the Event. Any remaining drawn cards are returned to the draw deck, and it is reshuffled.'
    event_unique = True


# --
# -- LATE WAR
# --


class Iranian_Hostage_Crisis(Card):
    name = 'Iranian_Hostage_Crisis'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 82
    ops = 3
    owner = 'USSR'
    event_text = 'Remove all US Influence in Iran. Add 2 USSR Influence in Iran. Doubles the effect of Terrorism card against US.'
    event_unique = True


class The_Iron_Lady(Card):
    name = 'The_Iron_Lady'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 83
    ops = 3
    owner = 'US'
    event_text = 'US gains 1 VP. Add 1 USSR Influence in Argentina. Remove all USSR Influence from UK. Socialist Governments event no longer playable.'
    event_unique = True


class Reagan_Bombs_Libya(Card):
    name = 'Reagan_Bombs_Libya'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 84
    ops = 2
    owner = 'US'
    event_text = 'US gains 1 VP for every 2 USSR Influence in Libya.'
    event_unique = True


class Star_Wars(Card):
    name = 'Star_Wars'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 85
    ops = 2
    owner = 'US'
    event_text = 'If the US is ahead on the Space Race Track, play this card to search through the discard pile for a non-scoring card of your choice. Event occurs immediately.'
    event_unique = True


class North_Sea_Oil(Card):
    name = 'North_Sea_Oil'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 86
    ops = 3
    owner = 'US'
    event_text = 'OPEC event is no longer playable. US may play 8 cards this turn.'
    event_unique = True


class The_Reformer(Card):
    name = 'The_Reformer'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 87
    ops = 3
    owner = 'USSR'
    event_text = 'Add 4 Influence in Europe (no more than 2 per country). If USSR is ahead of US in VP, then 6 Influence may be added instead. USSR may no longer conduct Coup attempts in Europe. Improves effect of Glasnost event.'
    event_unique = True


class Marine_Barracks_Bombing(Card):
    name = 'Marine_Barracks_Bombing'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 88
    ops = 2
    owner = 'USSR'
    event_text = 'Remove all US Influence in Lebanon plus remove 2 additional US Influence from anywhere in the Middle East.'
    event_unique = True


class Soviets_Shoot_Down_KAL_007(Card):
    name = 'Soviets_Shoot_Down_KAL_007'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 89
    ops = 4
    owner = 'US'
    event_text = 'Degrade DEFCON one level. US gains 2 VP. If South Korea is US Controlled, then the US may place Influence or attempt Realignment as if they played a 4 Ops card.'
    event_unique = True


class Glasnost(Card):
    name = 'Glasnost'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 90
    ops = 4
    owner = 'USSR'
    event_text = 'USSR gains 2 VP. Improve DEFCON one level. If The Reformer is in effect, then the USSR may place Influence or attempt Realignments as if they played a 4 Ops card.'
    event_unique = True


class Ortega_Elected_in_Nicaragua(Card):
    name = 'Ortega_Elected_in_Nicaragua'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 91
    ops = 2
    owner = 'USSR'
    event_text = 'Remove all US Influence from Nicaragua. Then USSR may make one free Coup attempt (with this card\'s Operations value) in a country adjacent to Nicaragua.'
    event_unique = True


class Terrorism(Card):
    name = 'Terrorism'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 92
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'Opponent must randomly discard one card. If played by USSR and Iranian Hostage Crisis is in effect, the US player must randomly discard two cards. (Events on discards do not occur.)'


class Iran_Contra_Scandal(Card):
    name = 'Iran_Contra_Scandal'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 93
    ops = 2
    owner = 'USSR'
    event_text = 'All US Realignment rolls have a -1 die roll modifier for the remainder of the turn.'
    event_unique = True


class Chernobyl(Card):
    name = 'Chernobyl'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 94
    ops = 3
    owner = 'US'
    event_text = 'The US player may designate one Region. For the remainder of the turn the USSR may not add additional Influence to that Region by the play of Operations Points via placing Influence.'
    event_unique = True


class Latin_American_Debt_Crisis(Card):
    name = 'Latin_American_Debt_Crisis'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 95
    ops = 2
    owner = 'USSR'
    event_text = 'Unless the US Player immediately discards a \'3\' or greater Operations card, double USSR Influence in two countries in South America.'
    event_unique = True


class Tear_Down_This_Wall(Card):
    name = 'Tear_Down_This_Wall'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 96
    ops = 3
    owner = 'US'
    event_text = 'Cancels/prevent Willy Brandt. Add 3 US Influence in East Germany. Then US may make a free Coup attempt or Realignment rolls in Europe using this card\'s Ops Value.'
    event_unique = True


class An_Evil_Empire(Card):
    name = 'An_Evil_Empire'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 97
    ops = 3
    owner = 'US'
    event_text = 'Cancels/Prevents Flower Power. US gains 1 VP.'
    event_unique = True


class Aldrich_Ames_Remix(Card):
    name = 'Aldrich_Ames_Remix'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 98
    ops = 3
    owner = 'USSR'
    event_text = 'US player exposes his hand to USSR player for remainder of turn. USSR then chooses one card from US hand, this card is discarded.'
    event_unique = True


class Pershing_II_Deployed(Card):
    name = 'Pershing_II_Deployed'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 99
    ops = 3
    owner = 'USSR'
    event_text = 'USSR gains 1 VP. Remove 1 US Influence from up to three countries in Western Europe.'
    event_unique = True


class Wargames(Card):
    name = 'Wargames'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 100
    ops = 4
    owner = 'NEUTRAL'
    event_text = 'If DEFCON Status 2, you may immediately end the game (without Final Scoring Phase) after giving opponent 6 VPs. How about a nice game of chess?'
    event_unique = True


class Solidarity(Card):
    name = 'Solidarity'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 101
    ops = 2
    owner = 'US'
    event_text = 'Playable as an event only if John Paul II Elected Pope is in effect. Add 3 US Influence in Poland.'
    event_unique = True


class Iran_Iraq_War(Card):
    name = 'Iran_Iraq_War'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 102
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'Iran or Iraq invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to target of invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track Effects of Victory: Player gains 2 VP and replaces opponent\'s Influence in target country with his own.'
    event_unique = True


# -- OPTIONAL
class Yuri_and_Samantha(Card):
    name = 'Yuri_and_Samantha'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 109
    optional_card = True
    ops = 2
    owner = 'USSR'
    event_text = 'USSR receives 1 VP for each US coup attempt made for the remainder of the current turn.'
    event_unique = True


# -- OPTIONAL
class AWACS_Sale_to_Saudis(Card):
    name = 'AWACS_Sale_to_Saudis'
    card_type = 'Event'
    stage = 'Late War'
    card_index = 110
    optional_card = True
    ops = 3
    owner = 'US'
    event_text = 'US receives 2 Influence in Saudi Arabia. Muslim Revolution may no longer be played as an event.'
    event_unique = True


class Blank_1_Op_Card(Card):
    name = 'Blank_1_Op_Card'
    card_type = 'Template'
    stage = 'Template'
    card_index = 150
    optional_card = False
    ops = 1
    owner = 'NEUTRAL'
    event_text = 'This is a blank card worth 1 operations points.'
    event_unique = False


class Blank_2_Op_Card(Card):
    name = 'Blank_2_Op_Card'
    card_type = 'Template'
    stage = 'Template'
    card_index = 151
    optional_card = False
    ops = 2
    owner = 'NEUTRAL'
    event_text = 'This is a blank card worth 2 operations points.'
    event_unique = False


class Blank_3_Op_Card(Card):
    name = 'Blank_3_Op_Card'
    card_type = 'Template'
    stage = 'Template'
    card_index = 152
    optional_card = False
    ops = 3
    owner = 'NEUTRAL'
    event_text = 'This is a blank card worth 3 operations points.'
    event_unique = False


class Blank_4_Op_Card(Card):
    name = 'Blank_4_Op_Card'
    card_type = 'Template'
    stage = 'Template'
    card_index = 153
    optional_card = False
    ops = 4
    owner = 'NEUTRAL'
    event_text = 'This is a blank card worth 4 operations points.'
    event_unique = False
