<template>
  <v-app>
    <v-content>
      <transition name="slide-fade" mode="out-in">
        <router-view />
      </transition>
    </v-content>
    <NavBar />
    <Footer />
  </v-app>
</template>

<script>
import { mapState } from 'vuex'
import NavBar from './components/NavBar'
import Footer from './components/Footer'

export default {
  name: 'App',
  components: { NavBar, Footer },
  computed: {
    moreComputed() {
      return null
    },
    ...mapState({
      gameInProgress: state => state.locals.gameInProgress,
      replaceInProgress: state => state.locals.replaceInProgress
    })
  },
  sockets: {
    connect() {
      this.$socket.client.emit('client_request_game_state')
      console.log('Socket connected: now querying game state..')
    },
    disconnect() {
      this.gameInProgress = false
      console.log('Socket disconnected.')
    },
    server_request_game_state() {
      console.log(`Server response: gameInProgress = ${this.gameInProgress}`)
    }
  }
}
</script>

<style>
html {
  overflow: hidden;
}

.slide-fade-enter,
.slide-fade-leave-to {
  transform: translateX(10px);
  opacity: 0;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-enter-to,
.slide-fade-leave {
  height: auto;
}
</style>
