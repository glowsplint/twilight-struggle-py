from typing import Sequence, Iterable, Callable, Tuple
from enums import Side, InputType


class Input:

    def __init__(self, side: Side, state: InputType, callback: Callable[[str], bool],
                 options: Iterable[str], prompt: str = '',
                 reps: int = 1, reps_unit: str = '', max_per_option: int = -1,
                 option_stop_early=''):
        '''
        Creates an input state, which is the interface by which the game engine
        communicates with the user.

        Parameters
        ----------
        side : Side
            The side of the player receiving the prompt. Neutral for rng events.
        state : InputType
            The type of selection expected.
        callback : Callable[[str], bool]
            The function to run on each input received from the player. This
            function should take a string as the user input. It should return
            True if the string was valid, and False otherwise.
            The return value may be deprecated in the future.
        options : Iterable[str]
            The options available to the user. Should match with state.
            Options can be removed before all reps are exhausted, but additional
            options cannot be added. Remove using the method remove_option.
        prompt : str
            The prompt to display to the user.
        reps : int
            The number of times this input is reqOutputred. Defaults to 1.
        reps_unit : str
            The unit to provide to the user when notifying them about the
            number of input repetitions remaining. Defaults to empty string,
            which means do not inform the user about remaining repetitions.
        max_per_option : int
            The maximum number of times a particular option can be selected.
            Defaults to reps.
        option_stop_early : str
            If the user is allowed to terminate input before the repetitions
            have been exhausted, this the option text for the early stopping
            option.
            Defaults to empty string, which means this options is not available.
        '''
        self.side = side
        self.state = state
        self.callback = callback
        self.prompt = prompt
        self.reps = reps
        self.reps_unit = reps_unit
        self.max_per_option = reps if max_per_option == -1 else max_per_option
        self.option_stop_early = option_stop_early
        self.selection = {k: 0 for k in options}
        self.discarded_options = set()

    def recv(self, input_str):
        '''
        This method is called by the user to select an option.
        Returns True if the selection was accepted, False otherwise.

        Parameters
        ----------
        input_str : str
            The selected option.
        '''
        if (input_str not in self.available_options and
                (not self.option_stop_early or input_str != self.option_stop_early)):
            return False

        if input_str == self.option_stop_early:
            self.callback(input_str)
            return True

        if self.callback(input_str):
            self.selection[input_str] += 1
            return True
        else:
            return False

    def remove_option(self, option):
        '''
        The game calls this function to remove an existing option from the
        player before reps has been exhausted. Generally used by callback
        functions.

        Parameters
        ----------
        option : str
            The option to remove.
        '''
        self.discarded_options.add(option)

    @property
    def available_options(self):
        '''
        Returns available input options to the user.
        '''
        return (
            item[0] for item in self.selection.items()
            if item[0] not in self.discarded_options
            and item[1] < self.max_per_option)

    @property
    def complete(self):
        '''
        Returns True if no more input is reqOutputred, False if input is not
        complete.
        '''
        return (not self.reps or len(self.selection) == len(self.discarded_options)
                or not len(list(self.available_options)))

    def change_max_per_option(self, n: int):
        self.max_per_option += n


class Output:
    '''
    Creates an output that works with both CLI and the GOutput.
    Outputs are templates for what will be displayed to the user. A single Output
        class is initialised (with no arguments) at the start of a cycle of the game
        loop. It is bOutputlt up additively in multiple stages. The entire output is
        displayed only when the show() method is called, after which it is cleared.

    Notifications are used for general 'public' alerts that need to come first.
    states are the corresponding InputType enumeration from enums.
    Prompts are similar to the headers at the top of the Steam version.
    Available options is a list of all available options.

    To edit an active Output instance:
        output_instance.instruction = 'Instruction'

    Methods
    -------
    show :
        BOutputlt for printing to the CLI. Usage within CLI only.

    _clear :
        Empties the Output object for subsequent use.
        Will be automatically called at the end of a show() method call.

    _process_<variable_name> :
        Sets self.<variable_name> from the value of self._<variable_name>
    '''

    ussr_prompt = '----- USSR Player: -----'
    us_prompt = '----- US Player: -----'
    rng_prompt = '----- RNG: -----'

    def __init__(self):

        self.notification = ''
        self.side = ''
        self.state = ''
        self.prompt = ''
        self.current_selection = ''
        self.reps = ''
        self.available_options_header = ''
        self.available_options = ''
        self.commit = ''

        self._available_options = {}
        self._side = None
        self._state = None

    def _process_options(self):
        available_options = "".join(
            f'{k:5} {v}' + '\n' for k, v in sorted(self._available_options.items()))[:-1]
        self.available_options += available_options

    def _process_side(self):
        if self._side == Side.USSR:
            self.side += Output.ussr_prompt
        elif self._side == Side.US:
            self.side += Output.us_prompt
        elif self._side == Side.NEUTRAL:
            self.side += Output.rng_prompt

    def _process_state(self):
        if self._state != None:
            self.state = {int(self._state): str(self._state)}

    def show(self, include_new_line=True):

        self._process_options()
        self._process_side()
        self._process_state()

        shown_items = (self.notification, self.side, self.prompt,
                       self.current_selection, self.reps, self.available_options_header,
                       self.available_options, self.commit)

        for item in shown_items:
            if item:
                if include_new_line:
                    print(item)
                else:
                    print(item, end='')
        self.__init__()  # reset object

    '''Can shift commit to prompt, and then do a check if state is commit show prompt last'''

    @property
    def json(self):
        return {
            'notification': self.notification,
            'side': self.side,
            'state': self.state,
            'prompt': self.prompt,
            'current_selection': self.current_selection,
            'reps': self.reps,
            'available_options': self._available_options,
            'commit': self.commit,
        }
