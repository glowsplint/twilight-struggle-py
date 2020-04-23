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
      state: '',
      prompt: '',
      current_selection: '',
      reps: '',
      available_options: '',
      commit: ''
    }
  },
  mutations: {
    SERVER_MOVE(state, payload) {
      state.locals.gameInProgress =
        payload.notification == 'Game already in progress.'
      state.globals.notification = payload.notification
      state.globals.side = payload.side
      state.globals.state = payload.state
      state.globals.prompt = prompt.notification
      state.globals.current_selection = payload.current_selection
      state.globals.reps = payload.reps
      state.globals.available_options = payload.available_options
      state.globals.commit = payload.commit

      console.log(payload)
    }
  },
  actions: {
    socket_serverMove({ commit }, payload) {
      commit('SERVER_MOVE', payload)
    }
  }
})
