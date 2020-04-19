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
import NavBar from './components/NavBar'
import Footer from './components/Footer'

export default {
  name: 'App',
  components: { NavBar, Footer }
}
</script>

<style>
html {
  overflow: hidden;
}

.slide-fade-enter {
  transform: translateX(10px);
  opacity: 0;
}

.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.2s ease;
}

.slide-fade-leave-to {
  transform: translateX(-10px);
  opacity: 0;
}
</style>
