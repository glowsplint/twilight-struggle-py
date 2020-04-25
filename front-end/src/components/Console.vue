<template>
  <div>
    Boop
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Console',
  methods: {},
  mounted() {},
  computed: {
    moreComputed() {
      return null
    },
    ...mapState({
      gameInProgress: state => state.locals.gameInProgress,
      replaceInProgress: state => state.locals.replaceInProgress
    })
  },
  data() {
    return {
      justify: 'space-around'
    }
  }
}
</script>

<style>
html {
  overflow: true;
}
</style>
