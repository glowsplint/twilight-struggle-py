


--
-- EARLY WAR
--



g_twilight_cards["Asia Scoring"] = { 
	card_name = "Asia Scoring";
	card_type = "Scoring";
	stage = "Early War";
	
	card_number = 1;
	
	scoring_region = "Asia";
	event_effects = {
		{ "ScoreAsia", 0 },
	};
	event_text = "Both sides score:\nPresence: 3\nDomination: 7\nControl: 9\n" ..
					"+1 per controlled Battleground Country in Region\n" ..
					"+1 per Country controlled that is adjacent to enemy superpower";

	may_be_held = false;
}

g_twilight_cards["Europe Scoring"] = { 
	card_name = "Europe Scoring";
	card_type = "Scoring";
	stage = "Early War";
	
	card_number = 2;
	
	scoring_region = "Europe";
	event_effects = {
		{ "ScoreEurope", 0 },
	};
	event_text = "Both sides score:\nPresence: 3\nDomination: 7\nControl: VICTORY\n" ..
					"+1 per controlled Battleground Country in Region\n" ..
					"+1 per Country controlled that is adjacent to enemy superpower";

	may_be_held = false;
}

g_twilight_cards["Middle East Scoring"] = { 
	card_name = "Middle East Scoring";
	card_type = "Scoring";
	stage = "Early War";
	
	card_number = 3;
	
	scoring_region = "Middle East";
	event_effects = {
		{ "ScoreMiddleEast", 0 },
	};
	event_text = "Both sides score:\nPresence: 3\nDomination: 5\nControl: 7\n" ..
					"+1 per controlled Battleground Country in Region";

	may_be_held = false;
}

g_twilight_cards["Duck and Cover"] = { 
	card_name = "Duck and Cover";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 4;
	
	operations_points = 3;
	pending_defcon_level = { -1, -1 };
	
	event_owner = "USA";
	event_effects = {
		{ "RestorePendingDefconLevel", 0 },
		{ "DegradeDEFCONLevel", 1 },
		{ "GainVictoryPointsForDEFCONBelow", 5 },
	};
	event_text = "Degrade DEFCON one level.\n" ..
					"Then US player earns VPs equal to 5 minus current DEFCON level.";
	
	ai = {
		defcon_drop = true,
		
		ussr = {
		},
		usa = {
			headline = 5,
		},
	};
}

g_twilight_cards["Five-Year Plan"] = { 
	card_name = "Five-Year Plan";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 5;
	
	operations_points = 3;
	pending_defcon_level = { -1, 0 };
	
	event_owner = "USA";
	event_effects = {
		{ "CommitPlayerDecision", 0 },
		{ "RestorePendingDefconLevel", 0 },
		{ "OpponentDiscardsRandomCard", 1 },
	};
	event_text = "USSR player must randomly discard one card. " ..
					"If the card is a US associated Event, the Event occurs immediately. " ..
					"If the card is a USSR associated Event or and Event applicable to both players, " ..
					"then the card must be discarded without triggering the Event.";
	
	ai = {
		defcon_draw = true,
			
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 7,
		},
	};
}


g_twilight_cards["The China Card"] = { 
	card_name = "The China Card";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 6;
	
	operations_points = 4;
	
	event_owner = "Neutral";
	can_headline_card = false;
	global_continuous_effects = {
		{
			effect = { "GainOperationsPointsWhenUsingThisCardInAsia", 1 };
		},
	};
	event_text = "Begins the game with the USSR player.\n" ..
					"+1 Operations value when all points are used in Asia. " ..
					"Pass to opponent after play.\n" ..
					"+1 VP for the player holding this card at the end of Turn 10.\n" ..
					"Cancels effect of \'Formosan Resolution\' if this card is played by the US player.";
	
	ai = {
		ussr = {
		},
		usa = {
		},
	};
}

g_twilight_cards["Socialist Governments"] = { 
	card_name = "Socialist Governments";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 7;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "IfHasNotBeenPlayedIronLady", 0 },
			{ "IfCrisisResult1945UKElectionIsNot4or5", 0 },
		};
		{ "RemoveOpponentInfluenceInWesternEuropeMax2", 3 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Unplayable as an event if \'The Iron Lady\' is in effect.\n" ..
					"Remove US Influence in Western Europe by a total of 3 Influence points, " ..
					"removing no more than 2 per country.";
	
	ai = {
		ussr = {
			headline = 8,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}

g_twilight_cards["Fidel"] = { 
	card_name = "Fidel";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 8;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "RemoveAllOpponentInfluenceInCuba", 0 },
		{ "GainInfluenceForControlInCuba", 0 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Remove all US Influence in Cuba. " ..
					"USSR gains sufficient Influence in Cuba for Control.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 5,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Vietnam Revolts"] = { 
	card_name = "Vietnam Revolts";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 9;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "GainInfluenceInVietnam", 2 },
		{ "PauseForAnimationToMap", 0 },
		{ "PutThisCardInPlay", 1 },			
	};
	continuous_effects = {
		{
			effect = { "GainOperationsPointsInSoutheastAsia", 1 };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "Add 2 USSR Influence in Vietnam. " ..
					"For the remainder of the turn, the Soviet player may add 1 Operations point " ..
					"to any card that uses all points in Southeast Asia.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 5,
			play_event_before_action_round = 2,
		},
		usa = {
			play_after_action_round = 5,
			resolve_opponent_event_last = true,
		},
	};
}

g_twilight_cards["Blockade"] = { 
	card_name = "Blockade";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 10;
	
	operations_points = 1;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "IfCrisisResultVEDayIsNot6", 0 },
		};
		{ "OpponentMayDiscardCardWithOpsPoints", 3 },
		{ "RemoveAllOpponentInfluenceInWestGermany", 0, condition={"IfYouDoNot",0}, },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Unless US Player immediately discards a \'3\' or more value Operations card, " ..
					"eliminate all US Influence in West Germany.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 6,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Korean War"] = { 
	card_name = "Korean War";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 11;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "CommitPlayerDecision", 0 },
		{ "WarInSouthKorea", 2 + (2 * 256) },
	};
	event_text = "North Korea invades South Korea. " ..
					"Roll one die and subtract 1 for every US Controlled country adjacent to South Korea. " ..
					"USSR Victory on modified die roll 4-6. " ..
					"USSR add 2 to Military Ops Track.\n" ..
					"Effects of Victory: USSR gains 2 VP and replaces all US Influence " ..
					"in South Korea with USSR Influence.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 6,
		},
		usa = {
			-- TODO: may only place influence adjacent to South Korea before event
		},
	};
}

g_twilight_cards["Romanian Abdication"] = { 
	card_name = "Romanian Abdication";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 12;
	
	operations_points = 1;
	
	event_owner = "USSR";
	event_effects = {
		{ "RemoveAllOpponentInfluenceInRomania", 0 },
		{ "GainInfluenceForControlInRomania", 0 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Remove all US Influence in Romania. " ..
					"USSR gains sufficient Influence in Romania for Control.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 4,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Arab-Israeli War"] = { 
	card_name = "Arab-Israeli War";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 13;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "IfHasNotBeenPlayedCampDavidAccords", 0 },
		};
		{ "CommitPlayerDecision", 0 },
		{ "WarInIsrael", 2 + (2 * 256) },
	};
	event_text = "A Pan-Arab Coalition invades Israel. " ..
					"Roll one die and subtract 1 for US Control of Israel " ..
					"and for US-controlled country adjacent to Israel. " ..
					"USSR Victory on modified die roll 4-6. " ..
					"USSR adds 2 to Military Ops Track.\n" ..
					"Effects of Victory: USSR gains 2 VP and replaces all US Influence " ..
					"in Israel with USSR Influence.";
	
	ai = {
		ussr = {
		},
		usa = {
			-- TODO: may only place influence adjacent to Israel before event
		},
	};
}

g_twilight_cards["COMECON"] = { 
	card_name = "COMECON";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 14;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "AddInfluenceInUncontrolledEasternEuropeMax1", 4 },
	};
	event_text = "Add 1 USSR Influence in each of four non-US Controlled countries in Eastern Europe.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 8,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}

g_twilight_cards["Nasser"] = { 
	card_name = "Nasser";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 15;
	
	operations_points = 1;
	
	event_owner = "USSR";
	event_effects = {
		{ "GainInfluenceInEgypt", 2 },
		{ "RemoveHalfOpponentInfluenceInEgpyt", 0 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Add 2 USSR Influence in Egypt. " ..
					"Remove half (rounded up) of the US Influence in Egypt.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 4,
		},
		usa = {
			-- TODO: may only place influence adjacent to Egypt before event
		},
	};
}

