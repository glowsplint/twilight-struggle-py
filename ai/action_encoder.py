"""
Action Encoder: Maps between game string options and integer action indices.

Hierarchical action encoding matching the existing Input system:
  - Card selection: index into hand (card_index based)
  - Action type: event/influence/coup/realign/space/skip (~7 options)
  - Country selection: index into 87 countries (country_index based)
  - Multiple selection: dynamic index
  - Dice roll: handled separately (1-6)

The action space is flat for neural network output, with illegal action masking.
"""

import numpy as np

from cards import Card
from enums import CardAction, InputType, Side
from world_map import CountryInfo


# Build deterministic ordered lists
COUNTRY_NAMES = sorted(CountryInfo.ALL.keys(), key=lambda n: CountryInfo.ALL[n].country_index)
CARD_NAMES = sorted(Card.ALL.keys(), key=lambda n: Card.ALL[n].card_index)

NUM_COUNTRIES = len(COUNTRY_NAMES)
NUM_CARDS = len(CARD_NAMES)
NUM_CARD_ACTIONS = len(CardAction)  # 7: PLAY_EVENT through SKIP_OPTIONAL_AR
DICE_OPTIONS = 6  # 1-6

# Flat action space layout:
# [0..NUM_CARDS-1]              = SELECT_CARD (select card by card list index)
# [NUM_CARDS..NUM_CARDS+6]      = SELECT_CARD_ACTION (7 actions)
# [NUM_CARDS+7..NUM_CARDS+6+NUM_COUNTRIES] = SELECT_COUNTRY
# [NUM_CARDS+7+NUM_COUNTRIES..+6] = DICE (6 options)
# [next..+1]                    = STOP_EARLY option

CARD_OFFSET = 0
ACTION_OFFSET = NUM_CARDS
COUNTRY_OFFSET = ACTION_OFFSET + NUM_CARD_ACTIONS
DICE_OFFSET = COUNTRY_OFFSET + NUM_COUNTRIES
STOP_EARLY_OFFSET = DICE_OFFSET + DICE_OPTIONS
TOTAL_ACTIONS = STOP_EARLY_OFFSET + 1

# Reverse lookups
COUNTRY_TO_IDX = {name: i for i, name in enumerate(COUNTRY_NAMES)}
CARD_TO_IDX = {name: i for i, name in enumerate(CARD_NAMES)}
CARD_ACTION_TO_IDX = {action.name: action.value for action in CardAction}


def encode_action(option: str, input_type: InputType) -> int:
    """
    Convert a game option string + input type into an action index.

    Parameters
    ----------
    option : str
        The option string (card name, country name, action name, dice value).
    input_type : InputType
        The current input type context.

    Returns
    -------
    int
        Action index in [0, TOTAL_ACTIONS).
    """
    if input_type == InputType.SELECT_CARD:
        if option in CARD_TO_IDX:
            return CARD_OFFSET + CARD_TO_IDX[option]
    elif input_type == InputType.SELECT_CARD_ACTION:
        if option in CARD_ACTION_TO_IDX:
            return ACTION_OFFSET + CARD_ACTION_TO_IDX[option]
    elif input_type == InputType.SELECT_COUNTRY:
        if option in COUNTRY_TO_IDX:
            return COUNTRY_OFFSET + COUNTRY_TO_IDX[option]
    elif input_type == InputType.ROLL_DICE:
        # Dice options are tuples like "(1, 2)" or single values
        try:
            val = int(option.strip("()").split(",")[0]) if "," in str(option) else int(option)
            return DICE_OFFSET + val - 1  # 1-indexed to 0-indexed
        except (ValueError, IndexError):
            pass
    elif input_type == InputType.SELECT_MULTIPLE:
        # For SELECT_MULTIPLE, try card first then country
        if option in CARD_TO_IDX:
            return CARD_OFFSET + CARD_TO_IDX[option]
        if option in COUNTRY_TO_IDX:
            return COUNTRY_OFFSET + COUNTRY_TO_IDX[option]

    # Stop early option
    return STOP_EARLY_OFFSET


def decode_action(action_idx: int, input_state) -> str:
    """
    Convert an action index back to a game option string.

    Parameters
    ----------
    action_idx : int
        The action index.
    input_state : Input
        The current input state for context.

    Returns
    -------
    str
        The game option string.
    """
    if action_idx == STOP_EARLY_OFFSET:
        return input_state.option_stop_early

    if CARD_OFFSET <= action_idx < ACTION_OFFSET:
        return CARD_NAMES[action_idx - CARD_OFFSET]
    elif ACTION_OFFSET <= action_idx < COUNTRY_OFFSET:
        action_value = action_idx - ACTION_OFFSET
        return CardAction(action_value).name
    elif COUNTRY_OFFSET <= action_idx < DICE_OFFSET:
        return COUNTRY_NAMES[action_idx - COUNTRY_OFFSET]
    elif DICE_OFFSET <= action_idx < STOP_EARLY_OFFSET:
        dice_val = action_idx - DICE_OFFSET + 1  # 0-indexed to 1-indexed
        # Return as string to match available_options format
        options = list(input_state.available_options)
        for opt in options:
            if str(dice_val) in str(opt):
                return opt
        return str(dice_val)

    raise ValueError(f"Invalid action index: {action_idx}")


def get_action_mask(input_state) -> np.ndarray:
    """
    Create a binary mask of legal actions for the current input state.

    Parameters
    ----------
    input_state : Input
        The current input state.

    Returns
    -------
    np.ndarray
        Boolean mask of shape (TOTAL_ACTIONS,). True = legal.
    """
    mask = np.zeros(TOTAL_ACTIONS, dtype=np.bool_)
    input_type = input_state.state

    for option in input_state.available_options:
        idx = encode_action(option, input_type)
        if 0 <= idx < TOTAL_ACTIONS:
            mask[idx] = True

    if input_state.option_stop_early:
        mask[STOP_EARLY_OFFSET] = True

    return mask


def masked_action_probs(policy_logits: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """
    Apply action mask to policy logits and return probabilities.

    Parameters
    ----------
    policy_logits : np.ndarray
        Raw policy logits from neural network.
    mask : np.ndarray
        Boolean mask of legal actions.

    Returns
    -------
    np.ndarray
        Probability distribution over actions (masked and softmax'd).
    """
    masked_logits = np.full_like(policy_logits, -1e9)
    masked_logits[mask] = policy_logits[mask]

    # Stable softmax
    max_logit = masked_logits.max()
    exp_logits = np.exp(masked_logits - max_logit)
    probs = exp_logits / exp_logits.sum()
    return probs
