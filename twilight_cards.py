# --
# -- EARLY WAR
# --

Asia_Scoring = {
	'card_name' : 'Asia Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Early War',
	'card_number' : 1,
	'scoring_region' : 'Asia',
	'event_effects' : [('ScoreAsia', 0)],
	'event_text' : 'Both sides score:\nPresence: 3\nDomination: 7\nControl: 9\n+1 per controlled Battleground Country in Region\n+1 per Country controlled that is adjacent to enemy superpower',
	'may_be_held' : False,
}

Europe_Scoring = {
	'card_name' : 'Europe Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Early War',
	'card_number' : 2,
	'scoring_region' : 'Europe',
	'event_effects' : [('ScoreEurope', 0)],
	'event_text' : 'Both sides score:\nPresence: 3\nDomination: 7\nControl: VICTORY\n+1 per controlled Battleground Country in Region\n+1 per Country controlled that is adjacent to enemy superpower',
	'may_be_held' : False,
}

Middle_East_Scoring = {
	'card_name' : 'Middle East Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Early War',
	'card_number' : 3,
	'scoring_region' : 'Middle East',
	'event_effects' : [('ScoreMiddleEast', 0)],
	'event_text' : 'Both sides score:\nPresence: 3\nDomination: 5\nControl: 7\n+1 per controlled Battleground Country in Region',
	'may_be_held' : False,
}

Duck_and_Cover = {
	'card_name' : 'Duck and Cover',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 4,
	'operations_points' : 3,
	'event_owner' : 'USA',
	'event_effects' : [('DegradeDEFCONLevel', 1), ('GainVictoryPointsForDEFCONBelow', 5)],
	'event_text' : 'Degrade DEFCON one level.\nThen US player earns VPs equal to 5 minus current DEFCON level.',
}

Five_Year_Plan = {
	'card_name' : 'Five-Year Plan',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 5,
	'operations_points' : 3,
	'event_owner' : 'USA',
	'event_effects' : [('CommitPlayerDecision', 0), ('OpponentDiscardsRandomCard', 1)],
	'event_text' : 'USSR player must randomly discard one card. If the card is a US associated Event, the Event occurs immediately. If the card is a USSR associated Event or and Event applicable to both players, then the card must be discarded without triggering the Event.',
}

The_China_Card = {
	'card_name' : 'The China Card',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 6,
	'operations_points' : 4,
	'event_owner' : 'Neutral',
	'can_headline_card' : False,
	'global_'continuous_effects'':: [('GainOperationsPointsWhenUsingThisCardInAsia', 1)],
	'event_text' : 'Begins the game with the USSR player.\n+1 Operations value when all points are used in Asia. Pass to opponent after play.\n+1 VP for the player holding this card at the end of Turn 10.\nCancels effect of \'Formosan Resolution\' if this card is played by the US player.',
}

Socialist_Governments = {
	'card_name' : 'Socialist Governments',
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
	'event_effects' : [('RemoveAllOpponentInfluenceInCuba', 0), ('GainInfluenceForControlInCuba', 0)],
	'event_text' : 'Remove all US Influence in Cuba. USSR gains sufficient Influence in Cuba for Control.',
	'remove_if_used_as_event' : True,
}

Vietnam_Revolts = {
	'card_name' : 'Vietnam Revolts',
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
	'card_name' : 'Korean War',
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
	'card_name' : 'Romanian Abdication',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 12,
	'operations_points' : 1,
	'event_owner' : 'USSR',
	'event_effects' : [('RemoveAllOpponentInfluenceInRomania', 0), ('GainInfluenceForControlInRomania', 0)],
	'event_text' : 'Remove all US Influence in Romania. USSR gains sufficient Influence in Romania for Control.',
	'remove_if_used_as_event' : True,
}


Arab_Israeli_War = {
	'card_name' : 'Arab-Israeli War',
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
	'event_effects' : [('GainInfluenceInEgypt', 2), ('RemoveHalfOpponentInfluenceInEgpyt', 0)],
	'event_text' : 'Add 2 USSR Influence in Egypt. Remove half (rounded up) of the US Influence in Egypt.',
	'remove_if_used_as_event' : True,
}