g_twilight_cards["Warsaw Pact Formed"] = { 
	card_name = "Warsaw Pact Formed";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 16;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "ChooseFromEffectList",
			{
				prompt = "Choose for Eastern Europe:",
				{
					{ "RemoveAllOpponentInfluenceFromEasternEurope", 4 },
					{ "PauseForAnimationToMap", 0 },
					description = "Remove 4 US Countries in Eastern Europe",
				},
				{
					{ "AddInfluenceInEasternEuropeMax2", 5 },
					description = "Add 5 USSR Influence in Eastern Europe",
				},
			}
		},
		{ "PutThisCardInPlayOppOwner", 0, condition={"IfHasNotBeenPlayedNATO",0} },			
	};
	event_text = "Remove all US Influence from four countries in Eastern Europe, " ..
					"or add 5 USSR Influence in Eastern Europe, adding no more than 2 per country. " ..
					"Allow play of NATO.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 8,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}

g_twilight_cards["De Gaulle Leads France"] = { 
	card_name = "De Gaulle Leads France";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 17;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "RemoveOpponentInfluenceInFrance", 2 },
		{ "GainInfluenceInFrance", 1 },
		{ "PauseForAnimationToMap", 0 },
		{ "PutThisCardInPlay", 0 },			
	};
	event_text = "Remove 2 US Influence in France, add 1 USSR Influence. " ..
					"Cancels effects of NATO for France.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 6,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Captured Nazi Scientist"] = { 
	card_name = "Captured Nazi Scientist";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 18;
	
	operations_points = 1;
	
	event_owner = "Neutral";
	event_effects = {
		{ "AdvanceSpaceRaceTrack", 1 },
	};
	event_text = "Advance player's Space Race marker one box.";
	remove_if_used_as_event = true;
	
	ai = {
		headline = 5,
			
		ussr = {
		},
		usa = {
		},
	};
}

g_twilight_cards["Truman Doctrine"] = { 
	card_name = "Truman Doctrine";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 19;
	
	operations_points = 1;
	
	event_owner = "USA";
	event_effects = {
		{ "RemoveAllOpponentInfluenceFromUncontrolledInEurope", 1 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Remove all USSR Influence markers in one uncontrolled country in Europe.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 5,
		},
	};
}


g_twilight_cards["Olympic Games"] = { 
	card_name = "Olympic Games";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 20;
	
	operations_points = 2;
	pending_defcon_level = { -1, -1 };

	event_owner = "Neutral";
	event_effects = {
		{ "ResolveOlympicGames", 4 },		-- will RestorePendingDefconLevel
	};
	event_text = "Player sponsors Olympics. " ..
					"Opponent may participate or boycott. " ..
					"If Opponent participates, each player rolls one die, with the sponsor adding 2 to his roll. " ..
					"High roll gains 2 VP. Reroll ties " ..
					"If Opponent boycotts, degrade DEFCON one level and the Sponsor may " ..
					"Conduct Operations as if they played a 4 Ops card.";
	
	ai = {
		headline = 5,
		defcon_event = true,
			
		ussr = {
		},
		usa = {
		},
	};
}

g_twilight_cards["NATO"] = { 
	card_name = "NATO";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 21;
	
	operations_points = 4;
	
	event_owner = "USA";
	event_effects = {
		usageconditions = {
			{ "IfHasBeenPlayedMarshallPlanOrWarsawPact", 0 },
		};
		{ "PutThisCardInPlay", 0 },
		{ "RemoveMarshallPlanFromPlay", 0 },
		{ "RemoveWarsawPactFormedFromPlay", 0 },
					
	};
	continuous_effects = {
		{
			effect = { "OpponentCannotCoupOrRealignInControlledEurope", 0 };
		},
	};
	event_text = "Play after \'Marshall Plan\' or \'Warsaw Pact\'.\n" ..
					"USSR player may no longer make Coup or Realignment rolls in any US Controlled countries in Europe. " ..
					"US Controlled countries in Europe may not be attacked by play of the Brush War event.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 2,
		},
	};
}

g_twilight_cards["Independent Reds"] = { 
	card_name = "Independent Reds";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 22;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "MatchOpponentInfluenceForIndependentReds", 1 },
	};
	event_text = "Adds sufficient US Influence in either Yugoslavia, Romania, Bulgaria, Hungary, " ..
					"or Czechoslavakia to equal USSR Influence.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 6,
		},
	};
}

g_twilight_cards["Marshall Plan"] = { 
	card_name = "Marshall Plan";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 23;
	
	operations_points = 4;
	
	event_owner = "USA";
	event_effects = {
		{ "AddInfluenceInUncontrolledWesternEuropeMax1", 7 },
		{ "PutThisCardInPlay", 0, condition={"IfHasNotBeenPlayedNATO",0} },			
	};
	event_text = "Allows play of NATO.\n" ..
					"Add one US Influence in each of seven non-USSR Controlled Western European countries.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 9,
		},
	};
}

g_twilight_cards["Indo-Pakistani War"] = { 
	card_name = "Indo-Pakistani War";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 24;
	
	operations_points = 2;
	
	event_owner = "Neutral";
	event_effects = {
		{ "WarInIndiaOrPakistan", 2 + (2 * 256) },
	};
	event_text = "India or Pakistan invades the other (player's choice). " ..
					"Roll one die and subtract 1 for every opponent-controlled country " ..
					"adjacent to the target of the invasion. " ..
					"Player Victory on modified die roll of 4-6. " ..
					"Player adds 2 to Military Ops Track. " ..
					"Effects of Victory: Player gains 2 VP and replaces all opponent's Influence " ..
					"in target country with his Influence.";
	
	ai = {
		headline = 7,
			
		ussr = {
		},
		usa = {
		},
	};
}

g_twilight_cards["Containment"] = { 
	card_name = "Containment";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 25;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "PutThisCardInPlay", 1 },			
	};
	continuous_effects = {
		{
			effect = { "IncreaseOperationsPointsForYourCards", 1 };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "All further Operations cards played by US this turn " ..
					"add one to their value (to a maximum of 4).";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			play_after_action_round = 5,
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 9,
			play_event_before_action_round = 1,
		},
	};
}

g_twilight_cards["CIA Created"] = { 
	card_name = "CIA Created";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 26;
	
	operations_points = 1;
	pending_defcon_level = { -1, 0 };
	
	event_owner = "USA";
	event_effects = {
		{ "CommitPlayerDecision", 0 },
		{ "RestorePendingDefconLevel", 0 },
		{ "OpponentRevealsHand", 0 },			
		{ "ConductOperationsWithThisCard", 1 },			
	};
	event_text = "USSR reveals hand this turn.\n" ..
					"Then the US may Conduct Operations as if they played a 1 Op card.";
	remove_if_used_as_event = true;
	
	ai = {
		
		ussr = {
			defcon_ops = true,
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 6,
		},
	};
}

g_twilight_cards["US/Japan Mutual Defense Pact"] = { 
	card_name = "US/Japan Mutual Defense Pact";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 27;
	
	operations_points = 4;
	
	event_owner = "USA";
	event_effects = {
		{ "GainInfluenceForControlInJapan", 0 },
		{ "PauseForAnimationToMap", 0 },
		{ "PutThisCardInPlay", 0 },			
	};
	continuous_effects = {
		{
			effect = { "OpponentCannotCoupOrRealignInJapan", 0 };
		},
	};
	event_text = "US gains sufficient Influence in Japan for Control. " ..
					"USSR may no longer make Coup or Realignment rolls in Japan.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 1,
		},
	};
}

g_twilight_cards["Suez Crisis"] = { 
	card_name = "Suez Crisis";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 28;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "IfCrisisResult1945UKElectionIsNot6", 0 },
		};
		{ "RemoveOpponentInfluenceForSuezCrisis", 4 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Remove a total of 4 US Influence from France, the United Kingdom or Israel. " ..
					"Remove no more than 2 Influence per country.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 10,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}

g_twilight_cards["East European Unrest"] = { 
	card_name = "East European Unrest";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 29;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "Remove1OpponentInfluenceFromEasternEuropeCountries", 3, condition={"IfTurnNumberLessThan",7} },
		{ "Remove2OpponentInfluenceFromEasternEuropeCountries", 3, condition={"IfTurnNumberGreaterThan",8} },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "In Early or Mid War: Remove 1 USSR Influence from three countries in Eastern Europe.\n" ..
					"In Late War: Remove 2 USSR Influence from three countries in Eastern Europe.";
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 7,
		},
	};
}

