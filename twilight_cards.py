from twilight_map import *

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

    def __init__(self, card_name="", card_type="", stage="", card_number=0,
                 optional_card=False,
                 operations_points=0,
                 event_text="", event_effects=None,
                 scoring_region="", may_be_held=True,
                 event_owner="NEUTRAL",
                 triggered_effects="",
                 continuous_effects="",
                 global_continuous_effects="",
                 usage_conditions="",
                 remove_if_used_as_event=False,
                 resolve_headline_first=False,
                 can_headline_card=True,
                 **kwargs):
        self.name = card_name
        self.type = card_type
        self.stage = stage
        self.index = card_number
        self.ops = operations_points
        self.text = event_text
        self.owner = Side[event_owner]
        self.optional = optional_card

        self.event_effects = event_effects
        self.triggered_effects = triggered_effects
        self.continuous_effects = continuous_effects
        self.global_continuous_effects = global_continuous_effects
        self.event_unique = remove_if_used_as_event
        self.scoring_region = scoring_region
        self.may_be_held = may_be_held
        self.usage_conditions = usage_conditions
        self.resolve_headline_first = resolve_headline_first
        self.can_headline_card = can_headline_card

        for key, value in kwargs.items():
            print(key, value)
            setattr(self, key, value)
        CardInfo.ALL[self.name] = self

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
        # for event in self.event_effects:
        #     event[0](event[1])
        # if hasattr(self, 'remove_if_used_as_event'):
        #     if self.remove_if_used_as_event:
        #     # to add functionality for remove cards from hand and into removed pile
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
        self.Early_War = []
        self.Mid_War = []
        self.Late_War = []

        for card_name in CardInfo.ALL.keys():
            self.ALL[card_name] = Card(card_name)
            if self.ALL[card_name].info.stage == 'Early War':
                self.Early_War.append(self.ALL[card_name])
            if self.ALL[card_name].info.stage == 'Mid War':
                self.Mid_War.append(self.ALL[card_name])
            if self.ALL[card_name].info.stage == 'Late War':
                self.Late_War.append(self.ALL[card_name])

    def __getitem__(self, item):
        return self.ALL[item]

class Card:
    def __init__(self, card_name):
        self.info = CardInfo.ALL[card_name]
        self.flipped = False # flipped means unavailable for use

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
	'card_name' : 'Asia_Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Early War',
	'card_number' : 1,
	'scoring_region' : 'Asia',
	'event_effects' : [('ScoreAsia', 0)],
	'event_text' : 'Both sides score: Presence: 3, Domination: 7, Control: 9. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower',
	'may_be_held' : False,
}

Europe_Scoring = {
	'card_name' : 'Europe_Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Early War',
	'card_number' : 2,
	'scoring_region' : 'Europe',
	'event_effects' : [('ScoreEurope', 0)],
	'event_text' : 'Both sides score: Presence: 3, Domination: 7, Control: VICTORY. +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower',
	'may_be_held' : False,
}

Middle_East_Scoring = {
	'card_name' : 'Middle_East_Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Early War',
	'card_number' : 3,
	'scoring_region' : 'Middle East',
	'event_effects' : [('ScoreMiddleEast', 0)],
	'event_text' : 'Both sides score: Presence: 3, Domination: 5, Control: 7. +1 per controlled Battleground Country in Region',
	'may_be_held' : False,
}

Duck_and_Cover = {
	'card_name' : 'Duck_and_Cover',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 4,
	'operations_points' : 3,
	'event_owner' : 'USA',
	'event_effects' : [('DegradeDEFCONLevel', 1), ('GainVictoryPointsForDEFCONBelow', 5)],
	'event_text' : 'Degrade DEFCON one level.\nThen US player earns VPs equal to 5 minus current DEFCON level.',
}

Five_Year_Plan = {
	'card_name' : 'Five_Year_Plan',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 5,
	'operations_points' : 3,
	'event_owner' : 'USA',
	'event_effects' : [('CommitPlayerDecision', 0), ('OpponentDiscardsRandomCard', 1)],
	'event_text' : 'USSR player must randomly discard one card. If the card is a US associated Event, the Event occurs immediately. If the card is a USSR associated Event or and Event applicable to both players, then the card must be discarded without triggering the Event.',
}

The_China_Card = {
	'card_name' : 'The_China_Card',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 6,
	'operations_points' : 4,
	'event_owner' : 'NEUTRAL',
	'can_headline_card' : False,
	'global_continuous_effects' : [('GainOperationsPointsWhenUsingThisCardInAsia', 1)],
	'event_text' : 'Begins the game with the USSR player.\n+1 Operations value when all points are used in Asia. Pass to opponent after play.\n+1 VP for the player holding this card at the end of Turn 10.\nCancels effect of \'Formosan Resolution\' if this card is played by the US player.',
}

Socialist_Governments = {
	'card_name' : 'Socialist_Governments',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 7,
	'operations_points' : 3,
	'event_owner' : 'USSR',
	'usage_conditions' : [('IfHasNotBeenPlayedIronLady', 0)],
	'event_effects' : [('RemoveOpponentInfluenceInWesternEuropeMax2', 3)],
	'event_text' : 'Unplayable as an event if \'The Iron Lady\' is in effect.\nRemove US Influence in Western Europe by a total of 3 Influence points, removing no more than 2 per country.',
}

Fidel = {
	'card_name' : 'Fidel',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 8,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'event_effects' : [('RemoveAllOpponentInfluenceInCuba', 0)],
	'event_text' : 'Remove all US Influence in Cuba. USSR gains sufficient Influence in Cuba for Control.',
	'remove_if_used_as_event' : True,
}

Vietnam_Revolts = {
	'card_name' : 'Vietnam_Revolts',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 9,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'event_effects' : [('GainInfluenceInVietnam', 2), ('PutThisCardInPlay', 1)],
	'continuous_effects' : [('GainOperationsPointsInSoutheastAsia', 1)],
	'triggered_effects' : [('AtEndOfTurnTriggerRemoveThisCardFromPlay', 0)],
	'event_text' : 'Add 2 USSR Influence in Vietnam. For the remainder of the turn, the Soviet player may add 1 Operations point to any card that uses all points in Southeast Asia.',
	'remove_if_used_as_event' : True,
}

Blockade = {
	'card_name' : 'Blockade',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 10,
	'operations_points' : 1,
	'event_owner' : 'USSR',
	'event_effects' : [('OpponentMayDiscardCardWithOpsPoints', 3)],
	'event_text' : 'Unless US Player immediately discards a \'3\' or more value Operations card, eliminate all US Influence in West Germany.',
	'remove_if_used_as_event' : True,
}

Korean_War = {
	'card_name' : 'Korean_War',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 11,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'event_effects' : [('CommitPlayerDecision', 0), ('WarInSouthKorea', 2)],
	'event_text' : 'North Korea invades South Korea. Roll one die and subtract 1 for every US Controlled country adjacent to South Korea. USSR Victory on modified die roll 4-6. USSR add 2 to Military Ops Track.\nEffects of Victory: USSR gains 2 VP and replaces all US Influence in South Korea with USSR Influence.',
	'remove_if_used_as_event' : True,
}

Romanian_Abdication = {
	'card_name' : 'Romanian_Abdication',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 12,
	'operations_points' : 1,
	'event_owner' : 'USSR',
	'event_effects' : [('RemoveAllOpponentInfluenceInRomania', 0)],
	'event_text' : 'Remove all US Influence in Romania. USSR gains sufficient Influence in Romania for Control.',
	'remove_if_used_as_event' : True,
}


Arab_Israeli_War = {
	'card_name' : 'Arab_Israeli_War',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 13,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'usage_conditions' : [('IfHasNotBeenPlayedCampDavidAccords', 0)],
	'event_effects' : [('CommitPlayerDecision', 0), ('WarInIsrael', 0)],
	'event_text' : 'A Pan-Arab Coalition invades Israel. Roll one die and subtract 1 for US Control of Israel and for US-controlled country adjacent to Israel. USSR Victory on modified die roll 4-6. USSR adds 2 to Military Ops Track.\nEffects of Victory: USSR gains 2 VP and replaces all US Influence in Israel with USSR Influence.',
}

