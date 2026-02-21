import { ref, reactive, computed } from 'vue'
import { defineStore } from 'pinia'
import type { ServerMovePayload, PlayerView, AIExplanation, GameGlobals, GamePrint } from '@/types/game'

export const useGameStore = defineStore('game', () => {
  // Constants
  const constants = {
    ussrPrompt: '----- USSR Player: -----',
    usPrompt: '----- US Player: -----',
    rngPrompt: '----- RNG: -----',
    availableOptionsHeader: 'Available options:',
  }

  // State
  const gameInProgress = ref(false)
  const replayInProgress = ref(false)

  const globals: GameGlobals = reactive({
    notification: [],
    side: '',
    inputType: '',
    prompt: '',
    currentSelection: '',
    reps: '',
    availableOptions: '',
    commit: '',
    selectedThisTurn: '',
  })

  const print: GamePrint = reactive({
    selected_this_turn: '',
    notification: [],
    _notification: '',
    reps: '',
    availableOptions: '',
    _availableOptions: '',
    side: '',
  })

  // AI-related state
  const playerView = ref<PlayerView | null>(null)
  const aiExplanation = ref<AIExplanation | null>(null)
  const aiThinking = ref(false)
  const gameMode = ref<'human' | 'ai'>('human')
  const aiSide = ref<string | null>(null)

  // Getters
  const gameLog = computed(() => {
    if (print.side) {
      return [
        print._notification,
        print.selected_this_turn,
        globals.currentSelection,
        print.side,
        print.reps,
        constants.availableOptionsHeader,
        print._availableOptions,
      ].join('\n')
    }
    return print._notification
  })

  // Actions
  function processServerMove(payload: ServerMovePayload) {
    globals.selectedThisTurn = payload.selected_this_turn
    globals.notification = payload.notification
    globals.side = payload.side ?? ''
    globals.inputType = payload.input_type ?? ''
    globals.prompt = payload.prompt || ''
    globals.currentSelection = payload.current_selection
    globals.reps = payload.reps
    globals.availableOptions = payload.available_options
    globals.commit = payload.commit
    gameInProgress.value = payload.game_in_progress

    if (payload.player_view && typeof payload.player_view === 'object') {
      playerView.value = payload.player_view
    }

    if (payload.ai_explanation) {
      aiExplanation.value = payload.ai_explanation
    }

    constructGameLog()
    aiThinking.value = false

    console.log(payload)
  }

  function constructGameLog() {
    print.selected_this_turn = `${globals.selectedThisTurn}`

    if (globals.side == 0) {
      print.side = constants.ussrPrompt
    } else if (globals.side == 1) {
      print.side = constants.usPrompt
    } else if (globals.side == 2) {
      print.side = constants.rngPrompt
    }

    if (globals.reps && globals.reps.length >= 2) {
      print.reps = `Remaining ${globals.reps[0]}: ${globals.reps[1]}`
    } else {
      print.reps = ''
    }

    print._availableOptions = ''
    if (globals.availableOptions && typeof globals.availableOptions === 'object') {
      for (const [key, value] of Object.entries(globals.availableOptions)) {
        print._availableOptions += `${key} \t ${value} \n`
      }
    }

    print._notification = ''
    if (globals.notification && globals.notification.entries) {
      for (const [, value] of globals.notification.entries()) {
        print._notification += `${value} \n`
      }
    }
  }

  function setGameMode(mode: 'human' | 'ai', side: string | null) {
    gameMode.value = mode
    aiSide.value = side
  }

  return {
    // State
    constants,
    gameInProgress,
    replayInProgress,
    globals,
    print,
    playerView,
    aiExplanation,
    aiThinking,
    gameMode,
    aiSide,
    // Getters
    gameLog,
    // Actions
    processServerMove,
    constructGameLog,
    setGameMode,
  }
})