g_twilight_cards["Decolonization"] = { 
	card_name = "Decolonization";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 30;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "AddInfluenceInAfricaOrSEAsiaMax1", 4 },
	};
	event_text = "Add one USSR Influence in each of any four African and/or SE Asian countries.";
	
	ai = {
		ussr = {
			headline = 9,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}

g_twilight_cards["Red Scare/Purge"] = { 
	card_name = "Red Scare/Purge";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 31;
	
	operations_points = 4;
	
	event_owner = "Neutral";
	event_effects = {
		usageconditions = {
			{ "NotIfChinaCardIsUnclaimedAndIsUSSR", 0 },
		};
		{ "PutThisCardInPlay", 1 },			
	};
	continuous_effects = {
		{
			effect = { "DecreaseOperationsPointsForOpponentsCards", 1 };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "All further Operations cards played by your opponent this turn " ..
					"are -1 to their value (to a minimum of 1 Op).";
	
	ai = {
		headline = 9,
		play_event_before_action_round = 1,
			
		ussr = {
		},
		usa = {
		},
	};
}

g_twilight_cards["UN Intervention"] = { 
	card_name = "UN Intervention";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 32;
	
	operations_points = 1;
	
	event_owner = "Neutral";
	can_headline_card = false;
	event_effects = {
		usageconditions = {
			{ "IfIsNotHeadlinePhase", 0 },
			{ "IfHaveOpponentEventInHand", 0 },
		};
		{ "ConductOperationsWithOpponentEventCard", 0 },			
	};
	event_text = "Play this card simultaneously with a card containing your opponent's associated Event. " ..
					"The Event is cancelled, but you may use its Operations value to Conduct Operations. " ..
					"The cancelled event returns to the discard pile. " ..
					"May not be played during headline phase.";
	
	ai = {
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["De-Stalinization"] = { 
	card_name = "De-Stalinization";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 33;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "RelocateInfluenceToUncontrolledCountriesMax2", 4 },
	};
	event_text = "USSR may relocate up to 4 Influence points to non-US controlled countries. " ..
					"No more than 2 Influence may be placed in the same country.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 8,
		},
		usa = {
			resolve_opponent_event_first = true,
			do_not_predict_headline = true,
		},
	};
}

g_twilight_cards["Nuclear Test Ban"] = { 
	card_name = "Nuclear Test Ban";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 34;
	
	operations_points = 4;
	
	event_owner = "Neutral";
	event_effects = {
		{ "GainVictoryPointsForDEFCONMinus", 2 },
		{ "ImproveDEFCONLevel", 2 },
	};
	event_text = "Player earns VPs equal to the current DEFCON level minus 2, " ..
					"then improve DEFCON two levels.";
	
	ai = {
		headline = 3,
			
		ussr = {
		},
		usa = {
		},
	};
}

g_twilight_cards["Formosan Resolution"] = { 
	card_name = "Formosan Resolution";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 35;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		usageconditions = {
			{ "NotIfChinaCardIsUnclaimedAndIsUSA", 0 },
		};
		{ "PutThisCardInPlay", 0 },			
	};
	continuous_effects = {
		{
			effect = { "TaiwanIsBattlegroundForScoringIfUSControlled", 0  };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "WhenYouPlayChinaCard", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "Taiwan shall be treated as a Battleground country for scoring purposes, " ..
					"if the US controls Taiwan when the Asia Scoring Card is played " ..
					"or during Final Scoring at the end of Turn 10. " ..
					"Taiwan is not a battleground country for any other game purpose. " ..
					"This card is discarded after US play of \'The China Card\'.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 4,
		},
	};
}

g_twilight_cards["Defectors"] = { 
	card_name = "Defectors";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 103;
	
	operations_points = 2;
	
	event_owner = "USA";
	resolve_headline_first = true;
	event_effects = {
		{ "CancelPlayerHeadline", 0, condition={"IfIsHeadlinePhase",0} },
		{ "GainVictoryPoints", 1, condition={"IfIsOpponentActionRound",0} },
	};
	event_text = "Play in Headline Phase to cancel USSR Headline event, including Scoring Card. " ..
					"Cancelled card returns to the Discard Pile.\n" ..
					"If Defectors played by USSR during Soviet action round, US gains 1 VP (unless played on the Space Race).";
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 9,
			play_event_before_action_round = 0,
		},
	};
}


-- OPTIONAL
g_twilight_cards["The Cambridge Five"] = { 
	card_name = "The Cambridge Five";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 104;
	optional_card = true;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "IfTurnNumberLessThan", 7 },
		};
		{ "CommitPlayerDecision", 0 },
		{ "OpponentRevealsScoringCardsInHand", 0 },
		{ "AddInfluenceInOpponentScoringCardRegion", 1 },
	};
	event_text = "The US player exposes all scoring cards in their hand. " ..
					"The USSR player may then add 1 Influence in any single region named on one of those scoring cards (USSR choice). " ..
					"Cannot be played as an event in Late War.";
	
	ai = {
		ussr = {
			headline = 7,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


-- OPTIONAL
g_twilight_cards["Special Relationship"] = { 
	card_name = "Special Relationship";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 105;
	optional_card = true;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "AddInfluenceToOneWesternEuropeCountry", 2, condition={"IfControlUKAndNATO",0} },
		{ "GainVictoryPoints", 2, condition={"IfControlUKAndNATO",0} },
		{ "AddInfluenceAdjacentToUK", 1, condition={"IfControlUKButNoNATO",8} },
	};
	event_text = "If UK is US controlled but NATO is not in effect, US adds 1 Influence to any country adjacent to the UK.\n" ..
					"If UK is US controlled and NATO is in effect, US adds 2 Influence " ..
					"to any Western European country and gains 2 VPs.";
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 6,
		},
	};
}


-- OPTIONAL
g_twilight_cards["NORAD"] = { 
	card_name = "NORAD";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 106;
	optional_card = true;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "PutThisCardInPlay", 0 },			
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfActionRound", 0 },
				{ "IfDefconDroppedTo2", 0 },
				{ "IfYouControlCanada", 0 },
			};
			triggereffect = {
				{ "TriggerAnnounceCardInPlay", 0 },
				{ "TriggerAddInfluenceToExisting", 1 },
			};
		},
	};
	event_text = "If the US controls Canada, the US may add 1 Influence to any country " ..
					"already containing US Influence at the conclusion of any Action Round " ..
					"in which the DEFCON marker moves to the \'2\' box. " ..
					"This event cancelled by \'Quagmire\'.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 6,
		},
	};
}



















--
-- MID WAR
--