COMECON = {
	'card_name' : 'COMECON',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 14,
	'operations_points' : 3,
	'event_owner' : 'USSR',
	'event_effects' : [('AddInfluenceInUncontrolledEasternEuropeMax1', 4)],
	'event_text' : 'Add 1 USSR Influence in each of four non-US Controlled countries in Eastern Europe.',
	'remove_if_used_as_event' : True,
}

Nasser = {
	'card_name' : 'Nasser',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 15,
	'operations_points' : 1,
	'event_owner' : 'USSR',
	'event_effects' : [('GainInfluenceInEgypt', 2)],
	'event_text' : 'Add 2 USSR Influence in Egypt. Remove half (rounded up) of the US Influence in Egypt.',
	'remove_if_used_as_event' : True,
}

Warsaw_Pact_Formed = {
	'card_name' : 'Warsaw_Pact_Formed',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 16,
	'operations_points' : 3,
	'event_owner' : 'USSR',
	'event_effects' : [('WarsawEffect', 0), ('PutThisCardInPlayOppOwnerIfHasNotBeenPlayedNATO', 0)],
	'event_text' : 'Remove all US Influence from four countries in Eastern Europe, or add 5 USSR Influence in Eastern Europe, adding no more than 2 per country. Allow play of NATO.',
	'remove_if_used_as_event' : True,
}

De_Gaulle_Leads_France = {
	'card_name' : 'De_Gaulle_Leads_France',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 17,
	'operations_points' : 3,
	'event_owner' : 'USSR',
	'event_effects' : [('RemoveOpponentInfluenceInFrance', 2), ('PutThisCardInPlay', 0)],
	'event_text' : 'Remove 2 US Influence in France, add 1 USSR Influence. Cancels effects of NATO for France.',
	'remove_if_used_as_event' : True,
}

Captured_Nazi_Scientist = {
	'card_name' : 'Captured_Nazi_Scientist',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 18,
	'operations_points' : 1,
	'event_owner' : 'NEUTRAL',
	'event_effects' : [('AdvanceSpaceRaceTrack', 1)],
	'event_text' : 'Advance player\'s Space Race marker one box.',
	'remove_if_used_as_event' : True,
}

Truman_Doctrine = {
	'card_name' : 'Truman_Doctrine',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 19,
	'operations_points' : 1,
	'event_owner' : 'USA',
	'event_effects' : [('RemoveAllOpponentInfluenceFromUncontrolledInEurope', 1)],
	'event_text' : 'Remove all USSR Influence markers in one uncontrolled country in Europe.',
	'remove_if_used_as_event' : True,
}


Olympic_Games = {
	'card_name' : 'Olympic_Games',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 20,
	'operations_points' : 2,
	'event_owner' : 'NEUTRAL',
	'event_effects' : [('ResolveOlympicGames', 4)],
	'event_text' : 'Player sponsors Olympics. Opponent may participate or boycott. If Opponent participates, each player rolls one die, with the sponsor adding 2 to his roll. High roll gains 2 VP. Reroll ties If Opponent boycotts, degrade DEFCON one level and the Sponsor may Conduct Operations as if they played a 4 Ops card.',
}

NATO = {
	'card_name' : 'NATO',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 21,
	'operations_points' : 4,
	'event_owner' : 'USA',
	'usage_conditions': [('IfHasBeenPlayedMarshallPlanOrWarsawPact', 0)],
	'event_effects' : [('PutThisCardInPlay', 0), ('RemoveMarshallPlanFromPlay', 0), ('RemoveWarsawPactFormedFromPlay', 0)],
	'continuous_effects' : [('OpponentCannotCoupOrRealignInControlledEurope', 0)],
	'event_text' : 'Play after \'Marshall Plan\' or \'Warsaw Pact\'.\nUSSR player may no longer make Coup or Realignment rolls in any US Controlled countries in Europe. US Controlled countries in Europe may not be attacked by play of the Brush War event.',
	'remove_if_used_as_event' : True,
}

Independent_Reds = {
	'card_name' : 'Independent_Reds',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 22,
	'operations_points' : 2,
	'event_owner' : 'USA',
	'event_effects' : [('MatchOpponentInfluenceForIndependentReds', 1)],
	'event_text' : 'Adds sufficient US Influence in either Yugoslavia, Romania, Bulgaria, Hungary, or Czechoslavakia to equal USSR Influence.',
	'remove_if_used_as_event' : True,
}

Marshall_Plan = {
	'card_name' : 'Marshall_Plan',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 23,
	'operations_points' : 4,
	'event_owner' : 'USA',
	'event_effects' : [('AddInfluenceInUncontrolledWesternEuropeMax1', 7), ('PutThisCardInPlay', 0)],
	'event_text' : 'Allows play of NATO.\nAdd one US Influence in each of seven non-USSR Controlled Western European countries.',
	'remove_if_used_as_event' : True,
}

Indo_Pakistani_War = {
	'card_name' : 'Indo_Pakistani_War',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 24,
	'operations_points' : 2,
	'event_owner' : 'NEUTRAL',
	'event_effects' : [('WarInIndiaOrPakistan', 0)],
	'event_text' : 'India or Pakistan invades the other (player\'s choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to the target of the invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track. Effects of Victory: Player gains 2 VP and replaces all opponent\'s Influence in target country with his Influence.',
}

Containment = {
	'card_name' : 'Containment',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 25,
	'operations_points' : 3,
	'event_owner' : 'USA',
	'event_effects' : [('PutThisCardInPlay', 1)],
	'continuous_effects' : [('IncreaseOperationsPointsForYourCards', 1)],
	'triggered_effects' : [('AtEndOfTurnTriggerRemoveThisCardFromPlay', 0)],
	'event_text' : 'All further Operations cards played by US this turn add one to their value (to a maximum of 4).',
	'remove_if_used_as_event' : True,
}

CIA_Created = {
	'card_name' : 'CIA_Created',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 26,
	'operations_points' : 1,
	'event_owner' : 'USA',
	'event_effects' : [('CommitPlayerDecision', 0), ('OpponentRevealsHand', 0), ('ConductOperationsWithThisCard', 1)],
	'event_text' : 'USSR reveals hand this turn. Then the US may Conduct Operations as if they played a 1 Op card.',
	'remove_if_used_as_event' : True,
}

US_Japan_Mutual_Defense_Pact = {
	'card_name' : 'US_Japan_Mutual_Defense_Pact',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 27,
	'operations_points' : 4,
	'event_owner' : 'USA',
	'event_effects' : [('GainInfluenceForControlInJapan', 0), ('PutThisCardInPlay', 0)],
	'continuous_effects' : [('OpponentCannotCoupOrRealignInJapan', 0)],
	'event_text' : 'US gains sufficient Influence in Japan for Control. USSR may no longer make Coup or Realignment rolls in Japan.',
	'remove_if_used_as_event' : True,
}

Suez_Crisis = {
	'card_name' : 'Suez_Crisis',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 28,
	'operations_points' : 3,
	'event_owner' : 'USSR',
	'event_effects' :[('RemoveOpponentInfluenceForSuezCrisis', 4)],
	'event_text' : 'Remove a total of 4 US Influence from France, the United Kingdom or Israel. Remove no more than 2 Influence per country.',
	'remove_if_used_as_event' : True,
}

East_European_Unrest = {
	'card_name' : 'East_European_Unrest',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 29,
	'operations_points' : 3,
	'event_owner' : 'USA',
	'event_effects' : [('Remove1OpponentInfluenceFromEasternEuropeCountriesIfTurnNumberLessThan7', 3), ('Remove2OpponentInfluenceFromEasternEuropeCountriesIfTurnNumberLessThan8', 3)],
	'event_text' : 'In Early or Mid War: Remove 1 USSR Influence from three countries in Eastern Europe. In Late War: Remove 2 USSR Influence from three countries in Eastern Europe.',
}

