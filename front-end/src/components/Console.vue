<template>
  <div id="console">
    <v-container class="my-n3" fluid app v-show="isConsoleShown">
      <v-row class="mt-4" justify="center" align="center">
        <pre>
          {{ gameLog }}
        </pre>
      </v-row>
      <v-row>
        <v-spacer />
      </v-row>
      <v-row class="mt-4" justify="center" align="center">
        <v-text-field
          v-model="clientAction"
          :label="
            gameLog
              ? `Action for this turn`
              : `Enter 'new' to begin or 'm' to continue`
          "
          style="margin-right: 15px; max-width: 460px"
          @keyup.enter="post"
          autocomplete="false"
          hide-details
          clearable
          dense
        >
          <template slot="append">
            <v-btn
              outlined
              style="margin-bottom: 6px"
              @click="post"
              :disabled="clientAction == ``"
            >
              <v-icon left>mdi-chevron-triple-right</v-icon>Submit
            </v-btn>
          </template>
        </v-text-field>
      </v-row>
    </v-container>
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
      gameInProgress: (state) => state.locals.gameInProgress,
      replaceInProgress: (state) => state.locals.replaceInProgress,
    }),
    ...mapGetters({
      gameLog: 'gameLog',
    }),
  },
  data() {
    return {
      clientAction: '',
      state: {},
      isConsoleShown: true,
      consoleGameLog: 'Console Game Log',
    }
  },
  methods: {
    post() {
      if (this.clientAction != '') {
        console.log(`Sending to server: ${this.clientAction}`)
        if (this.clientAction === 'restart') {
          this.restart()
        } else {
          this.$socket.client.emit('client_move', { move: this.clientAction })
        }
        this.clientAction = ''
      }
    },
    toggleConsole() {
      this.isConsoleShown = !this.isConsoleShown
    },
    restart() {
      console.log('Requesting for game restart.')
      this.$socket.client.emit('client_restart')
    },
  },
}
</script>

<style>
pre {
  height: 70vh;
  overflow: auto;
  font-size: 90%;
  font-family: 'Inconsolata', 'Monaco', 'Consolas', 'Courier New', 'Courier';
}
</style>