g_twilight_cards["Brush War"] = { 
	card_name = "Brush War";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 36;
	
	operations_points = 3;
	
	event_owner = "Neutral";
	event_effects = {
		{ "BrushWarInStabilityLowerThan2", 1 + (3 * 256) },
	};
	event_text = "Attack any country with a stability of 1 or 2. " ..
					"Roll a die and subtract 1 for every adjacent enemy controlled country. " ..
					"Success on 3-6. " ..
					"Player adds 3 to his Military Ops Track.\n" ..
					"Effects of Victory: Player gains 1 VP and replaces all opponent's Influence with his Influence.";
	
	ai = {
		headline = 10,
			
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["Central America Scoring"] = { 
	card_name = "Central America Scoring";
	card_type = "Scoring";
	stage = "Mid War";
	
	card_number = 37;
		
	scoring_region = "Central America";
	event_effects = {
		{ "ScoreCentralAmerica", 0 },
	};
	event_text = "Both sides score:\nPresence: 1\nDomination: 3\nControl: 5\n" ..
					"+1 per controlled Battleground Country in Region\n" ..
					"+1 per Country controlled that is adjacent to enemy superpower";
	may_be_held = false;
}


g_twilight_cards["Southeast Asia Scoring"] = { 
	card_name = "Southeast Asia Scoring";
	card_type = "Scoring";
	stage = "Mid War";
	
	card_number = 38;
	
	may_be_held = false;
	scoring_region = "Southeast Asia";
	event_effects = {
		{ "ScoreSoutheastAsia", 0 },
	};
	event_text = "Both sides score:\n" ..
					"1 VP each for Control of: Burma, Cambodia/Laos,\n" ..
					"    Vietnam, Malaysia, Indonesia, the Phillipines\n" ..
					"2 VP for Control of Thailand";
	
	remove_if_used_as_event = true;
}


g_twilight_cards["Arms Race"] = { 
	card_name = "Arms Race";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 39;
	
	operations_points = 3;
	
	event_owner = "Neutral";
	event_effects = {
		{ "GainVictoryPoints", 1, condition={"IfHasMoreMilOpsAndNotRequired",0} },
		{ "GainVictoryPoints", 3, condition={"IfHasMoreMilOpsAndRequired",0} },
	};
	event_text = "Compare each player's status on the Military Operations Track. " ..
					"If Phasing Player has more Military Operations points, he scores 1 VP. " ..
					"If Phasing Player has more Military Operations points and " ..
					"has met the Required Military Operations amount, he scores 3 VP instead.";
	
	ai = {
		ussr = {
		},
		usa = {
		},
	};
}

g_twilight_cards["Cuban Missile Crisis"] = { 
	card_name = "Cuban Missile Crisis";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 40;
	
	operations_points = 3;
	
	event_owner = "Neutral";
	event_effects = {
		{ "SetDEFCONLevel", 2 },
		{ "PutThisCardInPlay", 1 },			
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	
	cardinplay_abilities = {
		{
			ability_name = "Remove 2 Influence from Cuba",
			description = "Remove 2 Influence from Cuba";
			conditions = {
				{ "IfPlayerIsUSSR", 0 },
				{ "IfPlayerHasInfluenceInCuba", 2 },
			},
			{ "RemoveInfluenceInCuba", 2 },
			{ "PauseForAnimationToMap", 0 },
			{ "RemoveThisCardFromPlay", 1 },
		},
		{
			ability_name = "Remove 2 Influence from West Germany",
			description = "Remove 2 Influence from West Germany";
			conditions = {
				{ "IfPlayerIsUS", 0 },
				{ "IfPlayerHasInfluenceInWestGermany", 2 },
			},
			{ "RemoveInfluenceInWestGermany", 2 },
			{ "PauseForAnimationToMap", 0 },
			{ "RemoveThisCardFromPlay", 1 },
		},
		{
			ability_name = "Remove 2 Influence from Turkey",
			description = "Remove 2 Influence from Turkey";
			conditions = {
				{ "IfPlayerIsUS", 0 },
				{ "IfPlayerHasInfluenceInTurkey", 2 },
			},
			{ "RemoveInfluenceInTurkey", 2 },
			{ "PauseForAnimationToMap", 0 },
			{ "RemoveThisCardFromPlay", 1 },
		},
	};
	
	
	event_text = "Set DEFCON to Level 2. " ..
					"Any further Coup attempt by your opponent this turn, anywhere on the board, " ..
					"will result in Global Thermonuclear War. " ..
					"Your opponent will lose the game. " ..
					"This event may be cancelled at any time if the USSR player " ..
					"removes two Influence from Cuba " ..
					"or the US player removes 2 Influence from either West Germany or Turkey.";
	remove_if_used_as_event = true;
	
	ai = {
		headline = 8,
		play_event_before_action_round = 1,
		do_not_predict_headline = true,
		
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["Nuclear Subs"] = { 
	card_name = "Nuclear Subs";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 41;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "PutThisCardInPlay", 1 },			
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "US Coup attempts in Battleground Countries do not affect the DEFCON track " ..
					"for the remainder of the turn (does not affect Cuban Missile Crisis).";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			play_after_action_round = 5,
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 8,
			play_event_before_action_round = 2,
		},
	};
}


g_twilight_cards["Quagmire"] = { 
	card_name = "Quagmire";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 42;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "PutOpponentIntoQuagmire", 0 },			
		{ "RemoveNORADFromPlay", 0 },			
	};
	event_text = "On next action round, US player must discard an Operations card worth 2 or more " ..
					"and roll 1-4 to cancel this event. " ..
					"Repeat each US player Action round until successful or no appropriate cards remain. " ..
					"If out of appropriate cards, the US player may only play scoring cards until the next turn.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 5,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["Salt Negotiations"] = { 
	card_name = "Salt Negotiations";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 43;
	
	operations_points = 3;
	
	event_owner = "Neutral";
	event_effects = {
		{ "ImproveDEFCONLevel", 2 },
		{ "RecoverEventCardFromDiscardPile", 1 },
		{ "PutThisCardInPlay", 1 },			
	};
	continuous_effects = {
		{
			effect = { "ReduceAllCoupAttempts", 1 };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "Improve DEFCON two levels.\n" ..
					"Further Coup attempts incur -1 die roll modifier for both players for the remainder of the turn.\n" ..
					"Player may sort through discard pile and reclaim one non-scoring card, after revealing it to their opponent.";
	remove_if_used_as_event = true;
	
	ai = {
		headline = 6,
		
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["Bear Trap"] = { 
	card_name = "Bear Trap";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 44;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "PutOpponentIntoBearTrap", 0 },			
	};
	event_text = "On next action round, USSR player must discard an Operations card worth 2 or more " ..
					"and roll 1-4 to cancel this event. " ..
					"Repeat each USSR player Action Round until successful or no appropriate cards remain. " ..
					"If out of appropriate cards, the USSR player may only play scoring cards until the next turn.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 8,
		},
	};
}


