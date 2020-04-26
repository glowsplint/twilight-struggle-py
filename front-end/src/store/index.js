import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    constants: {
      ussrPrompt: '----- USSR Player: -----',
      usPrompt: '----- US Player: -----',
      rngPrompt: '----- RNG: -----',
      availableOptionsHeader: 'Available options:'
    },
    locals: {
      gameInProgress: false,
      replayInProgress: false
    },
    globals: {
      notification: '',
      side: '',
      inputType: '',
      prompt: '',
      currentSelection: '',
      reps: '',
      availableOptions: '',
      commit: ''
    },
    print: {
      selected_this_turn: '',
      notification: '',
      reps: '',
      availableOptions: '',
      _availableOptions: '',
      side: ''
    }
  },
  mutations: {
    SERVER_MOVE(state, payload) {
      state.globals.selectedThisTurn = payload.selected_this_turn
      state.globals.notification = payload.notification
      state.globals.side = payload.side
      state.globals.inputType = payload.input_type
      state.globals.prompt = prompt.notification
      state.globals.currentSelection = payload.current_selection
      state.globals.reps = payload.reps
      state.globals.availableOptions = payload.available_options
      state.globals.commit = payload.commit
      console.log(payload)
    },
    SERVER_REQUEST_GAME_STATE(state, payload) {
      state.locals.gameInProgress = payload.response
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
      state.print.reps = `Remaining ${state.globals.reps[0]}: ${state.globals.reps[1]}`

      // Process options
      state.print._availableOptions = ``
      for (let [key, value] of Object.entries(state.globals.availableOptions)) {
        state.print._availableOptions += `${key} \t ${value} \n`
      }

      // Process inputType

      // if (state.globals._inputType != null){
      //     state.globals.inputType = {int(state.globals._inputType): str(state.globals._inputType)}
      //   }
    }
  },
  actions: {
    socket_serverMove({ commit }, payload) {
      commit('SERVER_MOVE', payload)
      commit('CONSTRUCT_GAME_LOG')
    },
    socket_serverRequestGameState({ commit }, payload) {
      commit('SERVER_REQUEST_GAME_STATE', payload)
    }
  },
  getters: {
    gameLog: state => {
      if (state.print.side) {
        return [
          state.globals.notification,
          state.print.selected_this_turn,
          state.globals.currentSelection,
          state.print.side,
          state.print.reps,
          state.constants.availableOptionsHeader,
          state.print._availableOptions
        ].join('\n')
      }
      return state.globals.notification
    }
  }
})
