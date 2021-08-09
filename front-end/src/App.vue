<template>
  <v-app>
    <v-main>
      <transition name="slide-fade" mode="out-in">
        <router-view />
      </transition>
    </v-main>
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
      gameInProgress: (state) => state.locals.gameInProgress,
      replayInProgress: (state) => state.locals.replayInProgress,
    }),
  },
  sockets: {
    connect() {
      this.$socket.client.emit('client_move', { move: 's' })
      console.log('Socket connected: now querying game state..')
    },
    disconnect() {
      console.log('Socket disconnected.')
    },
  },
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