g_twilight_cards["Summit"] = { 
	card_name = "Summit";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 45;
	
	operations_points = 1;
	pending_defcon_level = { -1, -1 };
	
	event_owner = "Neutral";
	event_effects = {
		{ "CommitPlayerDecision", 0 },
		{ "RestorePendingDefconLevel", 0 },
		{ "ResolveSummit", 2 },			
	};
	event_text = "Both players roll a die.  Each adds 1 for each Region they Dominate or Control. " ..
				"High roller gains 2 VP and may move DEFCON marker one level in either direction. " ..
				"Do not reroll ties.";
	
	ai = {
		headline = 6,
		defcon_event = true,
		
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["How I Learned to Stop Worrying"] = { 
	card_name = "How I Learned to Stop Worrying";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 46;
	
	operations_points = 2;
	
	event_owner = "Neutral";
	event_effects = {
		{ "ChooseDEFCONLevel", 0 },
		{ "GainMilitaryOperationsTrack", 5 },		
	};
	event_text = "Set the DEFCON at any level you want (1-5). " ..
					"This event counts as 5 Military Operations for the purpose " ..
					"of required Military Operations.";
	remove_if_used_as_event = true;
	
	ai = {
		headline = 4,
		
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["Junta"] = { 
	card_name = "Junta";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 47;
	
	operations_points = 2;
	
	
	event_owner = "Neutral";
	event_effects = {
		{ "AddInfluenceToOneCentralOrSouthAmericaCountry", 2 },
		{ "MakeFreeCoupOrRealignmentsInCentralOrSouthAmerica", 2 },
	};
	event_text = "Place 2 Influence in any one Central or South American country.\n" ..
					"Then you may make a free Coup attempt or Realignment roll in one of these regions " ..
					"(using this card's Operations Value).";
	
	ai = {
		headline = 9,
		
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["Kitchen Debates"] = { 
	card_name = "Kitchen Debates";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 48;
	
	operations_points = 1;
	
	event_owner = "USA";
	event_effects = {
		usageconditions = {
			{ "IfYouControlMoreBattlegrounds", 0 },
		};
		{ "GainVictoryPoints", 2 },
	};
	event_text = "If the US controls more Battleground countries than the USSR, " ..
					"poke opponent in chest and gain 2 VP!";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 7,
		},
	};
}


g_twilight_cards["Missile Envy"] = { 
	card_name = "Missile Envy";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 49;
	
	operations_points = 2;
	pending_defcon_level = { -1, -1 };
	
	event_owner = "Neutral";
	event_effects = {
		{ "RemoveThisCardFromDiscardPile", 0 },
		{ "ResolveMissileEnvy", 0 },		-- will RestorePendingDefconLevel
		{ "DoNotDiscardThisCard", 0 },		
	};
	event_text = "Exchange this card for your opponent's highest valued Operations card in his hand. " ..
					"If two or more cards are tied, opponent chooses.\n" ..
					"If the exchanged card contains your event, or an event applicable to both players, " ..
					"it occurs immediately. " ..
					"If it contains opponent's event, use Operations value without triggering event. " ..
					"Opponent must use this card for Operations during his next action round.";
	
	ai = {
		headline = 8,
		defcon_draw = true,
		
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["We Will Bury You"] = { 
	card_name = "We Will Bury You";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 50;
	
	operations_points = 4;
	pending_defcon_level = { -1, -1 };
	
	event_owner = "USSR";
	event_effects = {
		{ "RestorePendingDefconLevel", 0 },
		{ "DegradeDEFCONLevel", 1 },
		{ "PutThisCardInPlay", 1 },			
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtStartOfOpponentActionRound", 0 },
			};
			triggereffect = {
				{ "TriggerIncrementEffectData", 0 },
			};
		},
		{
			conditions = {
				{ "WhenOpponentPlaysUNInterventionAsEvent", 0 },
				{ "IfEffectDataIsNotZero", 0 },
				{ "IfEffectDataIsZero", 1 },
			};
			triggereffect = {
				{ "TriggerIncrementEffectData", 1 },
			};
		},
		{
			conditions = {
				{ "WhenOpponentPlaysNotUNInterventionAsEvent", 0 },
				{ "IfEffectDataIsNotZero", 0 },
				{ "IfEffectDataIsZero", 1 },
			};
			triggereffect = {
				{ "TriggerAnnounceCardInPlay", 0 },
				{ "TriggerGainVictoryPoints", 3 },
				{ "TriggerIncrementEffectData", 1 },
			};
		},
		{
			conditions = {
				{ "AtEndOfActionRound", 0 },
				{ "IfEffectDataIsNotZero", 0 },
				{ "IfEffectDataIsZero", 1 },
			};
			triggereffect = {
				{ "TriggerAnnounceCardInPlay", 0 },
				{ "TriggerGainVictoryPoints", 3 },
				{ "TriggerIncrementEffectData", 1 },
			};
		},
		{
			conditions = {
				{ "AtEndOfActionRound", 0 },
				{ "IfEffectDataIsNotZero", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 0 },
			};
		},
	};
	event_text = "Unless UN Invervention is played as an Event on the US player's next round, " ..
					"USSR gains 3 VP prior to any US VP award.\n" ..
					"Degrade DEFCON one level.";
	remove_if_used_as_event = true;
	
	ai = {
		defcon_drop = true,

		ussr = {
			headline = 6,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["Brezhnev Doctrine"] = { 
	card_name = "Brezhnev Doctrine";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 51;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "PutThisCardInPlay", 1 },			
	};
	continuous_effects = {
		{
			effect = { "IncreaseOperationsPointsForYourCards", 1 };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "All further Operations cards played by the USSR this turn " ..
					"increase their Ops value by one (to a maximum of 4).";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 10,
			play_event_before_action_round = 1,
		},
		usa = {
			play_after_action_round = 5,
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["Portuguese Empire Crumbles"] = { 
	card_name = "Portuguese Empire Crumbles";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 52;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "GainInfluenceInSEAfricanStates", 2 },
		{ "GainInfluenceInAngola", 2 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Add 2 USSR Influence in both SE African States and Angola.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 6,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["South African Unrest"] = { 
	card_name = "South African Unrest";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 53;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "ChooseFromEffectList",
			{
				prompt = "Choose for South Africa:",
				{
					{ "GainInfluenceInSouthAfrica", 2 },
					{ "PauseForAnimationToMap", 0 },
					description = "Gain 2 Influence in South Africa",
				},
				{
					{ "GainInfluenceInSouthAfrica", 1 },
					{ "AddInfluenceAdjacentToSouthAfrica", 2 },
					{ "PauseForAnimationToMap", 0 },
					description = "Add Influence Adjacent to South Africa",
				},
			}
		},
	};
	event_text = "USSR either adds 2 Influence in South Africa " ..
					"or adds 1 Influence in South Africa and 2 Influence " ..
					"in any countries adjacent to South Africa.";
	
	ai = {
		ussr = {
			headline = 6,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Allende"] = { 
	card_name = "Allende";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 54;
	
	operations_points = 1;
	
	event_owner = "USSR";
	event_effects = {
		{ "GainInfluenceInChile", 2 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "USSR receives 2 Influence in Chile.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 7,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["Willy Brandt"] = { 
	card_name = "Willy Brandt";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 55;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "IfHasNotBeenPlayedTearDownThisWall", 0 },
		};
		{ "GainVictoryPoints", 1 },
		{ "GainInfluenceInWestGermany", 1 },
		{ "PutThisCardInPlay", 0 },			
	};
	event_text = "USSR receives gains 1 VP.\n" ..
					"USSR receives 1 Influence in West Germany.\n" ..
					"Cancels NATO for West Germany.\n" ..
					"This event unplayable and/or cancelled by Tear Down This Wall.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 5,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Muslim Revolution"] = { 
	card_name = "Muslim Revolution";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 56;
	
	operations_points = 4;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "IfHasNotBeenPlayedAWACSSaleToSaudis", 0 },
		};
		{ "RemoveAllOpponentInfluenceForMuslimRevolution", 2 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Remove all US Influence in two of the following countries: " ..
					"Sudan, Iran, Iraq, Egypt, Libya, Saudi Arabia, Syria, Jordan.";
	
	ai = {
		ussr = {
			headline = 8,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["ABM Treaty"] = { 
	card_name = "ABM Treaty";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 57;
	
	operations_points = 4;
	
	event_owner = "Neutral";
	event_effects = {
		{ "ImproveDEFCONLevel", 1 },
		{ "ConductOperationsWithThisCard", 4 },			
	};
	event_text = "Improve DEFCON one level.\n" ..
					"Then player may Conduct Operations as if they played a 4 Ops card.";
	
	ai = {
		headline = 7,
			
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["Cultural Revolution"] = { 
	card_name = "Cultural Revolution";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 58;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "NotIfChinaCardIsUnclaimedAndIsUSSR", 0 },
		};
		{ "GainVictoryPoints", 1, condition={"IfYouHaveChinaCard",0} },
		{ "ClaimChinaCard", 0, condition={"IfYouDoNotHaveChinaCard",0} },
	};
	event_text = "If the US has \'The China Card\', claim it face up and available for play. " ..
					"If the USSR already had it, USSR gains 1 VP.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 6,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["Flower Power"] = { 
	card_name = "Flower Power";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 59;
	
	operations_points = 4;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "IfHasNotBeenPlayedAnEvilEmpire", 0 },
		};
		{ "PutThisCardInPlay", 0 },			
	};
	triggered_effects = {
		{
			conditions = {
				{ "WhenOpponentPlaysWarCard", 0 },
			};
			triggereffect = {
				{ "TriggerAnnounceCardInPlay", 0 },
				{ "TriggerGainVictoryPoints", 2 },
			};
		},
	};
	event_text = "USSR gains 2 VP for every subsequently US played \'war card\' " ..
					"(played as an Event or Operations) unless played on the Space Race.\n" ..
					"War Cards: Arab-Israeli War, Korean War, Brush War, Indo-Pakistani War or Iran-Iraq War.\n" ..
					"This event cancelled by \'An Evil Empire\'.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 4,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["U2 Incident"] = { 
	card_name = "U2 Incident";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 60;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "GainVictoryPoints", 1 },
		{ "PutThisCardInPlay", 1 },			
	};
	triggered_effects = {
		{
			conditions = {
				{ "WhenUNInventionIsPlayedAsEvent", 0 },
			};
			triggereffect = {
				{ "TriggerAnnounceCardInPlay", 0 },
				{ "TriggerGainVictoryPoints", 1 },
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "USSR gains 1VP.\n" ..
					"If UN Intervention played later this turn as an Event, " ..
					"either by US or USSR, gain 1 additional VP.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 5,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["OPEC"] = { 
	card_name = "OPEC";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 61;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		usageconditions = {
			{ "IfHasNotBeenPlayedNorthSeaOil", 0 },
		};
		{ "GainVPForOPEC", 1 },
	};
	event_text = "USSR gains 1VP for each of the following countries he controls:\n" ..
					"Egypt, Iran, Libya, Saudi Arabia, Iraq, Gulf States, and Venezuela.\n" ..
					"Unplayable as an event if \'North Sea Oil\' is in effect.";
	
	ai = {
		ussr = {
			headline = 6,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["Lone Gunman"] = { 
	card_name = "Lone Gunman";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 62;
	
	operations_points = 1;
	pending_defcon_level = { 0, -1 };
	
	event_owner = "USSR";
	event_effects = {
		{ "CommitPlayerDecision", 0 },
		{ "RestorePendingDefconLevel", 0 },
		{ "OpponentRevealsHand", 0 },			
		{ "ConductOperationsWithThisCard", 1 },			
	};
	event_text = "US player reveals his hand. " ..
					"Then the USSR may Conduct Operations as if they played a 1 Op card.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 7,
		},
		usa = {
			defcon_ops = true,
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Colonial Rear Guards"] = { 
	card_name = "Colonial Rear Guards";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 63;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "AddInfluenceInAfricaOrSEAsiaMax1", 4 },
	};
	event_text = "Add 1 US Influence in each of four different African and/or Southeast Asian countries.";
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 8,
		},
	};
}


g_twilight_cards["Panama Canal Returned"] = { 
	card_name = "Panama Canal Returned";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 64;
	
	operations_points = 1;
	
	event_owner = "USA";
	event_effects = {
		{ "GainInfluenceInPanama", 1 },
		{ "GainInfluenceInCostaRica", 1 },
		{ "GainInfluenceInVenezuela", 1 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Add 1 US Influence in Panama, Costa Rica, and Venezuela.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 6,
		},
	};
}


g_twilight_cards["Camp David Accords"] = { 
	card_name = "Camp David Accords";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 65;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "GainVictoryPoints", 1 },
		{ "GainInfluenceInIsrael", 1 },
		{ "GainInfluenceInJordan", 1 },
		{ "GainInfluenceInEgypt", 1 },
		{ "PauseForAnimationToMap", 0 },
		{ "PutThisCardInPlay", 0 },			
	};
	event_text = "US gains 1 VP.\n" ..
					"US receives 1 Influence in Israel, Jordan and Egypt.\n" ..
					"Arab-Israeli War event no longer playable.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 7,
		},
	};
}


g_twilight_cards["Puppet Governments"] = { 
	card_name = "Puppet Governments";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 66;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "AddInfluenceInEmptyCountriesMax1", 3 },
	};
	event_text = "US may add 1 Influence in three countries that currently contain no Influence from either power.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 8,
		},
	};
}


