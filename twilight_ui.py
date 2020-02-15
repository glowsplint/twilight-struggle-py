from game_mechanics import *
from functools import reduce
from copy import deepcopy

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

new         Start a new game.
quit        Exit the game.
'''

    '''ask_for_input is our primary means of getting input from the user.'''

    ussr_prompt = '----- USSR Player: -----'
    us_prompt = '----- US Player: -----'
    commit_options = ["yes", "no"]

    def __init__(self):
        self.game_rollback = None
        self.game = Game()

    @staticmethod
    def ask_for_input(expected_number_of_arguments: int, rejection_msg: str, can_be_less=True):
        while True:
            if can_be_less:
                raw_input = input('> ').split(
                    ',')
                if raw_input[0].lower() == 'quit' or raw_input[0].lower() == 'exit' or raw_input[0].lower() == 'q':
                    return
                elif len(raw_input) == 0 or raw_input[0] == '?':
                    print(UI.help)
                elif len(raw_input) <= expected_number_of_arguments:
                    return raw_input
            else:
                raw_input = input('> ').split(
                    ',', expected_number_of_arguments - 1)
                if raw_input[0].lower() == 'quit' or raw_input[0].lower() == 'exit' or raw_input[0].lower() == 'q':
                    return
                elif len(raw_input) == 0 or raw_input[0] == '?':
                    print(UI.help)
                elif len(raw_input) == expected_number_of_arguments:
                    return raw_input
            print(rejection_msg)

    @property
    def input_state(self) -> Game.Input:
        return self.game.input_state

    @property
    def awaiting_commit(self):
        return not self.game.input_state.reps

    def prompt(self):

        if self.input_state.side == Side.USSR:
            print(UI.ussr_prompt)
        elif self.input_state.side == Side.US:
            print(UI.us_prompt)

        print(self.input_state.prompt)

        # print the already selected options
        first = True
        for k, v in self.input_state.selection.items():
            for i in range(v):
                if first:
                    print("You have selected", k, end="")
                    first = False
                else:
                    print(",", k, end="")
        if not first: print() # newline

        if self.input_state.reps_unit:
            print(f"Remaining {self.input_state.reps_unit}: {self.input_state.reps}")

        if self.awaiting_commit:
            print("Commit your actions? (Yes/No)")
        else:
            print(f"Options: {', '.join(sorted(self.input_state.available_options))}")

    def run(self):

        print('Initalising game..')
        while True:

            user_choice = input("> ").split(" ", 1)

            if len(user_choice) == 1:
                user_choice.append('')

            # parse the input
            if len(user_choice) == 0 or user_choice[0] == "?":
                print(UI.help)

            elif user_choice[0] == "quit" or user_choice[0] == "exit":
                break

            elif user_choice[0].lower() == 'new':
                print("Starting new game.")
                self.game.start()
                self.game_rollback = deepcopy(self.game)
                self.prompt()

            elif user_choice[0].lower() == 'c':
                UI.parse_card(user_choice[1])

            elif user_choice[0].lower() == 's':
                UI.parse_state(user_choice[1])

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
                    self.game_rollback = deepcopy(self.game)
                    self.game.stage_complete()
                    self.prompt()
                elif "no".startswith(comd):
                    self.game = self.game_rollback
                    print("Actions undone.")
                    self.prompt()
                else:
                    print("Invalid input.")
                    self.prompt()

            else:

                # this counts how many strings in the options start with the input
                matched = None
                for opt in self.input_state.available_options:
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

                print(f"Selected: {matched}.")
                self.input_state.recv(matched)
                self.prompt()

    help_card = '''
c           Display a list of cards in the current player's hand.
c <ID#>     Display information about the card with the given ID number.
c dis       Display a list of cards in the discard pile
c rem       Display a list of removed cards.
c dec       Returns the number of cards in the draw deck.
'''
    @staticmethod
    def parse_card(comd):

        if comd == '':
            print('Listing cards in hand.')
            print('Unimplemented')
        elif comd == '?':
            print(UI.help_card)
        elif comd == 'opp':
            print('Cards in opponent\'s hand: %d' %
                  1)  # TODO make it based on state
            print('Unimplemented')
        elif comd == 'dis':
            print('Listing %d discarded cards.' % len(discard_pile))
            for c in discard_pile:
                print(c)
        elif comd == 'rem':
            print('Listing %d removed cards.' % len(removed_pile))
            for c in removed_pile:
                print(c)
        elif comd == 'dec':
            print('Cards in draw pile: %d.' % len(draw_pile))
        else:
            print('Invalid command. Enter ? for help.')

    help_state = '''
s <eu|as|me|af|na|sa>   Displays the scoring state and country data for the given region.
'''
    @staticmethod
    def parse_state(comd):
        if comd == '':
            print('=== Game state ===')
            print('VP status: %d' % Game.main.vp_track)
            print('Unimplemented')
        elif comd == '?':
            print(UI.help_state)
        else:
            # remember to check if comd is a valid ID
            print('State of %s:' % comd)
            print('Unimplemented')
