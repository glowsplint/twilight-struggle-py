import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    locals: {
      gameInProgress: false,
      replayInProgress: false
    },
    globals: {
      notification: '',
      side: '',
      input_type: '',
      prompt: '',
      current_selection: '',
      reps: '',
      available_options: '',
      commit: ''
    }
  },
  mutations: {
    SERVER_MOVE(state, payload) {
      state.globals.notification = payload.notification
      state.globals.side = payload.side
      state.globals.input_type = payload.input_type
      state.globals.prompt = prompt.notification
      state.globals.current_selection = payload.current_selection
      state.globals.reps = payload.reps
      state.globals.available_options = payload.available_options
      state.globals.commit = payload.commit

      console.log(payload)
    },
    SERVER_REQUEST_GAME_STATE(state, payload) {
      state.locals.gameInProgress = payload.response
    }
  },
  actions: {
    socket_serverMove({ commit }, payload) {
      commit('SERVER_MOVE', payload)
    },
    socket_serverRequestGameState({ commit }, payload) {
      commit('SERVER_REQUEST_GAME_STATE', payload)
    }
  }
})