g_twilight_cards["Grain Sales to Soviets"] = { 
	card_name = "Grain Sales to Soviets";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 67;
	
	operations_points = 2;
	pending_defcon_level = { -1, 0 };
	
	event_owner = "USA";
	event_effects = {
		{ "CommitPlayerDecision", 0 },
		{ "RestorePendingDefconLevel", 0 },
		{ "MayPlayRandomCardFromOpponentHand", 0 },
		{ "ConductOperationsWithThisCard", 2, condition={"IfYouDoNot",2} },			
	};
	event_text = "Randomly choose one card from USSR hand. " ..
					"Play it or return it. " ..
					"If Soviet player has no cards, or returned, " ..
					"use this card to conduct Operations normally.";
	
	ai = {
		ussr = {
			defcon_ops = true,
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 10,
		},
	};
}


g_twilight_cards["John Paul II Elected Pope"] = { 
	card_name = "John Paul II Elected Pope";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 68;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "RemoveOpponentInfluenceInPoland", 2 },
		{ "GainInfluenceInPoland", 1 },
		{ "PauseForAnimationToMap", 0 },
		{ "PutThisCardInPlay", 0 },			
	};
	event_text = "Remove 2 USSR Influence in Poland and then add 1 US Influence in Poland.\n" ..
					"Allows play of \'Solidarity\'.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 8,
		},
	};
}

g_twilight_cards["Latin American Death Squads"] = { 
	card_name = "Latin American Death Squads";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 69;
	
	operations_points = 2;
	
	event_owner = "Neutral";
	event_effects = {
		{ "PutThisCardInPlay", 1 },			
	};
	continuous_effects = {
		{
			effect = { "AdjustCoupAttemptsInCentralAndSouthAmerica", 1 };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "All of the player's Coup attempts in Central and South America are +1 " ..
					"for the remainder of the turn, while all opponent's Coup attempts " ..
					"are -1 for the remainder of the turn.";
	
	ai = {
		headline = 3,
		play_event_before_action_round = 1,
		
		ussr = {
		},
		usa = {
		},
	};
}

g_twilight_cards["OAS Founded"] = { 
	card_name = "OAS Founded";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 70;
	
	operations_points = 1;
	
	event_owner = "USA";
	event_effects = {
		{ "AddInfluenceInCentralAmericaOrSouthAmerica", 2 },
	};
	event_text = "Add 2 US Influence in Central America and/or South America.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 8,
		},
	};
}


g_twilight_cards["Nixon Plays The China Card"] = { 
	card_name = "Nixon Plays The China Card";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 71;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "GainVictoryPoints", 2, condition={"IfYouHaveChinaCard",0} },
		{ "ClaimChinaCard", 1, condition={"IfYouDoNotHaveChinaCard",0} },
	};
	event_text = "If US has \'The China Card\', gain 2 VP. " ..
					"Otherwise, US player receives \'The China Card\' now, " ..
					"face down and unavailable for immediate play.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 6,
		},
	};
}


g_twilight_cards["Sadat Expels Soviets"] = { 
	card_name = "Sadat Expels Soviets";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 72;
	
	operations_points = 1;
	
	event_owner = "USA";
	event_effects = {
		{ "RemoveAllOpponentInfluenceInEgpyt", 0 },
		{ "GainInfluenceInEgypt", 1 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Remove all USSR Influence in Egypt and add one US Influence.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 6,
		},
	};
}


g_twilight_cards["Shuttle Diplomacy"] = { 
	card_name = "Shuttle Diplomacy";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 73;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "RemoveThisCardFromDiscardPile", 0 },
		{ "PutThisCardInPlaySpecial", 0 },
		{ "DoNotDiscardThisCard", 0 },		
	};
	continuous_effects = {
		{
			effect = { "OpponentIgnoresBattlegroundInAsiaOrMiddleEast", 1 };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "WhenScoringAsiaOrMiddleEast", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlayAndDiscard", 1 },
			};
		},
	};
	event_text = "Play in front of US player. " ..
					"During the next scoring of the Middle East or Asia (whichever comes first), " ..
					"subtract one Battleground country from USSR total, " ..
					"then put this card in the discard pile. " ..
					"Does not count for Final Scoring at the end of Turn 10.";
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 5,
		},
	};
}


g_twilight_cards["The Voice Of America"] = { 
	card_name = "The Voice Of America";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 74;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "RemoveOpponentInfluenceFromNonEuropeMax2", 4 },
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Remove 4 USSR Influence from non-European countries. " ..
					"No more than 2 may be removed from any one country.";
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
			do_not_predict_headline = true,
		},
		usa = {
			headline = 10,
		},
	};
}


g_twilight_cards["Liberation Theology"] = { 
	card_name = "Liberation Theology";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 75;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "AddInfluenceInCentralAmericaMax2", 3 },
	};
	event_text = "Add 3 USSR Influence in Central America, no more than 2 per country.";
	
	ai = {
		ussr = {
			headline = 9,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Ussuri River Skirmish"] = { 
	card_name = "Ussuri River Skirmish";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 76;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "AddInfluenceInAsiaMax2", 4, condition={"IfYouHaveChinaCard",0} },
		{ "ClaimChinaCard", 0, condition={"IfYouDoNotHaveChinaCard",0} },
	};
	event_text = "If the USSR has \'The China Card\', claim it face up and available for play. " ..
					"If the US already has \'The China Card\', add 4 US Influence in Asia, no more than 2 per country.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 9,
		},
	};
}


g_twilight_cards["Ask Not What Your Country Can Do For You..."] = { 
	card_name = "Ask Not What Your Country Can Do For You...";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 77;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "MayDiscardEntireHand", 0 },
		{ "CommitPlayerDecision", 0 },
		{ "DrawCardForEachDiscard", 0 },
	};
	event_text = "US player may discard up to entire hand (including Scoring cards) " ..
					"and draw replacements from the deck. " ..
					"The number of cards discarded must be decided prior to drawing any replacements.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			play_after_action_round = 6,
			resolve_opponent_event_first = true,
			do_not_predict_headline = true,
		},
		usa = {
			headline = 8,
			play_event_before_action_round = 2,
		},
	};
}


g_twilight_cards["Alliance for Progress"] = { 
	card_name = "Alliance for Progress";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 78;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "GainVPForAllianceForProgress", 1 },
	};
	event_text = "US gains 1 VP for each US controlled Battleground country in Central America and South America.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 8,
		},
	};
}


g_twilight_cards["Africa Scoring"] = { 
	card_name = "Africa Scoring";
	card_type = "Scoring";
	stage = "Mid War";
	
	card_number = 79;
	
	scoring_region = "Africa";
	event_effects = {
		{ "ScoreAfrica", 0 },
	};
	event_text = "Both sides score:\nPresence: 1\nDomination: 4\nControl: 6\n" ..
					"+1 per controlled Battleground Country in Region";
	
	may_be_held = false;
}


g_twilight_cards["One Small Step..."] = { 
	card_name = "One Small Step...";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 80;
	
	operations_points = 2;
	
	event_owner = "Neutral";
	event_effects = {
		usageconditions = {
			{ "IfYouAreBehindOnSpaceRaceTrack", 0 },
		};
		{ "AdvanceSpaceRaceTrack", 2 },
	};

	event_text = "If you are behind on the Space Race Track, play this card to move your marker " ..
					"two boxes forward on the Space Rack Track, " ..
					"gaining the VP value of the second box only.";
	
	ai = {
		headline = 5,
			
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["South America Scoring"] = { 
	card_name = "South America Scoring";
	card_type = "Scoring";
	stage = "Mid War";
	
	card_number = 81;
	
	scoring_region = "South America";
	event_effects = {
		{ "ScoreSouthAmerica", 0 },
	};
	event_text = "Both sides score:\nPresence: 2\nDomination: 5\nControl: 6\n" ..
					"+1 per controlled Battleground Country in Region";

	may_be_held = false;
}


-- OPTIONAL
g_twilight_cards["Che"] = { 
	card_name = "Che";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 107;
	optional_card = true;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "MakeCoupAttemptInNonBattlegroundInAmericasOrAfrica", 3 },
		{ "MakeCoupAttemptInNonBattlegroundInAmericasOrAfrica", 3, condition={"IfYouDo",0}, },
	};
	event_text = "USSR may immediately make a Coup attempt using this card's Operations value " ..
					"against a non-battleground country in Central America, South America, or Africa. " ..
					"If the Coup removes any US Influence, USSR may make a second Coup attempt " ..
					"against a different target under the same restrictions.";
	
	ai = {
		ussr = {
			headline = 9,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


-- OPTIONAL
g_twilight_cards["Our Man In Tehran"] = { 
	card_name = "Our Man In Tehran";
	card_type = "Event";
	stage = "Mid War";
	
	card_number = 108;
	optional_card = true;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		usageconditions = {
			{ "IfYouControlMiddleEastCountry", 1 },
		};
		{ "CommitPlayerDecision", 0 },
		{ "MayDiscardTopOfDrawPile", 5 },
	};
	event_text = "If the US controls at least one Middle East country, " ..
					"the US player draws the top 5 cards from the draw pile. " ..
					"They may reveal and then discard any or all of these drawn cards " ..
					"without triggering the Event. " ..
					"Any remaining drawn cards are returned to the draw deck, " ..
					"and it is reshuffled.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
			do_not_predict_headline = true,
		},
		usa = {
			headline = 4,
		},
	};
}










