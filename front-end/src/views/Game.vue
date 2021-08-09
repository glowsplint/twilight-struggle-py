<template>
  <div>
    <transition name="console-fade" mode="out-in">
      <Console v-if="isConsoleShown" />
      <Map v-else />
    </transition>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import Console from '@/components/Console'
import Map from '@/components/Map'

export default {
  name: 'Game',
  components: { Console, Map },
  mounted() {
    this.$nextTick(function () {
      window.addEventListener('keydown', (event) => {
        if (event.ctrlKey && event.key === '`') {
          this.toggleConsole()
        }
      })
    })
  },
  data() {
    return {
      state: {},
      isConsoleShown: false,
    }
  },
  computed: {
    moreComputed() {
      return null
    },
  },
  methods: {
    toggleConsole() {
      this.isConsoleShown = !this.isConsoleShown
    },
  },
}
</script>

<style>
html {
  overflow: hidden;
}

.console-fade-enter,
.console-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
  height: 0;
}

.console-fade-enter-active,
.console-fade-leave-active {
  transition: all 0.2s ease;
}

.console-fade-enter-to,
.console-fade-leave {
  height: auto;
}
</style>
