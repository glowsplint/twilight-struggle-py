from copy import deepcopy

from game_mechanics import Game
from twilight_enums import Side, InputType, CardAction
from twilight_map import MapRegion, CountryInfo
from twilight_cards import CardInfo

class UI:

    help = '''
The following commands are available:
?           Displays this help text.
m           Lists all possible moves, along with their respective IDs.
m <ID>      Makes a move.
m commit    Commits all moves made.
s           Displays the overall game state.
s ?         Shows help on game state queries.
c ?         Shows help on card information queries.
dbg ?       Shows help on debugging.

new         Start a new game.
quit        Exit the game.
'''

    ussr_prompt = '----- USSR Player: -----'
    us_prompt = '----- US Player: -----'
    commit_options = ["yes", "no"]

    def __init__(self):
        self.game_rollback = None
        self.game = Game()
        self.debug_save = None
        self.options = dict()

    @property
    def input_state(self) -> Game.Input:
        return self.game.input_state

    @property
    def awaiting_commit(self):
        return self.input_state.complete

    def get_options(self):
        self.options = dict()
        if self.game.input_state.state == InputType.SELECT_CARD_ACTION:
            for opt in self.input_state.available_options:
                self.options[CardAction[opt].value] = opt
        elif self.game.input_state.state == InputType.SELECT_CARD_IN_HAND:
            for opt in self.input_state.available_options:
                self.options[CardInfo.ALL[opt].card_index] = opt
        elif self.game.input_state.state == InputType.SELECT_COUNTRY:
            for opt in self.input_state.available_options:
                self.options[CountryInfo.ALL[opt].country_index] = opt
        elif self.game.input_state.state == InputType.SELECT_MULTIPLE:
            for i, opt in enumerate(self.input_state.available_options):
                self.options[i] = opt
        elif self.game.input_state.state == InputType.SELECT_DISCARD_OPTIONAL:
            for opt in self.input_state.available_options:
                if opt == Game.Input.OPTION_DO_NOT_DISCARD:
                    self.options[0] = opt
                else:
                    self.options[CardInfo.ALL[opt].card_index] = opt

    def prompt(self):

        if self.input_state.side == Side.USSR:
            print(UI.ussr_prompt)
        elif self.input_state.side == Side.US:
            print(UI.us_prompt)

        print(self.input_state.prompt)

        # print the already selected options
        first = True
        for k, v in self.input_state.selection.items():
            for _i in range(v):
                if first:
                    print("You have selected", k, end="")
                    first = False
                else:
                    print(",", k, end="")
        if not first:
            print()  # newline

        if self.input_state.reps_unit:
            print(
                f"Remaining {self.input_state.reps_unit}: {self.input_state.reps}")

        if self.awaiting_commit:
            print("Commit your actions? (Yes/No)")
        else:
            print("Available options:")
            for k, v in self.options.items():
                print(f'{k:5} {v}')

    def run(self):

        print('Initalising game..')
        while True:

            user_choice = input("> ").split(" ", 1)

            if len(user_choice) == 1:
                user_choice.append('')

            # parse the input
            if len(user_choice) == 0 or user_choice[0] == "?":
                print(UI.help)

            elif user_choice[0] == "quit" or user_choice[0] == "exit" or user_choice[0].lower() == 'q':
                break

            elif user_choice[0].lower() == 'new':
                print("Starting new game.")
                self.game.start()
                self.game_rollback = deepcopy(self.game)
                self.get_options()
                self.prompt()
                
            elif user_choice[0].lower() == 'dbg':
                self.parse_debug(user_choice[1])

            elif user_choice[0].lower() == 'c':
                self.parse_card(user_choice[1])

            elif user_choice[0].lower() == 's':
                self.parse_state(user_choice[1])

            elif user_choice[0].lower() == 'm':
                self.parse_move(user_choice[1])

            else:
                print('Invalid command. Enter ? for help.')

    def parse_move(self, comd):

        if comd == '':
            self.prompt()
            # Here you want to call some function to get all possible moves.
            # Each move should be deterministically assigned an ID (so it
            # can be referenced later).
        else:
            comd = comd.lower()

            if self.awaiting_commit:
                if "yes".startswith(comd):
                    self.game.stage_complete()
                    self.game_rollback = deepcopy(self.game)
                    self.get_options()
                    self.prompt()
                elif "no".startswith(comd):
                    self.game = self.game_rollback
                    self.game_rollback = deepcopy(self.game)
                    print("Actions undone.")
                    self.get_options()
                    self.prompt()
                else:
                    print("Invalid input.")
                    self.prompt()

            else:

                # this counts how many strings in the options start with the input
                matched = None
                if comd.isdigit():
                    if int(comd) in self.options:
                        matched = self.options[int(comd)]
                else:
                    for opt in self.options.values():
                        if opt.lower().startswith(comd):
                            if matched:
                                # there is more than one match
                                print("Error: multiple matching options!")
                                self.prompt()
                                return
                            matched = opt

                if not matched:
                    print("Error: no matching option!")
                    self.prompt()
                    return

                print(f"Selected: {matched}")
                self.input_state.recv(matched)
                self.get_options()
                self.prompt()

    help_card = '''
c           Display a list of cards in the current player's hand.
c <ID#>     Display information about the card with the given ID number.
c dis       Display a list of cards in the discard pile
c rem       Display a list of removed cards.
c dec       Returns the number of cards in the draw deck.
'''
    def parse_card(self, comd):

        if comd == '':
            print(
                f'Listing {len(self.game.hand[self.input_state.side])} cards in hand.')
            for c in sorted(self.game.hand[self.input_state.side]):
                print(c)
        elif comd == '?':
            print(UI.help_card)
        elif comd == 'opp':
            print(
                f'Cards in opponent hand: {len(self.game.hand[self.input_state.side.opp])}')
        elif comd == 'dis':
            print(f'Listing {len(self.game.discard_pile)} discarded cards.')
            for c in sorted(self.game.discard_pile):
                print(c)
        elif comd == 'rem':
            print(f'Listing {len(self.game.removed_pile)} removed cards.')
            for c in sorted(self.game.removed_pile):
                print(c)
        elif comd == 'dec':
            print(f'Cards in draw pile: {len(self.game.draw_pile)}.')
        else:
            print('Invalid command. Enter ? for help.')

    help_state = '''
s <eu|as|me|af|na|sa>   Displays the scoring state and country data for the given region.
'''

    def parse_state(self, comd):
        if comd == '':
            print('=== Game state ===')
            print(f'VP status: {self.game.vp_track}')
            print('Unimplemented')
        elif comd == '?':
            print(UI.help_state)
        else:
            # remember to check if comd is a valid ID
            region = MapRegion.fromStr(comd)
            print(f'State of {region.name}:')
            for n in sorted(CountryInfo.REGION_ALL[region]):
                print(self.game.map[n].get_state_str())
            print('Score state currently unimplemented')
    
    help_debug = '''
dbg                                 Starts debugging mode.
dbg inf set <country> <us>:<ussr>   Sets the influence in a particular country.
dbg card <card_name> <side>         Triggers the card event as the given side.
dbg rollback                        Restores the state before debugging started.
'''        
    def parse_debug(self, comd):
    
        
        if not comd:
            print("Debugging mode started.")
            self.debug_save = (deepcopy(self.game), deepcopy(self.game_rollback))
            return
        elif comd == '?':
            print(UI.help_debug)
            return
        elif not self.debug_save:
            print("Error: Not in debug mode.")
            return
        user_choice = comd.split(' ')
        if user_choice[0] == 'inf':
            if len(user_choice) != 4:
                print('Invalid command. Enter ? for help.')
            elif user_choice[2] not in CountryInfo.ALL:
                print('Invalid country name.')
            elif user_choice[1] == 'set':
                inf = user_choice[3].split(':')
                if len(inf) != 2:
                    print('Invalid command. Enter ? for help.')
                else:
                    self.game.map[user_choice[2]].influence[Side.US] = int(inf[0])
                    self.game.map[user_choice[2]].influence[Side.USSR] = int(inf[1])
        elif user_choice[0] == 'card':
            if len(user_choice) != 3:
                print('Invalid command. Enter ? for help.')
            elif user_choice[1] not in CardInfo.ALL:
                print('Invalid card name.')
            elif user_choice[2].lower() not in ['us', 'ussr']:
                print('Invalid side.')
            else:
                self.game.stage_list.append(lambda: print(f'\n=== {user_choice[1]} event complete. ===\nThe final prompt may print again. You should rollback.\n'))
                self.game.card_function_mapping[user_choice[1]](self.game, Side.fromStr(user_choice[2]))
                self.get_options()
                self.prompt()
        elif user_choice[0] == 'rollback':
            print("Restoring pre-debugging state.")
            self.game = self.debug_save[0]
            self.game_rollback = self.debug_save[1]
            self.get_options()
            self.prompt()
        else:
            print('Invalid command. Enter ? for help.')
          