--
-- LATE WAR
--



g_twilight_cards["Iranian Hostage Crisis"] = { 
	card_name = "Iranian Hostage Crisis";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 82;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "RemoveAllOpponentInfluenceInIran", 0 },
		{ "GainInfluenceInIran", 2 },
		{ "PauseForAnimationToMap", 0 },
		{ "PutThisCardInPlay", 0 },			
	};
	event_text = "Remove all US Influence in Iran. Add 2 USSR Influence in Iran.\n" ..
					"Doubles the effect of Terrorism card against US.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 7,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["The Iron Lady"] = { 
	card_name = "The Iron Lady";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 83;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "GainVictoryPoints", 1 },
		{ "OpponentGainsInfluenceInArgentina", 1 },
		{ "RemoveAllOpponentInfluenceInUK", 0 },
		{ "PauseForAnimationToMap", 0 },
		{ "PutThisCardInPlay", 0 },			
	};
	event_text = "US gains 1 VP.\n" ..
					"Add 1 USSR Influence in Argentina. Remove all USSR Influence from UK.\n" ..
					"Socialist Governments event no longer playable.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 6,
		},
	};
}


g_twilight_cards["Reagan Bombs Libya"] = { 
	card_name = "Reagan Bombs Libya";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 84;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		{ "GainVPForOpponentInfluenceInLibya", 2 },
	};
	event_text = "US gains 1 VP for every 2 USSR Influence in Libya.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 4,
		},
	};
}


g_twilight_cards["Star Wars"] = { 
	card_name = "Star Wars";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 85;
	
	operations_points = 2;
	pending_defcon_level = { -1, 0 };
	
	event_owner = "USA";
	event_effects = {
		usageconditions = {
			{ "IfUSIsAheadOnSpaceRaceTrack", 0 },
		};
		{ "CopyEventCardFromDiscardPile", 0 },		-- will RestorePendingDefconLevel
	};
	event_text = "If the US is ahead on the Space Race Track, " ..
					"play this card to search through the discard pile " ..
					"for a non-scoring card of your choice. " ..
					"Event occurs immediately.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			defcon_discard = true,
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 8,
		},
	};
}


g_twilight_cards["North Sea Oil"] = { 
	card_name = "North Sea Oil";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 86;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "SetActionRoundCount", 8 },
		{ "PutThisCardInPlay", 0 },			
	};
	event_text = "OPEC event is no longer playable.\n" ..
					"US may play 8 cards this turn.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 5,
		},
	};
}


g_twilight_cards["The Reformer"] = { 
	card_name = "The Reformer";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 87;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "AddInfluenceInEuropeMax2", 6, condition={"IfYouAreAheadOnVPTrack",0} },
		{ "AddInfluenceInEuropeMax2", 4, condition={"IfYouAreNotAheadOnVPTrack",0} },			
		{ "PutThisCardInPlay", 0, condition={"IfGlasnostIsNotInRemovedPile",0} },			
	};
	continuous_effects = {
		{
			effect = { "YouCannotCoupInEurope", 0 };
		},
	};
	event_text = "Add 4 Influence in Europe (no more than 2 per country). " ..
					"If USSR is ahead of US in VP, then 6 Influence may be added instead.\n" ..
					"USSR may no longer conduct Coup attempts in Europe.\n" ..
					"Improves effect of Glasnost event.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 9,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Marine Barracks Bombing"] = { 
	card_name = "Marine Barracks Bombing";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 88;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "RemoveAllOpponentInfluenceInLebanon", 0 },
		{ "PauseForAnimationToMap", 0 },
		{ "RemoveOpponentInfluenceInMiddleEast", 2 },			
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "Remove all US Influence in Lebanon plus remove 2 additional US Influence " ..
					"from anywhere in the Middle East.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 6,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Soviets Shoot Down KAL-007"] = { 
	card_name = "Soviets Shoot Down KAL-007";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 89;
	
	operations_points = 4;
	pending_defcon_level = { -1, -1 };
	
	event_owner = "USA";
	event_effects = {
		{ "RestorePendingDefconLevel", 0 },
		{ "DegradeDEFCONLevel", 1 },
		{ "GainVictoryPoints", 2 },
		{ "PlaceInfluenceOrAttemptRealignmentsWithThisCard", 4, condition={"IfYouControlSouthKorea",0} },			
	};
	event_text = "Degrade DEFCON one level. US gains 2 VP.\n" ..
					"If South Korea is US Controlled, then the US may place Influence " ..
					"or attempt Realignment as if they played a 4 Ops card.";
	remove_if_used_as_event = true;
	
	ai = {
		defcon_drop = true,
		
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 10,
		},
	};
}


g_twilight_cards["Glasnost"] = { 
	card_name = "Glasnost";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 90;
	
	operations_points = 4;
	
	event_owner = "USSR";
	event_effects = {
		{ "GainVictoryPoints", 2 },
		{ "ImproveDEFCONLevel", 1 },
		{ "PlaceInfluenceOrAttemptRealignmentsWithThisCard", 4, condition={"IfHasBeenPlayedTheReformer",0} },			
		{ "RemoveTheReformerFromPlay", 0 },
	};
	event_text = "USSR gains 2 VP.\n" ..
					"Improve DEFCON one level.\n" ..
					"If The Reformer is in effect, then the USSR may place Influence " ..
					"or attempt Realignments as if they played a 4 Ops card.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 9,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Ortega Elected in Nicaragua"] = { 
	card_name = "Ortega Elected in Nicaragua";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 91;
	
	operations_points = 2;
	pending_defcon_level = { 0, -1 };
	
	event_owner = "USSR";
	event_effects = {
		{ "RemoveAllOpponentInfluenceInNicaragua", 0 },
		{ "PauseForAnimationToMap", 0 },
		{ "MakeFreeCoupAttemptAdjacentToNicaragua", 0 },			
		{ "RestorePendingDefconLevel", 0 },
	};
	event_text = "Remove all US Influence from Nicaragua. " ..
					"Then USSR may make one free Coup attempt (with this card's Operations value) " ..
					"in a country adjacent to Nicaragua.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 5,
		},
		usa = {
			--defcon_ops = true,
			-- TODO: handle defcon when US has influence in Cuba
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Terrorism"] = { 
	card_name = "Terrorism";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 92;
	
	operations_points = 2;
	
	event_owner = "Neutral";
	event_effects = {
		{ "CommitPlayerDecision", 0 },
		{ "OpponentDiscardsRandomCard", 0 },
		{ "OpponentDiscardsRandomCard", 0, condition={"IfUSSRAndHasBeenPlayedIranianHostageCrisis",0} },
	};
	event_text = "Opponent must randomly discard one card. " ..
					"If played by USSR and Iranian Hostage Crisis is in effect, " ..
					"the US player must randomly discard two cards.\n" ..
					"(Events on discards do not occur.)";
	
	ai = {
		ussr = {
			headline = 7,
		},
		usa = {
		},
	};
}