Decolonization = {
	'card_name' : 'Decolonization',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 30,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'event_effects' : [('AddInfluenceInAfricaOrSEAsiaMax1', 4)],
	'event_text' : 'Add one USSR Influence in each of any four African and/or SE Asian countries.',
}

Red_Scare_Purge = {
	'card_name' : 'Red_Scare_Purge',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 31,
	'operations_points' : 4,
	'event_owner' : 'NEUTRAL',
	'event_effects' : [('PutThisCardInPlay', 1)],
	'continuous_effects' : [('DecreaseOperationsPointsForOpponentsCards', 1)],
	'triggered_effects' : [('AtEndOfTurnTriggerRemoveThisCardFromPlay', 0)],
	'event_text' : 'All further Operations cards played by your opponent this turn are -1 to their value (to a minimum of 1 Op).',
}

UN_Intervention = {
	'card_name' : 'UN_Intervention',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 32,
	'operations_points' : 1,
	'event_owner' : 'NEUTRAL',
	'can_headline_card' : False,
	'usage_conditions' : [('IfHaveOpponentEventInHand', 0)],
	'event_effects' : [('ConductOperationsWithOpponentEventCard', 0)],
	'event_text' : 'Play this card simultaneously with a card containing your opponent\'s associated Event. The Event is cancelled, but you may use its Operations value to Conduct Operations. The cancelled event returns to the discard pile. May not be played during headline phase.',
}


De_Stalinization = {
	'card_name' : 'De_Stalinization',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 33,
	'operations_points' : 3,
	'event_owner' : 'USSR',
	'event_effects' : [('RelocateInfluenceToUncontrolledCountriesMax2', 4)],
	'event_text' : 'USSR may relocate up to 4 Influence points to non-US controlled countries. No more than 2 Influence may be placed in the same country.',
	'remove_if_used_as_event' : True,
}

Nuclear_Test_Ban = {
	'card_name' : 'Nuclear_Test_Ban',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 34,
	'operations_points' : 4,
	'event_owner' : 'NEUTRAL',
	'event_effects' : [('GainVictoryPointsForDEFCONMinus', 2), ('ImproveDEFCONLevel', 2)],
	'event_text' : 'Player earns VPs equal to the current DEFCON level minus 2, then improve DEFCON two levels.',
}

Formosan_Resolution = {
	'card_name' : 'Formosan_Resolution',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 35,
	'operations_points' : 2,
	'event_owner' : 'USA',
	'event_effects' : [('PutThisCardInPlay', 0)],
	'continuous_effects' : [('TaiwanIsBattlegroundForScoringIfUSControlled', 0)],
	'triggered_effects' : [('WhenUSPlaysChinaCardTriggerRemoveThisCardFromPlay', 0)],
	'event_text' : 'Taiwan shall be treated as a Battleground country for scoring purposes, if the US controls Taiwan when the Asia Scoring Card is played or during Final Scoring at the end of Turn 10. Taiwan is not a battleground country for any other game purpose. This card is discarded after US play of \'The China Card\'.',
	'remove_if_used_as_event' : True,
}

Defectors = {
	'card_name' : 'Defectors',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 103,
	'operations_points' : 2,
	'event_owner' : 'USA',
	'resolve_headline_first' : True,
	'event_effects' : [('CancelPlayerHeadlineIfIsHeadlinePhase', 0), ('GainVictoryPointsIfIsOpponentActionRound', 1)],
	'event_text' : 'Play in Headline Phase to cancel USSR Headline event, including Scoring Card. Cancelled card returns to the Discard Pile.\nIf Defectors played by USSR during Soviet action round, US gains 1 VP (unless played on the Space Race).',
}


# -- OPTIONAL
The_Cambridge_Five = {
	'card_name' : 'The_Cambridge_Five',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 104,
	'optional_card' : True,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'usage_conditions' : [('IfTurnNumberLessThan', 7)],
	'event_effects' : [('CommitPlayerDecision', 0), ('OpponentRevealsScoringCardsInHand', 0), ('AddInfluenceInOpponentScoringCardRegion', 1)],
	'event_text' : 'The US player exposes all scoring cards in their hand. The USSR player may then add 1 Influence in any single region named on one of those scoring cards (USSR choice). Cannot be played as an event in Late War.',
}

# -- OPTIONAL
Special_Relationship = {
	'card_name' : 'Special_Relationship',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 105,
	'optional_card' : True,
	'operations_points' : 2,
	'event_owner' : 'USA',
	'event_effects' : [('AddInfluenceToOneWesternEuropeCountryIfControlUKAndNATO', 2), ('GainVictoryPointsIfControlUKAndNATO', 2), ('AddInfluenceAdjacentToUKIfControlUKButNoNATO', 1)],
	'event_text' : 'If UK is US controlled but NATO is not in effect, US adds 1 Influence to any country adjacent to the UK.\nIf UK is US controlled and NATO is in effect, US adds 2 Influence to any Western European country and gains 2 VPs.',
}


# -- OPTIONAL
NORAD = {
	'card_name' : 'NORAD',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 106,
	'optional_card' : True,
	'operations_points' : 3,
	'event_owner' : 'USA',
	'event_effects' : [('PutThisCardInPlay', 0)],
	'triggered_effects' : [('IfDefconDroppedTo2AtEndOfActionRoundIfYouControlCanadaTriggerAddInfluenceToExisting', 1)],
	'event_text' : 'If the US controls Canada, the US may add 1 Influence to any country already containing US Influence at the conclusion of any Action Round in which the DEFCON marker moves to the \'2\' box. This event cancelled by \'Quagmire\'.',
	'remove_if_used_as_event' : True,
}





# --
# -- MID WAR
# --
#
#
# Brush_War = {
# 	'card_name' : 'Brush_War',
# 	'card_type' : 'Event',
# 	'stage' : 'Mid War',
# 	'card_number' : 36,
# 	'operations_points' : 3,
# 	'event_owner' : 'NEUTRAL',
# 	'event_effects' : {
# 		{ 'BrushWarInStabilityLowerThan2', 1 + (3 * 256),
# 	},
# 	'event_text' : 'Attack any country with a stability of 1 or 2. Roll a die and subtract 1 for every adjacent enemy controlled country. Success on 3-6. Player adds 3 to his Military Ops Track.\nEffects of Victory: Player gains 1 VP and replaces all opponent's Influence with his Influence.',
# }



Central_America_Scoring = {
	'card_name' : 'Central_America_Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Mid War',
	'card_number' : 37,
	'scoring_region' : 'Central America',
	'event_effects' : [('ScoreCentralAmerica', 0)],
	'event_text' : 'Both sides score: Presence: 1, Domination: 3, Control: 5, +1 per controlled Battleground Country in Region, +1 per Country controlled that is adjacent to enemy superpower',
	'may_be_held' : False,
}


Southeast_Asia_Scoring = {
	'card_name' : 'Southeast_Asia_Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Mid War',
	'card_number' : 38,
	'may_be_held' : False,
	'scoring_region' : 'Southeast Asia',
	'event_effects' : [('ScoreSoutheastAsia', 0)],
	'event_text' : 'Both sides score: 1 VP each for Control of: Burma, Cambodia/Laos, Vietnam, Malaysia, Indonesia, the Phillipines, 2 VP for Control of Thailand',
	'remove_if_used_as_event' : True,
}

