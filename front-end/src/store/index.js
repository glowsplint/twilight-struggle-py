import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    constants: {
      ussrPrompt: '----- USSR Player: -----',
      usPrompt: '----- US Player: -----',
      rngPrompt: '----- RNG: -----',
      availableOptionsHeader: 'Available options:',
    },
    locals: {
      gameInProgress: false,
      replayInProgress: false,
    },
    globals: {
      notification: [],
      side: '',
      inputType: '',
      prompt: '',
      currentSelection: '',
      reps: '',
      availableOptions: '',
      commit: '',
    },
    print: {
      selected_this_turn: '',
      notification: [],
      _notification: '',
      reps: '',
      availableOptions: '',
      _availableOptions: '',
      side: '',
    },
    // AI-related state
    playerView: null,
    aiExplanation: null,
    aiThinking: false,
    gameMode: 'human', // 'human' or 'ai'
    aiSide: null,
  },
  mutations: {
    SERVER_MOVE(state, payload) {
      state.globals.selectedThisTurn = payload.selected_this_turn
      state.globals.notification = payload.notification
      state.globals.side = payload.side
      state.globals.inputType = payload.input_type
      state.globals.prompt = payload.prompt || ''
      state.globals.currentSelection = payload.current_selection
      state.globals.reps = payload.reps
      state.globals.availableOptions = payload.available_options
      state.globals.commit = payload.commit
      state.locals.gameInProgress = payload.game_in_progress

      // Update player view if present
      if (payload.player_view && typeof payload.player_view === 'object') {
        state.playerView = payload.player_view
      }

      // Update AI explanation if present
      if (payload.ai_explanation) {
        state.aiExplanation = payload.ai_explanation
      }

      console.log(payload)
    },
    CONSTRUCT_GAME_LOG(state) {
      // Process selected_this_turn
      state.print.selected_this_turn = `${state.globals.selectedThisTurn}`

      // Process side
      if (state.globals.side == 0) {
        state.print.side = state.constants.ussrPrompt
      } else if (state.globals.side == 1) {
        state.print.side = state.constants.usPrompt
      } else if (state.globals.side == 2) {
        state.print.side = state.constants.rngPrompt
      }

      // Process reps
      if (state.globals.reps && state.globals.reps.length >= 2) {
        state.print.reps = `Remaining ${state.globals.reps[0]}: ${state.globals.reps[1]}`
      } else {
        state.print.reps = ''
      }

      // Process options
      state.print._availableOptions = ``
      if (state.globals.availableOptions && typeof state.globals.availableOptions === 'object') {
        for (let [key, value] of Object.entries(state.globals.availableOptions)) {
          state.print._availableOptions += `${key} \t ${value} \n`
        }
      }

      // Process notifications
      state.print._notification = ``
      if (state.globals.notification && state.globals.notification.entries) {
        for (let [_, value] of state.globals.notification.entries()) {
          state.print._notification += `${value} \n`
        }
      }
    },
    SET_AI_THINKING(state, isThinking) {
      state.aiThinking = isThinking
    },
    SET_GAME_MODE(state, { mode, aiSide }) {
      state.gameMode = mode
      state.aiSide = aiSide
    },
    SET_AI_EXPLANATION(state, explanation) {
      state.aiExplanation = explanation
    },
  },
  actions: {
    socket_serverMove({ commit }, payload) {
      commit('SERVER_MOVE', payload)
      commit('CONSTRUCT_GAME_LOG')
      commit('SET_AI_THINKING', false)
    },
    socket_aiThinking({ commit }) {
      commit('SET_AI_THINKING', true)
    },
    socket_aiExplanation({ commit }, payload) {
      commit('SET_AI_EXPLANATION', payload)
    },
  },
  getters: {
    gameLog: (state) => {
      if (state.print.side) {
        return [
          state.print._notification,
          state.print.selected_this_turn,
          state.globals.currentSelection,
          state.print.side,
          state.print.reps,
          state.constants.availableOptionsHeader,
          state.print._availableOptions,
        ].join('\n')
      }
      return state.print._notification
    },
  },
})