Warsaw_Pact_Formed = {
	'card_name' : 'Warsaw Pact Formed',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 16,
	'operations_points' : 3,
	'event_owner' : 'USSR',
	'event_effects' : {
		{ 'ChooseFromEffectList',
			{
				prompt = 'Choose for Eastern Europe:',
				{
					{ 'RemoveAllOpponentInfluenceFromEasternEurope', 4,

					description = 'Remove 4 US Countries in Eastern Europe',
				},
				{
					{ 'AddInfluenceInEasternEuropeMax2', 5,
					description = 'Add 5 USSR Influence in Eastern Europe',
				},
			}
		},
		{ 'PutThisCardInPlayOppOwner', 0, condition={'IfHasNotBeenPlayedNATO',0},
	},
	'event_text' : 'Remove all US Influence from four countries in Eastern Europe, or add 5 USSR Influence in Eastern Europe, adding no more than 2 per country. Allow play of NATO.',
	'remove_if_used_as_event' : True,
}

De_Gaulle_Leads_France = {
	'card_name' : 'De Gaulle Leads France',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 17,
	'operations_points' : 3,
	'event_owner' : 'USSR',
	'event_effects' : [('RemoveOpponentInfluenceInFrance', 2), ('GainInfluenceInFrance', 1), ('PutThisCardInPlay', 0)],
	'event_text' : 'Remove 2 US Influence in France, add 1 USSR Influence. Cancels effects of NATO for France.',
	'remove_if_used_as_event' : True,
}

Captured_Nazi_Scientist = {
	'card_name' : 'Captured Nazi Scientist',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 18,
	'operations_points' : 1,
	'event_owner' : 'Neutral',
	'event_effects' : [('AdvanceSpaceRaceTrack', 1)],
	'event_text' : 'Advance player's Space Race marker one box.',
	'remove_if_used_as_event' : True,
}

Truman_Doctrine = {
	'card_name' : 'Truman Doctrine',
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
	'card_name' : 'Olympic Games',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 20,
	'operations_points' : 2,
	'event_owner' : 'Neutral',
	'event_effects' : []'ResolveOlympicGames', 4)],
	'event_text' : 'Player sponsors Olympics. Opponent may participate or boycott. If Opponent participates, each player rolls one die, with the sponsor adding 2 to his roll. High roll gains 2 VP. Reroll ties If Opponent boycotts, degrade DEFCON one level and the Sponsor may Conduct Operations as if they played a 4 Ops card.',
}

NATO = {
	'card_name' : 'NATO',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 21,
	'operations_points' : 4,
	'event_owner' : 'USA',
	'usage_conditions': [('IfHasBeenPlayedMarshallPlanOrWarsawPact', 0)]
	'event_effects' : [('PutThisCardInPlay', 0), ('RemoveMarshallPlanFromPlay', 0), ('RemoveWarsawPactFormedFromPlay', 0)],
	'continuous_effects' : [('OpponentCannotCoupOrRealignInControlledEurope', 0)],
	'event_text' : 'Play after \'Marshall Plan\' or \'Warsaw Pact\'.\nUSSR player may no longer make Coup or Realignment rolls in any US Controlled countries in Europe. US Controlled countries in Europe may not be attacked by play of the Brush War event.',
	'remove_if_used_as_event' : True,
}

Independent_Reds = {
	'card_name' : 'Independent Reds',
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
	'card_name' : 'Marshall Plan',
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
	'card_name' : 'Indo-Pakistani War',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 24,
	'operations_points' : 2,
	'event_owner' : 'Neutral',
	'event_effects' : [('WarInIndiaOrPakistan', 0)],
	'event_text' : 'India or Pakistan invades the other (player's choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to the target of the invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track. Effects of Victory: Player gains 2 VP and replaces all opponent's Influence in target country with his Influence.',
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
	'card_name' : 'CIA Created',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 26,
	'operations_points' : 1,
	'event_owner' : 'USA',
	'event_effects' : [('CommitPlayerDecision', 0), ('OpponentRevealsHand', 0), ('ConductOperationsWithThisCard', 1),
	'event_text' : 'USSR reveals hand this turn.\nThen the US may Conduct Operations as if they played a 1 Op card.',
	'remove_if_used_as_event' : True,
}

US_Japan_Mutual_Defense_Pact = {
	'card_name' : 'US/Japan Mutual Defense Pact',
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
	'card_name' : 'Suez Crisis',
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
	'card_name' : 'East European Unrest',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 29,
	'operations_points' : 3,
	'event_owner' : 'USA',
	'event_effects' : [('Remove1OpponentInfluenceFromEasternEuropeCountriesIfTurnNumberLessThan7', 3), [('Remove2OpponentInfluenceFromEasternEuropeCountriesIfTurnNumberLessThan8', 3)],
	'event_text' : 'In Early or Mid War: Remove 1 USSR Influence from three countries in Eastern Europe.\nIn Late War: Remove 2 USSR Influence from three countries in Eastern Europe.',
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
	'card_name' : 'Red Scare/Purge',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 31,
	'operations_points' : 4,
	'event_owner' : 'Neutral',
	'event_effects' : [('PutThisCardInPlay', 1)],
	'continuous_effects' : [('DecreaseOperationsPointsForOpponentsCards', 1)],
	'triggered_effects' : [('AtEndOfTurnTriggerRemoveThisCardFromPlay', 0)],
	'event_text' : 'All further Operations cards played by your opponent this turn are -1 to their value (to a minimum of 1 Op).',
}

UN_Intervention = {
	'card_name' : 'UN Intervention',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 32,
	'operations_points' : 1,
	'event_owner' : 'Neutral',
	'can_headline_card' : False,
	'usage_conditions' : [('IfHaveOpponentEventInHand', 0)],
	'event_effects' : [('ConductOperationsWithOpponentEventCard', 0)],
	'event_text' : 'Play this card simultaneously with a card containing your opponent\'s associated Event. The Event is cancelled, but you may use its Operations value to Conduct Operations. The cancelled event returns to the discard pile. May not be played during headline phase.',
}


De_Stalinization = {
	'card_name' : 'De-Stalinization',
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
	'card_name' : 'Nuclear Test Ban',
	'card_type' : 'Event',
	'stage' : 'Early War',
	'card_number' : 34,
	'operations_points' : 4,
	'event_owner' : 'Neutral',
	'event_effects' : [('GainVictoryPointsForDEFCONMinus', 2), ('ImproveDEFCONLevel', 2)],
	'event_text' : 'Player earns VPs equal to the current DEFCON level minus 2, then improve DEFCON two levels.',
}

Formosan_Resolution = {
	'card_name' : 'Formosan Resolution',
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
	'card_name' : 'The Cambridge Five',
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
	'card_name' : 'Special Relationship',
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



'''

--
-- MID WAR
--


Brush_War = {
	'card_name' : 'Brush War',
	'card_type' : 'Event',
	'stage' : 'Mid War',
	'card_number' : 36,
	'operations_points' : 3,
	'event_owner' : 'Neutral',
	'event_effects' : {
		{ 'BrushWarInStabilityLowerThan2', 1 + (3 * 256),
	},
	'event_text' : 'Attack any country with a stability of 1 or 2. Roll a die and subtract 1 for every adjacent enemy controlled country. Success on 3-6. Player adds 3 to his Military Ops Track.\nEffects of Victory: Player gains 1 VP and replaces all opponent's Influence with his Influence.',
}


Central_America_Scoring = {
	'card_name' : 'Central America Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Mid War',

	'card_number' : 37,

	'scoring_region' : 'Central America',
	'event_effects' : {
		{ 'ScoreCentralAmerica', 0,
	},
	'event_text' : 'Both sides score:\nPresence: 1\nDomination: 3\nControl: 5\n+1 per controlled Battleground Country in Region\n+1 per Country controlled that is adjacent to enemy superpower',
	'may_be_held' : False,
}


Southeast_Asia_Scoring = {
	'card_name' : 'Southeast Asia Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Mid War',

	'card_number' : 38,

	'may_be_held' : False,
	'scoring_region' : 'Southeast Asia',
	'event_effects' : {
		{ 'ScoreSoutheastAsia', 0,
	},
	'event_text' : 'Both sides score:\n1 VP each for Control of: Burma, Cambodia/Laos,\n    Vietnam, Malaysia, Indonesia, the Phillipines\n2 VP for Control of Thailand',

	'remove_if_used_as_event' : True,
}


Arms_Race = {
	'card_name' : 'Arms Race',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 39,

	'operations_points' : 3,

	'event_owner' : 'Neutral',
	'event_effects' : {
		{ 'GainVictoryPoints', 1, condition={'IfHasMoreMilOpsAndNotRequired',0},
		{ 'GainVictoryPoints', 3, condition={'IfHasMoreMilOpsAndRequired',0},
	},
	'event_text' : 'Compare each player's status on the Military Operations Track. If Phasing Player has more Military Operations points, he scores 1 VP. If Phasing Player has more Military Operations points and has met the Required Military Operations amount, he scores 3 VP instead.',
}

Cuban_Missile_Crisis = {
	'card_name' : 'Cuban Missile Crisis',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 40,

	'operations_points' : 3,

	'event_owner' : 'Neutral',
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
	'card_name' : 'Nuclear Subs',
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
	'card_name' : 'Salt Negotiations',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 43,

	'operations_points' : 3,

	'event_owner' : 'Neutral',
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
	'card_name' : 'Bear Trap',
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

	'event_owner' : 'Neutral',
	'event_effects' : {
		{ 'CommitPlayerDecision', 0,
		{ 'ResolveSummit', 2,
	},
	'event_text' : 'Both players roll a die.  Each adds 1 for each Region they Dominate or Control. igh roller gains 2 VP and may move DEFCON marker one level in either direction. o not reroll ties.',
}


How_I_Learned_to_Stop_Worrying = {
	'card_name' : 'How I Learned to Stop Worrying',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 46,

	'operations_points' : 2,

	'event_owner' : 'Neutral',
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


	'event_owner' : 'Neutral',
	'event_effects' : {
		{ 'AddInfluenceToOneCentralOrSouthAmericaCountry', 2,
		{ 'MakeFreeCoupOrRealignmentsInCentralOrSouthAmerica', 2,
	},
	'event_text' : 'Place 2 Influence in any one Central or South American country.\nThen you may make a free Coup attempt or Realignment roll in one of these regions (using this card's Operations Value).',
}


Kitchen_Debates = {
	'card_name' : 'Kitchen Debates',
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
	'card_name' : 'Missile Envy',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 49,

	'operations_points' : 2,

	'event_owner' : 'Neutral',
	'event_effects' : {
		{ 'RemoveThisCardFromDiscardPile', 0,
		{ 'ResolveMissileEnvy', 0,		-- will
		{ 'DoNotDiscardThisCard', 0,
	},
	'event_text' : 'Exchange this card for your opponent's highest valued Operations card in his hand. If two or more cards are tied, opponent chooses.\nIf the exchanged card contains your event, or an event applicable to both players, it occurs immediately. If it contains opponent's event, use Operations value without triggering event. Opponent must use this card for Operations during his next action round.',
}


We_Will_Bury_You = {
	'card_name' : 'We Will Bury You',
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
	'card_name' : 'Brezhnev Doctrine',
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
	'card_name' : 'Portuguese Empire Crumbles',
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
	'card_name' : 'South African Unrest',
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
	'card_name' : 'Willy Brandt',
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
	'card_name' : 'Muslim Revolution',
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
	'card_name' : 'ABM Treaty',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 57,

	'operations_points' : 4,

	'event_owner' : 'Neutral',
	'event_effects' : {
		{ 'ImproveDEFCONLevel', 1,
		{ 'ConductOperationsWithThisCard', 4,
	},
	'event_text' : 'Improve DEFCON one level.\nThen player may Conduct Operations as if they played a 4 Ops card.',
}


Cultural_Revolution = {
	'card_name' : 'Cultural Revolution',
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
	'card_name' : 'Flower Power',
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
	'card_name' : 'U2 Incident',
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
	'card_name' : 'Lone Gunman',
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
	'card_name' : 'Colonial Rear Guards',
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
	'card_name' : 'Panama Canal Returned',
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
	'card_name' : 'Camp David Accords',
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
	'card_name' : 'Puppet Governments',
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
	'card_name' : 'Grain Sales to Soviets',
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
	'card_name' : 'John Paul II Elected Pope',
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
	'card_name' : 'Latin American Death Squads',
	'card_type' : 'Event',
	'stage' : 'Mid War',

	'card_number' : 69,

	'operations_points' : 2,

	'event_owner' : 'Neutral',
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
	'card_name' : 'OAS Founded',
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
	'card_name' : 'Nixon Plays The China Card',
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
	'card_name' : 'Sadat Expels Soviets',
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
	'card_name' : 'Shuttle Diplomacy',
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
	'card_name' : 'The Voice Of America',
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
	'card_name' : 'Liberation Theology',
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
	'card_name' : 'Ussuri River Skirmish',
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


Ask_Not_What_Your_Country_Can_Do_For_Y'card_name' : 'Ask Not What Your Country Can Do For Yard_type' : 'Event',
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
	'card_name' : 'Alliance for Progress',
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


Africa_Scoring = {
	'card_name' : 'Africa Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Mid War',

	'card_number' : 79,

	'scoring_region' : 'Africa',
	'event_effects' : {
		{ 'ScoreAfrica', 0,
	},
	'event_text' : 'Both sides score:\nPresence: 1\nDomination: 4\nControl: 6\n+1 per controlled Battleground Country in Region',

	'may_be_held' : False,
}


One_Small_Step = {
	'card_type' : 'Event',
	'stage' : 'Mid War',
	'card_number' : 80,
	'operations_points' : 2,
	'event_owner' : 'Neutral',
	'event_effects' : {
		usageconditions = {
			{ 'IfYouAreBehindOnSpaceRaceTrack', 0,
		},
		{ 'AdvanceSpaceRaceTrack', 2,
	},

	'event_text' : 'If you are behind on the Space Race Track, play this card to move your marker two boxes forward on the Space Rack Track, gaining the VP value of the second box only.',
}


South_America_Scoring = {
	'card_name' : 'South America Scoring',
	'card_type' : 'Scoring',
	'stage' : 'Mid War',
	'card_number' : 81,
	'scoring_region' : 'South America',
	'event_effects' : [('ScoreSouthAmerica', 0)],
	'event_text' : 'Both sides score:\nPresence: 2\nDomination: 5\nControl: 6\n+1 per controlled Battleground Country in Region',
	'may_be_held' : False,
}


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
	'card_name' : 'Our Man In Tehran',
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
	'card_name' : 'Iranian Hostage Crisis',
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
	'card_name' : 'The Iron Lady',
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
	'card_name' : 'Reagan Bombs Libya',
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
	'card_name' : 'Star Wars',
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
	'card_name' : 'North Sea Oil',
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
	'card_name' : 'The Reformer',
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
	'card_name' : 'Marine Barracks Bombing',
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
	'card_name' : 'Soviets Shoot Down KAL-007',
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
	'card_name' : 'Ortega Elected in Nicaragua',
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
	'event_owner' : 'Neutral',
	'event_effects' : [('CommitPlayerDecision', 0), ('OpponentDiscardsRandomCard', 0), ('OpponentDiscardsRandomCardIfUSSRAndHasBeenPlayedIranianHostageCrisis', 0)],
	'event_text' : 'Opponent must randomly discard one card. If played by USSR and Iranian Hostage Crisis is in effect, the US player must randomly discard two cards.\n(Events on discards do not occur.)',
}

Iran-Contra_Scandal = {
	'card_name' : 'Iran-Contra Scandal',
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
	'card_name' : 'Latin American Debt Crisis',
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
	'card_name' : 'Tear Down This Wall',
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
	'card_name' : 'An Evil Empire',
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
	'card_name' : 'Aldrich Ames Remix',
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
	'card_name' : 'Pershing II Deployed',
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

	'event_owner' : 'Neutral',
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
	'card_name' : 'Iran-Iraq War',
	'card_type' : 'Event',
	'stage' : 'Late War',

	'card_number' : 102,

	'operations_points' : 2,

	'event_owner' : 'Neutral',
	'event_effects' : {
		{ 'WarInIranOrIraq', 2 + (2 * 256),
	},
	'event_text' : 'Iran or Iraq invades the other (player's choice). Roll one die and subtract 1 for every opponent-controlled country adjacent to target of invasion. Player Victory on modified die roll of 4-6. Player adds 2 to Military Ops Track\nEffects of Victory: Player gains 2 VP and replaces opponent's Influence in target country with his own.',
	'remove_if_used_as_event' : True,
}


# -- OPTIONAL
Yuri_and_Samantha = {
	'card_name' : 'Yuri and Samantha',
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
	'card_name' : 'AWACS Sale to Saudis',
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