''''
Arms_Race = {
	'card_name' : 'Arms_Race',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 39,

	'operations_points' : 3,

	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'GainVictoryPoints', 1, condition={'IfHasMoreMilOpsAndNotRequired',0},
		{ 'GainVictoryPoints', 3, condition={'IfHasMoreMilOpsAndRequired',0},
	},
	'event_text' : 'Compare each player's status on the Military Operations Track. If Phasing Player has more Military Operations points, he scores 1 VP. If Phasing Player has more Military Operations points and has met the Required Military Operations amount, he scores 3 VP instead.',
}

Cuban_Missile_Crisis = {
	'card_name' : 'Cuban_Missile_Crisis',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 40,

	'operations_points' : 3,

	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'SetDEFCONLevel', 2,
		{ 'PutThisCardInPlay', 1,
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'AtEndOfTurn', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
	},

	cardinplay_abilities = {
		{
			ability_name = 'Remove 2 Influence from Cuba',
			description = 'Remove 2 Influence from Cuba',
			conditions = {
				{ 'IfPlayerIsUSSR', 0,
				{ 'IfPlayerHasInfluenceInCuba', 2,
			},
			{ 'RemoveInfluenceInCuba', 2,

			{ 'RemoveThisCardFromPlay', 1,
		},
		{
			ability_name = 'Remove 2 Influence from West Germany',
			description = 'Remove 2 Influence from West Germany',
			conditions = {
				{ 'IfPlayerIsUS', 0,
				{ 'IfPlayerHasInfluenceInWestGermany', 2,
			},
			{ 'RemoveInfluenceInWestGermany', 2,

			{ 'RemoveThisCardFromPlay', 1,
		},
		{
			ability_name = 'Remove 2 Influence from Turkey',
			description = 'Remove 2 Influence from Turkey',
			conditions = {
				{ 'IfPlayerIsUS', 0,
				{ 'IfPlayerHasInfluenceInTurkey', 2,
			},
			{ 'RemoveInfluenceInTurkey', 2,

			{ 'RemoveThisCardFromPlay', 1,
		},
	},


	'event_text' : 'Set DEFCON to Level 2. Any further Coup attempt by your opponent this turn, anywhere on the board, will result in Global Thermonuclear War. Your opponent will lose the game. This event may be cancelled at any time if the USSR player removes two Influence from Cuba or the US player removes 2 Influence from either West Germany or Turkey.',
	'remove_if_used_as_event' : True,
}


Nuclear_Subs = {
	'card_name' : 'Nuclear_Subs',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 41,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'PutThisCardInPlay', 1,
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'AtEndOfTurn', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
	},
	'event_text' : 'US Coup attempts in Battleground Countries do not affect the DEFCON track for the remainder of the turn (does not affect Cuban Missile Crisis).',
	'remove_if_used_as_event' : True,
}


Quagmire = {
	'card_name' : 'Quagmire',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 42,

	'operations_points' : 3,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'PutOpponentIntoQuagmire', 0,
		{ 'RemoveNORADFromPlay', 0,
	},
	'event_text' : 'On next action round, US player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each US player Action round until successful or no appropriate cards remain. If out of appropriate cards, the US player may only play scoring cards until the next turn.',
	'remove_if_used_as_event' : True,
}


Salt_Negotiations = {
	'card_name' : 'Salt_Negotiations',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 43,

	'operations_points' : 3,

	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'ImproveDEFCONLevel', 2,
		{ 'RecoverEventCardFromDiscardPile', 1,
		{ 'PutThisCardInPlay', 1,
	},
	'continuous_effects' : {
		{
			effect = { 'ReduceAllCoupAttempts', 1,
		},
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'AtEndOfTurn', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
	},
	'event_text' : 'Improve DEFCON two levels.\nFurther Coup attempts incur -1 die roll modifier for both players for the remainder of the turn.\nPlayer may sort through discard pile and reclaim one non-scoring card, after revealing it to their opponent.',
	'remove_if_used_as_event' : True,
}


Bear_Trap = {
	'card_name' : 'Bear_Trap',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 44,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'PutOpponentIntoBearTrap', 0,
	},
	'event_text' : 'On next action round, USSR player must discard an Operations card worth 2 or more and roll 1-4 to cancel this event. Repeat each USSR player Action Round until successful or no appropriate cards remain. If out of appropriate cards, the USSR player may only play scoring cards until the next turn.',
	'remove_if_used_as_event' : True,
}


Summit = {
	'card_name' : 'Summit',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 45,

	'operations_points' : 1,

	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'CommitPlayerDecision', 0,
		{ 'ResolveSummit', 2,
	},
	'event_text' : 'Both players roll a die.  Each adds 1 for each Region they Dominate or Control. High roller gains 2 VP and may move DEFCON marker one level in either direction. o not reroll ties.',
}


How_I_Learned_to_Stop_Worrying = {
	'card_name' : 'How_I_Learned_to_Stop_Worrying',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 46,

	'operations_points' : 2,

	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'ChooseDEFCONLevel', 0,
		{ 'GainMilitaryOperationsTrack', 5,
	},
	'event_text' : 'Set the DEFCON at any level you want (1-5). This event counts as 5 Military Operations for the purpose of required Military Operations.',
	'remove_if_used_as_event' : True,
}


Junta = {
	'card_name' : 'Junta',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 47,

	'operations_points' : 2,


	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'AddInfluenceToOneCentralOrSouthAmericaCountry', 2,
		{ 'MakeFreeCoupOrRealignmentsInCentralOrSouthAmerica', 2,
	},
	'event_text' : 'Place 2 Influence in any one Central or South American country.\nThen you may make a free Coup attempt or Realignment roll in one of these regions (using this card's Operations Value).',
}


Kitchen_Debates = {
	'card_name' : 'Kitchen_Debates',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 48,

	'operations_points' : 1,

	'event_owner' : 'USA',
	'event_effects' : {
		usageconditions = {
			{ 'IfYouControlMoreBattlegrounds', 0,
		},
		{ 'GainVictoryPoints', 2,
	},
	'event_text' : 'If the US controls more Battleground countries than the USSR, poke opponent in chest and gain 2 VP!',
	'remove_if_used_as_event' : True,
}


Missile_Envy = {
	'card_name' : 'Missile_Envy',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 49,

	'operations_points' : 2,

	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'RemoveThisCardFromDiscardPile', 0,
		{ 'ResolveMissileEnvy', 0,		-- will
		{ 'DoNotDiscardThisCard', 0,
	},
	'event_text' : 'Exchange this card for your opponent's highest valued Operations card in his hand. If two or more cards are tied, opponent chooses.\nIf the exchanged card contains your event, or an event applicable to both players, it occurs immediately. If it contains opponent's event, use Operations value without triggering event. Opponent must use this card for Operations during his next action round.',
}


We_Will_Bury_You = {
	'card_name' : 'We_Will_Bury_You',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 50,

	'operations_points' : 4,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'DegradeDEFCONLevel', 1,
		{ 'PutThisCardInPlay', 1,
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'AtStartOfOpponentActionRound', 0,
			},
			triggereffect = {
				{ 'TriggerIncrementEffectData', 0,
			},
		},
		{
			conditions = {
				{ 'WhenOpponentPlaysUNInterventionAsEvent', 0,
				{ 'IfEffectDataIsNotZero', 0,
				{ 'IfEffectDataIsZero', 1,
			},
			triggereffect = {
				{ 'TriggerIncrementEffectData', 1,
			},
		},
		{
			conditions = {
				{ 'WhenOpponentPlaysNotUNInterventionAsEvent', 0,
				{ 'IfEffectDataIsNotZero', 0,
				{ 'IfEffectDataIsZero', 1,
			},
			triggereffect = {
				{ 'TriggerAnnounceCardInPlay', 0,
				{ 'TriggerGainVictoryPoints', 3,
				{ 'TriggerIncrementEffectData', 1,
			},
		},
		{
			conditions = {
				{ 'AtEndOfActionRound', 0,
				{ 'IfEffectDataIsNotZero', 0,
				{ 'IfEffectDataIsZero', 1,
			},
			triggereffect = {
				{ 'TriggerAnnounceCardInPlay', 0,
				{ 'TriggerGainVictoryPoints', 3,
				{ 'TriggerIncrementEffectData', 1,
			},
		},
		{
			conditions = {
				{ 'AtEndOfActionRound', 0,
				{ 'IfEffectDataIsNotZero', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 0,
			},
		},
	},
	'event_text' : 'Unless UN Invervention is played as an Event on the US player's next round, USSR gains 3 VP prior to any US VP award.\nDegrade DEFCON one level.',
	'remove_if_used_as_event' : True,
}


Brezhnev_Doctrine = {
	'card_name' : 'Brezhnev_Doctrine',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 51,

	'operations_points' : 3,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'PutThisCardInPlay', 1,
	},
	'continuous_effects' : {
		{
			effect = { 'IncreaseOperationsPointsForYourCards', 1,
		},
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'AtEndOfTurn', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
	},
	'event_text' : 'All further Operations cards played by the USSR this turn increase their Ops value by one (to a maximum of 4).',
	'remove_if_used_as_event' : True,
}


Portuguese_Empire_Crumbles = {
	'card_name' : 'Portuguese_Empire_Crumbles',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 52,

	'operations_points' : 2,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'GainInfluenceInSEAfricanStates', 2,
		{ 'GainInfluenceInAngola', 2,
	},
	'event_text' : 'Add 2 USSR Influence in both SE African States and Angola.',
	'remove_if_used_as_event' : True,
}


South_African_Unrest = {
	'card_name' : 'South_African_Unrest',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 53,

	'operations_points' : 2,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'ChooseFromEffectList',
			{
				prompt = 'Choose for South Africa:',
				{
					{ 'GainInfluenceInSouthAfrica', 2,

					description = 'Gain 2 Influence in South Africa',
				},
				{
					{ 'GainInfluenceInSouthAfrica', 1,
					{ 'AddInfluenceAdjacentToSouthAfrica', 2,

					description = 'Add Influence Adjacent to South Africa',
				},
			}
		},
	},
	'event_text' : 'USSR either adds 2 Influence in South Africa or adds 1 Influence in South Africa and 2 Influence in any countries adjacent to South Africa.',
}


Allende = {
	'card_name' : 'Allende',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 54,

	'operations_points' : 1,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'GainInfluenceInChile', 2,
	},
	'event_text' : 'USSR receives 2 Influence in Chile.',
	'remove_if_used_as_event' : True,
}


Willy_Brandt = {
	'card_name' : 'Willy_Brandt',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 55,

	'operations_points' : 2,

	'event_owner' : 'USSR',
	'event_effects' : {
		usageconditions = {
			{ 'IfHasNotBeenPlayedTearDownThisWall', 0,
		},
		{ 'GainVictoryPoints', 1,
		{ 'GainInfluenceInWestGermany', 1,
		{ 'PutThisCardInPlay', 0,
	},
	'event_text' : 'USSR receives gains 1 VP.\nUSSR receives 1 Influence in West Germany.\nCancels NATO for West Germany.\nThis event unplayable and/or cancelled by Tear Down This Wall.',
	'remove_if_used_as_event' : True,
}


Muslim_Revolution = {
	'card_name' : 'Muslim_Revolution',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 56,

	'operations_points' : 4,

	'event_owner' : 'USSR',
	'event_effects' : {
		usageconditions = {
			{ 'IfHasNotBeenPlayedAWACSSaleToSaudis', 0,
		},
		{ 'RemoveAllOpponentInfluenceForMuslimRevolution', 2,
	},
	'event_text' : 'Remove all US Influence in two of the following countries: Sudan, Iran, Iraq, Egypt, Libya, Saudi Arabia, Syria, Jordan.',
}


ABM_Treaty = {
	'card_name' : 'ABM_Treaty',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 57,

	'operations_points' : 4,

	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'ImproveDEFCONLevel', 1,
		{ 'ConductOperationsWithThisCard', 4,
	},
	'event_text' : 'Improve DEFCON one level.\nThen player may Conduct Operations as if they played a 4 Ops card.',
}


Cultural_Revolution = {
	'card_name' : 'Cultural_Revolution',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 58,

	'operations_points' : 3,

	'event_owner' : 'USSR',
	'event_effects' : {
		usageconditions = {
			{ 'NotIfChinaCardIsUnclaimedAndIsUSSR', 0,
		},
		{ 'GainVictoryPoints', 1, condition={'IfYouHaveChinaCard',0},
		{ 'ClaimChinaCard', 0, condition={'IfYouDoNotHaveChinaCard',0},
	},
	'event_text' : 'If the US has \'The China Card\', claim it face up and available for play. If the USSR already had it, USSR gains 1 VP.',
	'remove_if_used_as_event' : True,
}


Flower_Power = {
	'card_name' : 'Flower_Power',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 59,

	'operations_points' : 4,

	'event_owner' : 'USSR',
	'event_effects' : {
		usageconditions = {
			{ 'IfHasNotBeenPlayedAnEvilEmpire', 0,
		},
		{ 'PutThisCardInPlay', 0,
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'WhenOpponentPlaysWarCard', 0,
			},
			triggereffect = {
				{ 'TriggerAnnounceCardInPlay', 0,
				{ 'TriggerGainVictoryPoints', 2,
			},
		},
	},
	'event_text' : 'USSR gains 2 VP for every subsequently US played \'war card\' (played as an Event or Operations) unless played on the Space Race.\nWar Cards: Arab-Israeli War, Korean War, Brush War, Indo-Pakistani War or Iran-Iraq War.\nThis event cancelled by \'An Evil Empire\'.',
	'remove_if_used_as_event' : True,
}


U2_Incident = {
	'card_name' : 'U2_Incident',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 60,

	'operations_points' : 3,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'GainVictoryPoints', 1,
		{ 'PutThisCardInPlay', 1,
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'WhenUNInventionIsPlayedAsEvent', 0,
			},
			triggereffect = {
				{ 'TriggerAnnounceCardInPlay', 0,
				{ 'TriggerGainVictoryPoints', 1,
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
		{
			conditions = {
				{ 'AtEndOfTurn', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
	},
	'event_text' : 'USSR gains 1VP.\nIf UN Intervention played later this turn as an Event, either by US or USSR, gain 1 additional VP.',
	'remove_if_used_as_event' : True,
}


OPEC = {
	'card_name' : 'OPEC',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 61,

	'operations_points' : 3,

	'event_owner' : 'USSR',
	'event_effects' : {
		usageconditions = {
			{ 'IfHasNotBeenPlayedNorthSeaOil', 0,
		},
		{ 'GainVPForOPEC', 1,
	},
	'event_text' : 'USSR gains 1VP for each of the following countries he controls:\nEgypt, Iran, Libya, Saudi Arabia, Iraq, Gulf States, and Venezuela.\nUnplayable as an event if \'North Sea Oil\' is in effect.',
}


Lone_Gunman = {
	'card_name' : 'Lone_Gunman',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 62,

	'operations_points' : 1,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'CommitPlayerDecision', 0,
		{ 'OpponentRevealsHand', 0,
		{ 'ConductOperationsWithThisCard', 1,
	},
	'event_text' : 'US player reveals his hand. Then the USSR may Conduct Operations as if they played a 1 Op card.',
	'remove_if_used_as_event' : True,
}


Colonial_Rear_Guards = {
	'card_name' : 'Colonial_Rear_Guards',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 63,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'AddInfluenceInAfricaOrSEAsiaMax1', 4,
	},
	'event_text' : 'Add 1 US Influence in each of four different African and/or Southeast Asian countries.',
}


Panama_Canal_Returned = {
	'card_name' : 'Panama_Canal_Returned',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 64,

	'operations_points' : 1,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'GainInfluenceInPanama', 1,
		{ 'GainInfluenceInCostaRica', 1,
		{ 'GainInfluenceInVenezuela', 1,
	},
	'event_text' : 'Add 1 US Influence in Panama, Costa Rica, and Venezuela.',
	'remove_if_used_as_event' : True,
}


Camp_David_Accords = {
	'card_name' : 'Camp_David_Accords',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 65,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'GainVictoryPoints', 1,
		{ 'GainInfluenceInIsrael', 1,
		{ 'GainInfluenceInJordan', 1,
		{ 'GainInfluenceInEgypt', 1,
		{ 'PutThisCardInPlay', 0,
	},
	'event_text' : 'US gains 1 VP.\nUS receives 1 Influence in Israel, Jordan and Egypt.\nArab-Israeli War event no longer playable.',
	'remove_if_used_as_event' : True,
}


Puppet_Governments = {
	'card_name' : 'Puppet_Governments',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 66,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'AddInfluenceInEmptyCountriesMax1', 3,
	},
	'event_text' : 'US may add 1 Influence in three countries that currently contain no Influence from either power.',
	'remove_if_used_as_event' : True,
}


Grain_Sales_to_Soviets = {
	'card_name' : 'Grain_Sales_to_Soviets',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 67,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'CommitPlayerDecision', 0,
		{ 'MayPlayRandomCardFromOpponentHand', 0,
		{ 'ConductOperationsWithThisCard', 2, condition={'IfYouDoNot',2},
	},
	'event_text' : 'Randomly choose one card from USSR hand. Play it or return it. If Soviet player has no cards, or returned, use this card to conduct Operations normally.',
}


John_Paul_II_Elected_Pope = {
	'card_name' : 'John_Paul_II_Elected_Pope',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 68,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'RemoveOpponentInfluenceInPoland', 2,
		{ 'GainInfluenceInPoland', 1,
		{ 'PutThisCardInPlay', 0,
	},
	'event_text' : 'Remove 2 USSR Influence in Poland and then add 1 US Influence in Poland.\nAllows play of \'Solidarity\'.',
	'remove_if_used_as_event' : True,
}

Latin_American_Death_Squads = {
	'card_name' : 'Latin_American_Death_Squads',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 69,

	'operations_points' : 2,

	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'PutThisCardInPlay', 1,
	},
	'continuous_effects' : {
		{
			effect = { 'AdjustCoupAttemptsInCentralAndSouthAmerica', 1,
		},
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'AtEndOfTurn', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
	},
	'event_text' : 'All of the player's Coup attempts in Central and South America are +1 for the remainder of the turn, while all opponent's Coup attempts are -1 for the remainder of the turn.',
}

OAS_Founded = {
	'card_name' : 'OAS_Founded',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 70,

	'operations_points' : 1,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'AddInfluenceInCentralAmericaOrSouthAmerica', 2,
	},
	'event_text' : 'Add 2 US Influence in Central America and/or South America.',
	'remove_if_used_as_event' : True,
}


Nixon_Plays_The_China_Card = {
	'card_name' : 'Nixon_Plays_The_China_Card',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 71,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'GainVictoryPoints', 2, condition={'IfYouHaveChinaCard',0},
		{ 'ClaimChinaCard', 1, condition={'IfYouDoNotHaveChinaCard',0},
	},
	'event_text' : 'If US has \'The China Card\', gain 2 VP. Otherwise, US player receives \'The China Card\' now, face down and unavailable for immediate play.',
	'remove_if_used_as_event' : True,
}


Sadat_Expels_Soviets = {
	'card_name' : 'Sadat_Expels_Soviets',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 72,

	'operations_points' : 1,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'RemoveAllOpponentInfluenceInEgpyt', 0,
		{ 'GainInfluenceInEgypt', 1,
	},
	'event_text' : 'Remove all USSR Influence in Egypt and add one US Influence.',
	'remove_if_used_as_event' : True,
}


Shuttle_Diplomacy = {
	'card_name' : 'Shuttle_Diplomacy',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 73,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'RemoveThisCardFromDiscardPile', 0,
		{ 'PutThisCardInPlaySpecial', 0,
		{ 'DoNotDiscardThisCard', 0,
	},
	'continuous_effects' : {
		{
			effect = { 'OpponentIgnoresBattlegroundInAsiaOrMiddleEast', 1,
		},
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'WhenScoringAsiaOrMiddleEast', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlayAndDiscard', 1,
			},
		},
	},
	'event_text' : 'Play in front of US player. During the next scoring of the Middle East or Asia (whichever comes first), subtract one Battleground country from USSR total, then put this card in the discard pile. Does not count for Final Scoring at the end of Turn 10.',
}


The_Voice_Of_America = {
	'card_name' : 'The_Voice_Of_America',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 74,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'RemoveOpponentInfluenceFromNonEuropeMax2', 4,
	},
	'event_text' : 'Remove 4 USSR Influence from non-European countries. No more than 2 may be removed from any one country.',
}


Liberation_Theology = {
	'card_name' : 'Liberation_Theology',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 75,

	'operations_points' : 2,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'AddInfluenceInCentralAmericaMax2', 3,
	},
	'event_text' : 'Add 3 USSR Influence in Central America, no more than 2 per country.',
}


Ussuri_River_Skirmish = {
	'card_name' : 'Ussuri_River_Skirmish',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 76,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'AddInfluenceInAsiaMax2', 4, condition={'IfYouHaveChinaCard',0},
		{ 'ClaimChinaCard', 0, condition={'IfYouDoNotHaveChinaCard',0},
	},
	'event_text' : 'If the USSR has \'The China Card\', claim it face up and available for play. If the US already has \'The China Card\', add 4 US Influence in Asia, no more than 2 per country.',
	'remove_if_used_as_event' : True,
}


Ask_Not_What_Your_Country_Can_Do_For_Y'card_name' : 'Ask_Not_What_Your_Country_Can_Do_For_Yard_type'_:_'Event',
	'stage' : 'Mid War',

	'card_number' : 77,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'MayDiscardEntireHand', 0,
		{ 'CommitPlayerDecision', 0,
		{ 'DrawCardForEachDiscard', 0,
	},
	'event_text' : 'US player may discard up to entire hand (including Scoring cards) and draw replacements from the deck. The number of cards discarded must be decided prior to drawing any replacements.',
	'remove_if_used_as_event' : True,
}


Alliance_for_Progress = {
	'card_name' : 'Alliance_for_Progress',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 78,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'GainVPForAllianceForProgress', 1,
	},
	'event_text' : 'US gains 1 VP for each US controlled Battleground country in Central America and South America.',
	'remove_if_used_as_event' : True,
}

'''
Africa_Scoring = {
	'card_name' : 'Africa_Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Mid War',
	'card_number' : 79,
	'scoring_region' : 'Africa',
	'event_effects' : [('ScoreAfrica', 0)],
	'event_text' : 'Both sides score: Presence: 1, Domination: 4, Control: 6, +1 per controlled Battleground Country in Region',

	'may_be_held' : False,
}
''''

One_Small_Step = {
	'card_type' : 'Event',
	'stage' : 'Mid War',
	'card_number' : 80,
	'operations_points' : 2,
	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		usageconditions = {
			{ 'IfYouAreBehindOnSpaceRaceTrack', 0,
		},
		{ 'AdvanceSpaceRaceTrack', 2,
	},

	'event_text' : 'If you are behind on the Space Race Track, play this card to move your marker two boxes forward on the Space Rack Track, gaining the VP value of the second box only.',
}
'''

