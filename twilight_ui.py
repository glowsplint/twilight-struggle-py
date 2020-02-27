import random

from os import path
from copy import deepcopy
from datetime import datetime
from textwrap import wrap

from game_mechanics import Game
from twilight_enums import Side, InputType, CardAction
from twilight_map import MapRegion, CountryInfo
from twilight_cards import Card
from twilight_input_output import Input


class UI:

    help = '''
The following commands are available:
?               Displays this help text.
s               Displays the overall game state.
m ?             Shows help on move queries.
s ?             Shows help on game state queries.
c ?             Shows help on card information queries.
dbg ?           Shows help on debugging.
rng on|off      Toggles automatic random number generation (rng off for debugging).
commit on|off   Toggles commit prompts.
log on|off      Toggles game logging.
load <filename> Loads <filename> from the log directory.

new             Start a new game.
quit            Exit the game.
'''

    ussr_prompt = '----- USSR Player: -----'
    us_prompt = '----- US Player: -----'
    rng_prompt = '----- RNG: -----'
    left_margin_big = 25
    left_margin_small = 15

    def __init__(self):
        self.game_lookahead = None
        self.game_rollback = None
        self.game = Game()
        self.debug_save = None
        self.options = dict()
        self.auto_rng = True
        self.auto_commit = True

        self.game_in_progress = False

        self.temp_log = []
        self.logging = False
        self.log_filepath = None

    @property
    def input_state(self) -> Input:
        return self.game.input_state

    @property
    def awaiting_commit(self):
        return self.game_lookahead

    def log_generate_filepath(self):
        self.log_filepath = f'log{path.sep}game-{datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S-UTC")}.tsg'

    def log_write_out(self):
        if not self.temp_log:
            return
        out = '\n'.join(self.temp_log) + '\n'
        with open(self.log_filepath, 'a') as f:
            f.write(out)
        self.temp_log.clear()

    def new_game(self):
        if self.logging:
            self.log_generate_filepath()
        self.game_in_progress = True
        self.game.start()
        self.advance_game()

    def advance_game(self):
        if self.auto_commit and self.logging:
            self.log_write_out()
        self.game.stage_complete()
        while not self.game.input_state:
            self.game.stage_complete()

    def commit(self):
        if self.logging:
            self.log_write_out()
        self.game_lookahead = None
        self.advance_game()
        self.game_rollback = deepcopy(self.game)
        self.game_state_changed()

    def revert(self):
        if self.logging:
            self.temp_log.clear()
        self.game = self.game_rollback
        self.game_lookahead = None
        self.game_rollback = deepcopy(self.game)
        self.game_state_changed()

    def move(self, move):
        self.game.input_state.recv(move)
        if self.logging:
            self.temp_log.append(move)

    def generate_options(self):
        if self.game.input_state.state == InputType.SELECT_CARD_ACTION:
            self.options = {CardAction[opt].value: opt
                            for opt in self.input_state.available_options}
        elif self.game.input_state.state == InputType.SELECT_CARD:
            self.options = {Card.ALL[opt].card_index: opt
                            for opt in self.input_state.available_options}
        elif self.game.input_state.state == InputType.SELECT_COUNTRY:
            self.options = {CountryInfo.ALL[opt].country_index: opt
                            for opt in self.input_state.available_options}
        elif self.game.input_state.state == InputType.SELECT_MULTIPLE:
            self.options = {i: opt
                            for i, opt in
                            enumerate(self.input_state.available_options)}
        elif self.game.input_state.state == InputType.ROLL_DICE:
            self.options = {i: opt
                            for i, opt in
                            enumerate(self.input_state.available_options)}

        if self.game.input_state.option_stop_early:
            self.options[0] = self.game.input_state.option_stop_early

    def game_state_changed(self, prompt=True):

        while True:

            if self.auto_rng:
                # automatically run rng
                if self.game.input_state.side == Side.NEUTRAL:
                    if self.game.input_state.complete:
                        # done with the rng, continue on to the next stage
                        self.advance_game()
                        self.game_rollback = deepcopy(self.game)
                    else:
                        choices = list(self.game.input_state.available_options)
                        c = random.choice(choices)
                        # process the input
                        self.move(c)
                    continue

            # see if this stage is done
            if self.game.input_state.complete:

                if self.auto_commit:
                    self.advance_game()
                    continue

                else:
                    # We will see what the next input required is.
                    self.game_lookahead = deepcopy(self.game)
                    self.game_lookahead.stage_complete()
                    while not self.game_lookahead.input_state:
                        self.game_lookahead.stage_complete()

                    if self.game.input_state.side == self.game_lookahead.input_state.side:
                        # The same player is up for input again. Don't ask for commit.
                        self.game_lookahead = None
                        self.advance_game()
                        continue
                    else:
                        break

            # if we get here it's time for player input. We will break at the end.
            self.generate_options()

            # time for player input
            break

        if prompt:
            self.prompt()

    def prompt(self):

        if self.input_state.side == Side.USSR:
            print(UI.ussr_prompt)
        elif self.input_state.side == Side.US:
            print(UI.us_prompt)
        elif self.input_state.side == Side.NEUTRAL:
            print(UI.rng_prompt)

        print(self.input_state.prompt)

        # print the already selected options
        first = True
        for k, v in self.input_state.selection.items():
            for _i in range(v):
                if first:
                    print('You have selected', k, end='')
                    first = False
                else:
                    print(',', k, end='')
        if not first:
            print()  # newline

        if self.input_state.reps_unit:
            print(
                f'Remaining {self.input_state.reps_unit}: {self.input_state.reps}')

        if self.awaiting_commit:
            print('Commit your actions? (Yes/No)')
        else:
            print('Available options:')
            # if self.input_state.state == InputType.ROLL_DICE:
            #     for v in sorted(self.options.values()):
            #         print(v)
            # else:
            for k, v in sorted(self.options.items()):
                print(f'{k:5} {v}')

    def run(self):

        print('Initalising game.')
        while True:

            user_choice = input('> ').split(' ', 1)

            if len(user_choice) == 1:
                user_choice.append('')

            # parse the input
            if len(user_choice) == 0 or user_choice[0] == '?':
                print(UI.help)

            elif user_choice[0] == 'quit' or user_choice[0] == 'exit' or user_choice[0].lower() == 'q':
                if self.logging:
                    self.log_write_out()
                break

            elif user_choice[0].lower() == 'new':
                if self.game_in_progress:
                    print('Game already in progress.')
                    continue
                print('Starting new game.')
                self.new_game()
                self.game_rollback = deepcopy(self.game)
                self.game_state_changed()

            elif user_choice[0].lower() == 'dbg':
                self.parse_debug(user_choice[1])

            elif user_choice[0].lower() == 'rng':
                if user_choice[1].lower() == 'on':
                    self.auto_rng = True
                elif user_choice[1].lower() == 'off':
                    self.auto_rng = False
                else:
                    print('Invalid command. Enter ? for help.')

            elif user_choice[0].lower() == 'commit':
                if user_choice[1].lower() == 'on':
                    self.auto_commit = True
                elif user_choice[1].lower() == 'off':
                    self.auto_commit = False
                else:
                    print('Invalid command. Enter ? for help.')

            elif user_choice[0].lower() == 'log':
                self.parse_log(user_choice[1])

            elif user_choice[0].lower() == 'load':
                self.parse_load(user_choice[1])

            elif user_choice[0].lower() == 'c':
                self.parse_card(user_choice[1])

            elif user_choice[0].lower() == 's':
                self.parse_state(user_choice[1])

            elif user_choice[0].lower() == 'm':
                self.parse_move(user_choice[1])

            else:
                print('Invalid command. Enter ? for help.')

    help_move = '''
m                   Lists all possible moves, along with their respective enum.
m <name|enum>       Makes the move with the name or with the enum. The name can be
                    abbreviated to the first characters as long as it is unambiguous.
m <m1 m2 m3 ...>    Makes multiple moves in order m1, m2, m3, ...
'''
    def parse_move(self, comd):

        if not self.game_in_progress:
            print('Game not in progress.')
            return

        if not comd:  # empty string
            self.prompt()
            # Here you want to call some function to get all possible moves.
            # Each move should be deterministically assigned an ID (so it
            # can be referenced later).
        elif comd == '?':
            print(UI.help_move)

        else:
            comd = comd.lower()

            if self.awaiting_commit:
                if 'yes'.startswith(comd):
                    self.commit()
                elif 'no'.startswith(comd):
                    print('Actions undone.')
                    self.revert()
                else:
                    print('Invalid input.')
                    self.prompt()

            else:
                # check for multiple move entry
                moves = comd.split()[:self.input_state.reps]
                for m in moves:

                    # this counts how many strings in the options start with the input
                    matched = None
                    ambiguous = False
                    if m.isdigit():
                        if int(m) in self.options:
                            matched = self.options[int(m)]
                    else:
                        for opt in self.options.values():
                            if opt.lower().startswith(m):
                                if matched:
                                    # there is more than one match
                                    ambiguous = True
                                    break
                                matched = opt

                    if not matched:
                        print(f'Error: no matching option for {m}!')
                        break
                    if ambiguous:
                        print(f'Error: multiple matching options for {m}!')
                        break

                    print(f'Selected: {matched}')
                    self.move(matched)
                    self.game_state_changed(prompt=False)
                self.prompt()

    help_card = '''
c               Display a list of cards in the current player's hand.
c <name|ID#>    Display information about the card with the given name or card index.
c opp           Returns the number cards in the opponent's hand.
c dis           Display a list of cards in the discard pile.
c rem           Display a list of removed cards.
c dec           Returns the number of cards in the draw deck.
'''
    def parse_card(self, comd):

        if not self.game_in_progress:
            print('Game not in progress.')
            return

        if comd == '':
            print(
                f'Listing {len(self.game.hand[self.input_state.side])} cards in hand.')
            for c in sorted(self.game.hand[self.input_state.side]):
                print(f'{Card.ALL[c].card_index:5} {c}')
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
            matched = None
            ambiguous = False

            def _print_card_info(comd, text: bool = True):
                if not text:
                    items = Card.INDEX[int(comd)].__dict__.items()
                else:
                    items = Card.ALL[matched].__dict__.items()

                print(f'Displaying information on card {comd}:')
                for k, v in items:
                    v = wrap(str(v), width=110)
                    indent = '\n'+(UI.left_margin_big+1)*' '
                    v = indent.join(v)
                    if str(v):
                        print(f'{k:>{UI.left_margin_big}} {v}')

            if comd.isdigit():
                if int(comd) in Card.INDEX.keys():
                    _print_card_info(comd, text=False)
            else:
                for opt in Card.ALL.keys():
                    if opt.lower().startswith(comd):
                        if matched:
                            ambiguous = True
                            break
                        matched = opt
                if ambiguous:
                    print(f'Error: multiple matching options for {comd}!')
                elif matched:
                    _print_card_info(matched, text=True)
                else:
                    print('Invalid command. Enter ? for help.')

    help_state = '''
s <eu|as|me|af|na|sa>   Displays the scoring state and country data for the given region.
s turn                  Displays information on the current turn and action round
'''

    def parse_state(self, comd):

        if not self.game_in_progress:
            print('Game not in progress.')
            return

        if comd == '':
            # eventually needs to be ported to access PlayerView
            print('=== Game state ===')
            ar_output = 'Headline phase' if self.game.ar_track == 0 else 'AR' + \
                str(self.game.ar_track)
            side = self.game.ar_side.toStr()

            game_values = {
                'VP': self.game.vp_track,
                'DEFCON': self.game.defcon_track,
                'Milops': self.game.milops_track,
                'Space': self.game.space_track,
                'Spaced turns': self.game.spaced_turns,
                'US Basket': self.game.basket[Side.US],
                'USSR Basket': self.game.basket[Side.USSR],
                'ARs this turn': (self.game.ars_by_turn[0][self.game.turn_track], self.game.ars_by_turn[1][self.game.turn_track])
            }

            print(f'T{self.game.turn_track} {ar_output}, {side}\'s turn.')
            for k, v in game_values.items():
                print(f'{k:>{UI.left_margin_small}} {v}')

        elif comd == '?':
            print(UI.help_state)
        else:
            # remember to check if comd is a valid ID
            region = MapRegion.fromStr(comd)
            print(f'State of {region.name}:')
            for n in sorted(CountryInfo.REGION_ALL[region]):
                print(self.game.map[n].get_state_str())
            self.game.score(region, check_only=True)

    help_debug = '''
dbg                                 Starts debugging mode.
dbg inf set <country> <us>:<ussr>   Sets the influence in a particular country.
dbg card <card_name> <side>         Triggers the card event as the given side.
dbg rollback                        Restores the state before debugging started.
'''
    def parse_debug(self, comd):

        if not self.game_in_progress:
            print('Game not in progress.')
            return

        if not comd:
            print('Debugging mode started.')
            self.debug_save = (deepcopy(self.game),
                               deepcopy(self.game_rollback))
            return
        elif comd == '?':
            print(UI.help_debug)
            return
        elif not self.debug_save:
            print('Error: Not in debug mode.')
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
                    self.game.map[user_choice[2]
                                  ].influence[Side.US] = int(inf[0])
                    self.game.map[user_choice[2]
                                  ].influence[Side.USSR] = int(inf[1])
        elif user_choice[0] == 'card':
            if len(user_choice) != 3:
                print('Invalid command. Enter ? for help.')
            elif user_choice[1] not in Card.ALL:
                print('Invalid card name.')
            elif user_choice[2].lower() not in ['us', 'ussr']:
                print('Invalid side.')
            else:
                input_state_rollback = deepcopy(self.game.input_state)

                def end_of_event():
                    self.game.input_state = input_state_rollback
                    print(f'\n=== {user_choice[1]} event complete. ===\n')
                self.game.stage_list.append(end_of_event)
                self.game.card_function_mapping[user_choice[1]](
                    self.game, Side.fromStr(user_choice[2]))
                self.game_state_changed()
        elif user_choice[0] == 'rollback':
            print('Restoring pre-debugging state.')
            self.game = self.debug_save[0]
            self.game_rollback = self.debug_save[1]
            self.game_state_changed()
        else:
            print('Invalid command. Enter ? for help.')

    def parse_log(self, comd):

        if self.game_in_progress:
            print('Cannot toggle logging while game is in progress.')
            return
        if comd.lower() == 'on':
            self.logging = True
        elif comd.lower() == 'off':
            self.logging = False
        else:
            print('Invalid command. Enter ? for help.')

    def parse_load(self, comd):

        if self.game_in_progress:
            print('Cannot load game while game is in progress.')
            return

        try:
            f = open(f'log{path.sep}{comd}')
        except:
            print('Cannot open file.')
            return

        self.new_game()
        for i, line in enumerate(f):
            line = line.strip()
            if line not in self.input_state.available_options:
                print(f'Invalid move on line {i}:{line}')
                break
            self.move(line)
            if self.game.input_state.complete:
                self.advance_game()
        print('Game loaded.')
        self.game_state_changed()
        f.close()
