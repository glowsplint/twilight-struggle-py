<template>
  <div id="console">
    <pre>
      {{ gameLog }}
    </pre>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'

export default {
  name: 'Console',
  methods: {},
  computed: {
    moreComputed() {
      return null
    },
    ...mapState({
      gameInProgress: state => state.locals.gameInProgress,
      replaceInProgress: state => state.locals.replaceInProgress
    }),
    ...mapGetters({
      gameLog: 'gameLog'
    })
  }
}
</script>

<style>
pre {
  height: 70vh;
  overflow: auto;
  font-size: 90%;
}
</style>
