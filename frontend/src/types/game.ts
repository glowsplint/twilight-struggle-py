/** Shape of the `server_move` socket event payload from the Flask backend. */
export interface ServerMovePayload {
  selected_this_turn: string
  notification: string[]
  side: number | null
  input_type: string | null
  prompt: string
  current_selection: string
  reps: [string, number] | string
  available_options: Record<string, string> | string
  commit: string
  player_view: PlayerView | string
  game_in_progress: boolean
  ai_explanation?: AIExplanation
}

/** Serialized PlayerView from the Python backend. */
export interface PlayerView {
  vp_track: number
  turn_track: number
  ar_track: number
  ar_side: number | null
  ars_by_turn: [string[], string[]]
  ar_side_done: [boolean, boolean]
  defcon_track: number
  milops_track: [number, number]
  space_track: [number, number]
  spaced_turns: [number, number]
  handicap: number | null
  map: Record<string, CountryMapData>
  removed_pile: string[]
  discard_pile: string[]
  basket: [string[], string[]]
  hand: string[]
  opp_hand_scoring: boolean
  opp_hand: string[]
}

/** Per-country map data from the backend. */
export interface CountryMapData {
  control: number
  us_influence: number
  ussr_influence: number
  battleground: boolean
  stability: number
}

/** AI move explanation attached to server_move payloads. */
export interface AIExplanation {
  chosen_action: string
  confidence: string
  reasoning: string
  alternatives: AIAlternative[]
  total_simulations: number
  num_worlds: number
  raw_confidence: number
}

/** A single alternative action considered by the AI. */
export interface AIAlternative {
  action: string
  confidence: string
  raw_confidence: number
}

/** Entry in the countryData lookup (map rendering coordinates). */
export interface CountryEntry {
  name: string
  x: number
  y: number
  opacity: number
}

/** Reactive globals object in the game store. */
export interface GameGlobals {
  notification: string[]
  side: string | number
  inputType: string
  prompt: string
  currentSelection: string
  reps: [string, number] | string
  availableOptions: Record<string, string> | string
  commit: string
  selectedThisTurn: string
}

/** Reactive print object in the game store. */
export interface GamePrint {
  selected_this_turn: string
  notification: string[]
  _notification: string
  reps: string
  availableOptions: string
  _availableOptions: string
  side: string
}

/** Configuration sent to start an AI game. */
export interface AIGameConfig {
  opponent: string
  side: string
  difficulty: string
}

/** Sidebar navigation item. */
export interface SidebarItem {
  title: string
  link: string
  icon: import('vue').Component
  disabled?: boolean
  disabledWhenNoGame?: boolean
}

/** Home screen action button entry. */
export interface ClickableItem {
  title: string
  icon: import('vue').Component
  onPress: () => void
  disabled: boolean
  tooltip: string
  showWhenGameInProgress?: boolean
  showAlways?: boolean
}