South_America_Scoring = {
	'card_name' : 'South_America_Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Mid War',
	'card_number' : 81,
	'scoring_region' : 'South America',
	'event_effects' : [('ScoreSouthAmerica', 0)],
	'event_text' : 'Both sides score: Presence: 2, Domination: 5, Control: 6, +1 per controlled Battleground Country in Region',
	'may_be_held' : False,
}

''''
# -- OPTIONAL
Che = {
	'card_name' : 'Che',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 107,
	'optional_card' : True,

	'operations_points' : 3,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'MakeCoupAttemptInNonBattlegroundInAmericasOrAfrica', 3,
		{ 'MakeCoupAttemptInNonBattlegroundInAmericasOrAfrica', 3, condition={'IfYouDo',0},,
	},
	'event_text' : 'USSR may immediately make a Coup attempt using this card's Operations value against a non-battleground country in Central America, South America, or Africa. If the Coup removes any US Influence, USSR may make a second Coup attempt against a different target under the same restrictions.',
}


# -- OPTIONAL
Our_Man_In_Tehran = {
	'card_name' : 'Our_Man_In_Tehran',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 108,
	'optional_card' : True,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		usageconditions = {
			{ 'IfYouControlMiddleEastCountry', 1,
		},
		{ 'CommitPlayerDecision', 0,
		{ 'MayDiscardTopOfDrawPile', 5,
	},
	'event_text' : 'If the US controls at least one Middle East country, the US player draws the top 5 cards from the draw pile. They may reveal and then discard any or all of these drawn cards without triggering the Event. Any remaining drawn cards are returned to the draw deck, and it is reshuffled.',
	'remove_if_used_as_event' : True,
}










--
-- LATE WAR
--



Iranian_Hostage_Crisis = {
	'card_name' : 'Iranian_Hostage_Crisis',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 82,
	'operations_points' : 3,
	'event_owner' : 'USSR',
	'event_effects' : [('RemoveAllOpponentInfluenceInIran', 0), ('GainInfluenceInIran', 2), ('PutThisCardInPlay', 0)],
	'event_text' : 'Remove all US Influence in Iran. Add 2 USSR Influence in Iran.\nDoubles the effect of Terrorism card against US.',
	'remove_if_used_as_event' : True,
}


The_Iron_Lady = {
	'card_name' : 'The_Iron_Lady',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 83,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'GainVictoryPoints', 1,
		{ 'OpponentGainsInfluenceInArgentina', 1,
		{ 'RemoveAllOpponentInfluenceInUK', 0,
		{ 'PutThisCardInPlay', 0,
	},
	'event_text' : 'US gains 1 VP.\nAdd 1 USSR Influence in Argentina. Remove all USSR Influence from UK.\nSocialist Governments event no longer playable.',
	'remove_if_used_as_event' : True,
}


Reagan_Bombs_Libya = {
	'card_name' : 'Reagan_Bombs_Libya',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 84,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'GainVPForOpponentInfluenceInLibya', 2,
	},
	'event_text' : 'US gains 1 VP for every 2 USSR Influence in Libya.',
	'remove_if_used_as_event' : True,
}


Star_Wars = {
	'card_name' : 'Star_Wars',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 85,

	'operations_points' : 2,

	'event_owner' : 'USA',
	'event_effects' : {
		usageconditions = {
			{ 'IfUSIsAheadOnSpaceRaceTrack', 0,
		},
		{ 'CopyEventCardFromDiscardPile', 0,		-- will
	},
	'event_text' : 'If the US is ahead on the Space Race Track, play this card to search through the discard pile for a non-scoring card of your choice. Event occurs immediately.',
	'remove_if_used_as_event' : True,
}


North_Sea_Oil = {
	'card_name' : 'North_Sea_Oil',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 86,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'SetActionRoundCount', 8,
		{ 'PutThisCardInPlay', 0,
	},
	'event_text' : 'OPEC event is no longer playable.\nUS may play 8 cards this turn.',
	'remove_if_used_as_event' : True,
}


The_Reformer = {
	'card_name' : 'The_Reformer',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 87,

	'operations_points' : 3,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'AddInfluenceInEuropeMax2', 6, condition={'IfYouAreAheadOnVPTrack',0},
		{ 'AddInfluenceInEuropeMax2', 4, condition={'IfYouAreNotAheadOnVPTrack',0},
		{ 'PutThisCardInPlay', 0, condition={'IfGlasnostIsNotInRemovedPile',0},
	},
	'continuous_effects' : {
		{
			effect = { 'YouCannotCoupInEurope', 0,
		},
	},
	'event_text' : 'Add 4 Influence in Europe (no more than 2 per country). If USSR is ahead of US in VP, then 6 Influence may be added instead.\nUSSR may no longer conduct Coup attempts in Europe.\nImproves effect of Glasnost event.',
	'remove_if_used_as_event' : True,
}


Marine_Barracks_Bombing = {
	'card_name' : 'Marine_Barracks_Bombing',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 88,

	'operations_points' : 2,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'RemoveAllOpponentInfluenceInLebanon', 0,
		{ 'RemoveOpponentInfluenceInMiddleEast', 2,
	},
	'event_text' : 'Remove all US Influence in Lebanon plus remove 2 additional US Influence from anywhere in the Middle East.',
	'remove_if_used_as_event' : True,
}


Soviets_Shoot_Down_KAL-007 = {
	'card_name' : 'Soviets_Shoot_Down_KAL_007',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 89,

	'operations_points' : 4,

	'event_owner' : 'USA',
	'event_effects' : [('DegradeDEFCONLevel', 1), ('GainVictoryPoints', 2), ('PlaceInfluenceOrAttemptRealignmentsWithThisCardIfYouControlSouthKorea', 4)],
	'event_text' : 'Degrade DEFCON one level. US gains 2 VP.\nIf South Korea is US Controlled, then the US may place Influence or attempt Realignment as if they played a 4 Ops card.',
	'remove_if_used_as_event' : True,
}

Glasnost = {
	'card_name' : 'Glasnost',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 90,
	'operations_points' : 4,
	'event_owner' : 'USSR',
	'event_effects' : [('GainVictoryPoints', 2), ('ImproveDEFCONLevel', 1), ('PlaceInfluenceOrAttemptRealignmentsWithThisCardIfHasBeenPlayedTheReformer', 4), ('RemoveTheReformerFromPlay', 0)],
	'event_text' : 'USSR gains 2 VP.\nImprove DEFCON one level.\nIf The Reformer is in effect, then the USSR may place Influence or attempt Realignments as if they played a 4 Ops card.',
	'remove_if_used_as_event' : True,
}

Ortega_Elected_in_Nicaragua = {
	'card_name' : 'Ortega_Elected_in_Nicaragua',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 91,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'event_effects' : [('RemoveAllOpponentInfluenceInNicaragua', 0), ('MakeFreeCoupAttemptAdjacentToNicaragua', 0)],
	'event_text' : 'Remove all US Influence from Nicaragua. Then USSR may make one free Coup attempt (with this card's Operations value) in a country adjacent to Nicaragua.',
	'remove_if_used_as_event' : True,
}

Terrorism = {
	'card_name' : 'Terrorism',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 92,
	'operations_points' : 2,
	'event_owner' : 'NEUTRAL',
	'event_effects' : [('CommitPlayerDecision', 0), ('OpponentDiscardsRandomCard', 0), ('OpponentDiscardsRandomCardIfUSSRAndHasBeenPlayedIranianHostageCrisis', 0)],
	'event_text' : 'Opponent must randomly discard one card. If played by USSR and Iranian Hostage Crisis is in effect, the US player must randomly discard two cards.\n(Events on discards do not occur.)',
}

Iran-Contra_Scandal = {
	'card_name' : 'Iran_Contra_Scandal',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 93,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'PutThisCardInPlay', 1,
	},
	'continuous_effects' : {
		{
			effect = { 'OpponentRealignmentRollsAreReducedBy', 1,
		},
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'AtEndOfTurn', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
	},
	'event_text' : 'All US Realignment rolls have a -1 die roll modifier for the remainder of the turn.',
	'remove_if_used_as_event' : True,
}


Chernobyl = {
	'card_name' : 'Chernobyl',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 94,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'ChooseOneRegion', 0,
		{ 'PutThisCardInPlayWithRegionChoice', 0,
	},
	'continuous_effects' : {
		{
			effect = { 'OpponentMayNotPlaceInfluenceInSelectedRegion', 0,
		},
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'AtEndOfTurn', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
	},
	'event_text' : 'The US player may designate one Region. For the remainder of the turn the USSR may not add additional Influence to that Region by the play of Operations Points via placing Influence.',
	'remove_if_used_as_event' : True,
}

Latin_American_Debt_Crisis = {
	'card_name' : 'Latin_American_Debt_Crisis',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 95,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'OpponentMayDiscardCardWithOpsPoints', 3,
		{ 'DoubleInfluenceInSouthAmericanCountries', 2, condition={'IfYouDoNot',0},,
	},
	'event_text' : 'Unless the US Player immediately discards a \'3\' or greater Operations card, double USSR Influence in two countries in South America.',
	'remove_if_used_as_event' : True,
}


Tear_Down_This_Wall = {
	'card_name' : 'Tear_Down_This_Wall',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 96,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'RemoveWillyBrandtFromPlay', 0,
		{ 'GainInfluenceInEastGermany', 3,
		{ 'MakeFreeCoupOrRealignmentAttemptsInEurope', 0,
		{ 'PutThisCardInPlay', 0, condition={'IfWillyBrandtIsNotInRemovedPile',0},
	},
	'event_text' : 'Cancels/prevent Willy Brandt.\nAdd 3 US Influence in East Germany.\nThen US may make a free Coup attempt or Realignment rolls in Europe using this card's Ops Value.',
	'remove_if_used_as_event' : True,
}


An_Evil_Empire = {
	'card_name' : 'An_Evil_Empire',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 97,

	'operations_points' : 3,

	'event_owner' : 'USA',
	'event_effects' : {
		{ 'RemoveFlowerPowerFromPlay', 0,
		{ 'GainVictoryPoints', 1,
		{ 'PutThisCardInPlay', 0, condition={'IfFlowerPowerIsNotInRemovedPile',0},
	},
	'event_text' : 'Cancels/Prevents Flower Power.\nUS gains 1 VP.',
	'remove_if_used_as_event' : True,
}


Aldrich_Ames_Remix = {
	'card_name' : 'Aldrich_Ames_Remix',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 98,

	'operations_points' : 3,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'CommitPlayerDecision', 0,
		--{ 'OpponentRevealsHand', 0,
		{ 'DiscardCardFromOpponentHand', 0,
	},
	'event_text' : 'US player exposes his hand to USSR player for remainder of turn. USSR then chooses one card from US hand, this card is discarded.',
	'remove_if_used_as_event' : True,
}

Pershing_II_Deployed = {
	'card_name' : 'Pershing_II_Deployed',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 99,

	'operations_points' : 3,

	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'GainVictoryPoints', 1,
		{ 'RemoveOpponentInfluenceInWesternEuropeMax1', 3,
	},
	'event_text' : 'USSR gains 1 VP.\nRemove 1 US Influence from up to three countries in Western Europe.',
	'remove_if_used_as_event' : True,
}


Wargames = {
	'card_name' : 'Wargames',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 100,
	'operations_points' : 4,
	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		usageconditions = {
			{ 'IfDefconLevelIs', 2,
		},
		{ 'ResolveWargames', 6,
	},
	'event_text' : 'If DEFCON Status 2, you may immediately end the game (without Final Scoring Phase) after giving opponent 6 VPs.\nHow about a nice game of chess?',
	'remove_if_used_as_event' : True,
}


Solidarity = {
	'card_name' : 'Solidarity',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 101,
	'operations_points' : 2,
	'event_owner' : 'USA',
	'event_effects' : {
		usageconditions = {
			{ 'IfHasBeenPlayedJohnPaulIIElectedPope', 0,
		},
		{ 'GainInfluenceInPoland', 3,
		{ 'RemoveJohnPaulIIElectedPopeFromPlay', 0,
	},
	'event_text' : 'Playable as an event only if John Paul II Elected Pope is in effect.\nAdd 3 US Influence in Poland.',
	'remove_if_used_as_event' : True,
}


Iran-Iraq_War = {
	'card_name' : 'Iran_Iraq_War',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 102,
	'operations_points' : 2,
	'event_owner' : 'NEUTRAL',
	'event_effects' : {
		{ 'WarInIranOrIraq', 2 + (2 * 256),
	},
	'event_text' : 'Iran or Iraq invades the other (player's choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to target of invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track\nEffects of Victory: Player gains 2 VP and replaces opponent's Influence in target country with his own.',
	'remove_if_used_as_event' : True,
}


# -- OPTIONAL
Yuri_and_Samantha = {
	'card_name' : 'Yuri_and_Samantha',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 109,
	'optional_card' : True,
	'operations_points' : 2,
	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'PutThisCardInPlay', 1,
	},
	'triggered_effects' : {
		{
			conditions = {
				{ 'WhenOpponentMakesCoupAttempt', 0,
			},
			triggereffect = {
				{ 'TriggerAnnounceCardInPlay', 0,
				{ 'TriggerGainVictoryPoints', 1,
			},
		},
		{
			conditions = {
				{ 'AtEndOfTurn', 0,
			},
			triggereffect = {
				{ 'TriggerRemoveThisCardFromPlay', 1,
			},
		},
	},
	'event_text' : 'USSR receives 1 VP for each US coup attempt made for the remainder of the current turn.',
	'remove_if_used_as_event' : True,
}


# -- OPTIONAL
AWACS_Sale_to_Saudis = {
	'card_name' : 'AWACS_Sale_to_Saudis',
	'card_type' : 'Event',
	'stage' : 'Late War',
	'card_number' : 110,
	'optional_card' : True,
	'operations_points' : 3,
	'event_owner' : 'USA',
	'event_effects' : {
		{ 'GainInfluenceInSaudiArabia', 2,
		{ 'PutThisCardInPlay', 0,
	},
	'event_text' : 'US receives 2 Influence in Saudi Arabia. Muslim Revolution may no longer be played as an event.',
	'remove_if_used_as_event' : True,
}

'''

