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

    def __init__(self, game_instance):
        self.game = game_instance

    @staticmethod
    def ask_for_input(expected_number_of_arguments: int, rejection_msg: str):
        while True:
            raw_input = input('> ').split(
                ',', expected_number_of_arguments - 1)
            if raw_input[0].lower() == 'quit' or raw_input[0].lower() == 'exit' or raw_input[0].lower() == 'q':
                return
            elif len(raw_input) == 0 or raw_input[0] == '?':
                print(UI.help)
            elif len(raw_input) == expected_number_of_arguments:
                return raw_input
            print(rejection_msg)

    def run(self):

        print('Initalising game..')
        while True:

            if len(self.game.stage_list) > 0:
                if self.game.stage_list[-1]() == None:
                    self.game.stage_list.pop()
                    continue
            else:
                print('End of game.')
                break

            user_choice = UI.ask_for_input(1)
            if user_choice == None:
                break

            if len(user_choice) == 1:
                user_choice.append('')

            # parse the input
            if user_choice[0].lower() == 'new':
                print('Unimplemented')

            elif user_choice[0].lower() == 'c':
                UI.parse_card(user_choice[1])

            elif user_choice[0].lower() == 's':
                UI.parse_state(user_choice[1])

            elif user_choice[0].lower() == 'm':
                UI.parse_move(user_choice[1])

            else:
                print('Invalid command. Enter ? for help.')

    @staticmethod
    def parse_move(comd):

        if comd == '':
            print('Listing all moves.')
            print('Unimplemented')
            # Here you want to call some function to get all possible moves.
            # Each move should be deterministically assigned an ID (so it
            # can be referenced later).
        elif comd == 'commit':
            print('Game state advancing.')
            # this is where you tell the game engine to lock in the currently
            # selected move.
            print('Unimplemented')
        else:
            print('Making move ID %s' % comd)
            # check moves to find the corresponding ID. If it's not found print
            # an error message.
            # Then, tell the game engine to make a temp move.
            # or for now, we can just actually make the move with no takeback
            # which means the commit command won't do anything.
            print('Unimplemented')

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
