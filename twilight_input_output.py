from typing import Any, Dict, Sequence, Iterable, Callable, Tuple
from twilight_enums import Side, InputType


class Input:

    def __init__(self, side: Side, state: InputType, callback: Callable[[str], bool],
                 options: Iterable[str], prompt: str = '',
                 reps: int = 1, reps_unit: str = '', max_per_option: int = -1,
                 option_stop_early='', context: Dict[str, Any] | None = None):
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
            Options can be updated before all reps are exhausted via
            add_option/remove_option when engine legality changes dynamically.
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
        context : dict, optional
            Optional metadata consumed by non-UI agents (for example RL
            featurizers). Engine flow must not rely on this being present.
        '''
        self.side = side
        self.state = state
        self.callback = callback
        self.prompt = prompt
        self.reps = reps
        self.reps_unit = reps_unit
        self.max_per_option = reps if max_per_option == -1 else max_per_option
        self.option_stop_early = option_stop_early
        self.context = {} if context is None else dict(context)
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
        if not self.is_option_legal(input_str):
            return False

        if input_str == self.option_stop_early:
            self.callback(input_str)
            return True

        if self.callback(input_str):
            self.selection[input_str] += 1
            return True
        else:
            return False

    def _is_standard_option_available(self, option: str) -> bool:
        return (
            option in self.selection
            and option not in self.discarded_options
            and self.selection[option] < self.max_per_option
        )

    def is_option_legal(self, input_str: str) -> bool:
        if self.option_stop_early and input_str == self.option_stop_early:
            return self.reps > 0
        return self._is_standard_option_available(input_str)

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
        if option not in self.selection:
            raise KeyError('Option was never present!')
        self.discarded_options.add(option)

    def add_option(self, option):
        """Add a newly legal option without restoring a discarded option."""
        if option not in self.selection:
            self.selection[option] = 0

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
    def legal_options(self):
        for option in self.available_options:
            yield option
        if self.option_stop_early and self.reps > 0:
            yield self.option_stop_early

    @property
    def complete(self):
        '''
        Returns True if no more input is required, False if input is not
        complete.
        '''
        if self.reps <= 0:
            return True
        return not any(
            self._is_standard_option_available(option)
            for option in self.selection
        )

    def change_max_per_option(self, n: int):
        self.max_per_option += n