'''Processes only early war cards'''
Arab_Israeli_War = CardInfo(**Arab_Israeli_War)
Asia_Scoring = CardInfo(**Asia_Scoring)
Blockade = CardInfo(**Blockade)
CIA_Created = CardInfo(**CIA_Created)
COMECON = CardInfo(**COMECON)
Captured_Nazi_Scientist = CardInfo(**Captured_Nazi_Scientist)
Containment = CardInfo(**Containment)
De_Gaulle_Leads_France = CardInfo(**De_Gaulle_Leads_France)
De_Stalinization = CardInfo(**De_Stalinization)
Decolonization = CardInfo(**Decolonization)
Defectors = CardInfo(**Defectors)
Duck_and_Cover = CardInfo(**Duck_and_Cover)
East_European_Unrest = CardInfo(**East_European_Unrest)
Europe_Scoring = CardInfo(**Europe_Scoring)
Fidel = CardInfo(**Fidel)
Five_Year_Plan = CardInfo(**Five_Year_Plan)
Formosan_Resolution = CardInfo(**Formosan_Resolution)
Independent_Reds = CardInfo(**Independent_Reds)
Indo_Pakistani_War = CardInfo(**Indo_Pakistani_War)
Korean_War = CardInfo(**Korean_War)
Marshall_Plan = CardInfo(**Marshall_Plan)
Middle_East_Scoring = CardInfo(**Middle_East_Scoring)
NATO = CardInfo(**NATO)
NORAD = CardInfo(**NORAD)
Nasser = CardInfo(**Nasser)
Nuclear_Test_Ban = CardInfo(**Nuclear_Test_Ban)
Olympic_Games = CardInfo(**Olympic_Games)
Red_Scare_Purge = CardInfo(**Red_Scare_Purge)
Romanian_Abdication = CardInfo(**Romanian_Abdication)
Socialist_Governments = CardInfo(**Socialist_Governments)
Special_Relationship = CardInfo(**Special_Relationship)
Suez_Crisis = CardInfo(**Suez_Crisis)
The_Cambridge_Five = CardInfo(**The_Cambridge_Five)
The_China_Card = CardInfo(**The_China_Card)
Truman_Doctrine = CardInfo(**Truman_Doctrine)
UN_Intervention = CardInfo(**UN_Intervention)
US_Japan_Mutual_Defense_Pact = CardInfo(**US_Japan_Mutual_Defense_Pact)
Vietnam_Revolts = CardInfo(**Vietnam_Revolts)
Warsaw_Pact_Formed = CardInfo(**Warsaw_Pact_Formed)

'''Mid war scoring cards'''
Central_America_Scoring = CardInfo(**Central_America_Scoring)
Southeast_Asia_Scoring = CardInfo(**Southeast_Asia_Scoring)
Africa_Scoring = CardInfo(**Africa_Scoring)
South_America_Scoring = CardInfo(**South_America_Scoring)