g_twilight_cards["Iran-Contra Scandal"] = { 
	card_name = "Iran-Contra Scandal";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 93;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "PutThisCardInPlay", 1 },			
	};
	continuous_effects = {
		{
			effect = { "OpponentRealignmentRollsAreReducedBy", 1 };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "All US Realignment rolls have a -1 die roll modifier for the remainder of the turn.";
	remove_if_used_as_event = true;
	
	ai = {
		headline = 4,
			
		ussr = {
			play_event_before_action_round = 0,
		},
		usa = {
			play_after_action_round = 3,
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["Chernobyl"] = { 
	card_name = "Chernobyl";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 94;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "ChooseOneRegion", 0 },			
		{ "PutThisCardInPlayWithRegionChoice", 0 },			
	};
	continuous_effects = {
		{
			effect = { "OpponentMayNotPlaceInfluenceInSelectedRegion", 0 };
		},
	};
	triggered_effects = {
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "The US player may designate one Region. " ..
					"For the remainder of the turn the USSR may not add additional Influence to that Region " ..
					"by the play of Operations Points via placing Influence.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			play_after_action_round = 5,
			resolve_opponent_event_last = true,
			do_not_predict_headline = true,
		},
		usa = {
			headline = 7,
			play_event_before_action_round = 2,
		},
	};
}

g_twilight_cards["Latin American Debt Crisis"] = { 
	card_name = "Latin American Debt Crisis";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 95;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "OpponentMayDiscardCardWithOpsPoints", 3 },
		{ "DoubleInfluenceInSouthAmericanCountries", 2, condition={"IfYouDoNot",0}, },
	};
	event_text = "Unless the US Player immediately discards a \'3\' or greater Operations card, " ..
					"double USSR Influence in two countries in South America.";
	--remove_if_used_as_event = true;
	remove_if_used_as_event_before_version = 6;
	
	ai = {
		ussr = {
			headline = 7,
		},
		usa = {
			resolve_opponent_event_first = true,
		},
	};
}


g_twilight_cards["Tear Down This Wall"] = { 
	card_name = "Tear Down This Wall";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 96;
	
	operations_points = 3;
	pending_defcon_level = { -1, 0 };
	
	event_owner = "USA";
	event_effects = {
		{ "RemoveWillyBrandtFromPlay", 0 },
		{ "GainInfluenceInEastGermany", 3 },
		{ "PauseForAnimationToMap", 0 },
		{ "MakeFreeCoupOrRealignmentAttemptsInEurope", 0 },			
		{ "RestorePendingDefconLevel", 0 },
		{ "PutThisCardInPlay", 0, condition={"IfWillyBrandtIsNotInRemovedPile",0} },
	};
	event_text = "Cancels/prevent Willy Brandt.\n" ..
					"Add 3 US Influence in East Germany.\n" ..
					"Then US may make a free Coup attempt or Realignment rolls " ..
					"in Europe using this card's Ops Value.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			defcon_ops = true,
			resolve_opponent_event_first = true,
			do_not_predict_headline = true,
		},
		usa = {
			headline = 9,
		},
	};
}


g_twilight_cards["An Evil Empire"] = { 
	card_name = "An Evil Empire";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 97;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "RemoveFlowerPowerFromPlay", 0 },
		{ "GainVictoryPoints", 1 },
		{ "PutThisCardInPlay", 0, condition={"IfFlowerPowerIsNotInRemovedPile",0} },
	};
	event_text = "Cancels/Prevents Flower Power.\n" ..
					"US gains 1 VP.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_last = true,
		},
		usa = {
			headline = 6,
		},
	};
}


g_twilight_cards["Aldrich Ames Remix"] = { 
	card_name = "Aldrich Ames Remix";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 98;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "CommitPlayerDecision", 0 },
		--{ "OpponentRevealsHand", 0 },			
		{ "DiscardCardFromOpponentHand", 0 },			
	};
	event_text = "US player exposes his hand to USSR player for remainder of turn. " ..
					"USSR then chooses one card from US hand; this card is discarded.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 9,
			--play_event_before_action_round = 2,
		},
		usa = {
			play_after_action_round = 4,
			resolve_opponent_event_first = true,
		},
	};
}

g_twilight_cards["Pershing II Deployed"] = { 
	card_name = "Pershing II Deployed";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 99;
	
	operations_points = 3;
	
	event_owner = "USSR";
	event_effects = {
		{ "GainVictoryPoints", 1 },
		{ "RemoveOpponentInfluenceInWesternEuropeMax1", 3 },			
		{ "PauseForAnimationToMap", 0 },
	};
	event_text = "USSR gains 1 VP.\n" ..
					"Remove 1 US Influence from up to three countries in Western Europe.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 8,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


g_twilight_cards["Wargames"] = { 
	card_name = "Wargames";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 100;
	
	operations_points = 4;
	
	event_owner = "Neutral";
	event_effects = {
		usageconditions = {
			{ "IfDefconLevelIs", 2 },
		};
		{ "ResolveWargames", 6 },
	};
	event_text = "If DEFCON Status 2, you may immediately end the game (without Final Scoring Phase) " ..
					"after giving opponent 6 VPs.\n" ..
					"How about a nice game of chess?";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
		},
		usa = {
		},
	};
}


g_twilight_cards["Solidarity"] = { 
	card_name = "Solidarity";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 101;
	
	operations_points = 2;
	
	event_owner = "USA";
	event_effects = {
		usageconditions = {
			{ "IfHasBeenPlayedJohnPaulIIElectedPope", 0 },
		};
		{ "GainInfluenceInPoland", 3 },
		{ "PauseForAnimationToMap", 0 },
		{ "RemoveJohnPaulIIElectedPopeFromPlay", 0 },
	};
	event_text = "Playable as an event only if John Paul II Elected Pope is in effect.\n" ..
					"Add 3 US Influence in Poland.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 6,
		},
	};
}


g_twilight_cards["Iran-Iraq War"] = { 
	card_name = "Iran-Iraq War";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 102;
	
	operations_points = 2;
	
	event_owner = "Neutral";
	event_effects = {
		{ "WarInIranOrIraq", 2 + (2 * 256) },
	};
	event_text = "Iran or Iraq invades the other (player's choice). " ..
					"Roll one die and subtract 1 for every opponent-controlled country adjacent to target of invasion. " ..
					"Player Victory on modified die roll of 4-6. " ..
					"Player adds 2 to Military Ops Track\n" ..
					"Effects of Victory: Player gains 2 VP and replaces opponent's Influence in target country with his own.";
	remove_if_used_as_event = true;
	
	ai = {
		headline = 7,
		
		ussr = {
		},
		usa = {
		},
	};
}


-- OPTIONAL
g_twilight_cards["Yuri and Samantha"] = { 
	card_name = "Yuri and Samantha";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 109;
	optional_card = true;
	
	operations_points = 2;
	
	event_owner = "USSR";
	event_effects = {
		{ "PutThisCardInPlay", 1 },			
	};
	triggered_effects = {
		{
			conditions = {
				{ "WhenOpponentMakesCoupAttempt", 0 },
			};
			triggereffect = {
				{ "TriggerAnnounceCardInPlay", 0 },
				{ "TriggerGainVictoryPoints", 1 },
			};
		},
		{
			conditions = {
				{ "AtEndOfTurn", 0 },
			};
			triggereffect = {
				{ "TriggerRemoveThisCardFromPlay", 1 },
			};
		},
	};
	event_text = "USSR receives 1 VP for each US coup attempt made for the remainder of the current turn.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			headline = 4,
		},
		usa = {
			resolve_opponent_event_last = true,
		},
	};
}


-- OPTIONAL
g_twilight_cards["AWACS Sale to Saudis"] = { 
	card_name = "AWACS Sale to Saudis";
	card_type = "Event";
	stage = "Late War";
	
	card_number = 110;
	optional_card = true;
	
	operations_points = 3;
	
	event_owner = "USA";
	event_effects = {
		{ "GainInfluenceInSaudiArabia", 2 },
		{ "PauseForAnimationToMap", 0 },
		{ "PutThisCardInPlay", 0 },
	};
	event_text = "US receives 2 Influence in Saudi Arabia. " ..
					"Muslim Revolution may no longer be played as an event.";
	remove_if_used_as_event = true;
	
	ai = {
		ussr = {
			resolve_opponent_event_first = true,
		},
		usa = {
			headline = 7,
		},
	};
}






g_twilight_cards["1 Op AI Proxy"] = { 
	card_name = "1 Op AI Proxy";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 201;
	
	operations_points = 1;
	
	event_owner = "Neutral";
	event_text = "1 Op Proxy.  For AI Use Only.";
}

g_twilight_cards["2 Op AI Proxy"] = { 
	card_name = "2 Op AI Proxy";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 202;
	
	operations_points = 2;
	
	event_owner = "Neutral";
	event_text = "2 Op Proxy.  For AI Use Only.";
}

g_twilight_cards["3 Op AI Proxy"] = { 
	card_name = "3 Op AI Proxy";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 203;
	
	operations_points = 3;
	
	event_owner = "Neutral";
	event_text = "3 Op Proxy.  For AI Use Only.";
}

g_twilight_cards["4 Op AI Proxy"] = { 
	card_name = "4 Op AI Proxy";
	card_type = "Event";
	stage = "Early War";
	
	card_number = 204;
	
	operations_points = 4;
	
	event_owner = "Neutral";
	event_text = "4 Op Proxy.  For AI Use Only.";
}