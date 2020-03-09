from typing import Sequence, Iterable, Callable, Tuple
from twilight_enums import Side, InputType


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
            The number of times this input is required. Defaults to 1.
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
        Returns True if no more input is required, False if input is not
        complete.
        '''
        return not self.reps or len(self.selection) == len(self.discarded_options)

    def change_max_per_option(self, n: int):
        self.max_per_option += n


class Output:

    class Notification:

        def __init__(self, turn, ar, ar_side=None, prompt=''):
            self.turn = turn
            self.ar = ar
            self.ar_side = ar_side
            self.prompt = prompt

        @staticmethod
        def fromInput(turn, ar, ar_side, input):

            if input.side == Side.US or input.side == Side.USSR:
                msg = f'{input.side} selected '

            return Game.Output.Notification(
                turn, ar, ar_side,
            )

    def output_both(self, out):
        self.output_queue[Side.USSR].append(out)
        self.output_queue[Side.US].append(out)
