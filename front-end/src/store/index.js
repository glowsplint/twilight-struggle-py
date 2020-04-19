import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    locals: {
      gameInProgress: false,
      replayInProgress: false
    }
  },
  mutations: {
    SOCKET_SERVER_MOVE(gameInProgress, payload) {
      gameInProgress = payload
      console.log('mutation called')
      console.log(payload)
    }
  },
  actions: {
    socket_serverMove({ context }) {
      commit('SOCKET_CLIENT_MOVE', payload)
      console.log('action called')
    }
  }
})
