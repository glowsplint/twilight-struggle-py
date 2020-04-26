<template>
  <div>
    <v-container class="my-n3" fluid app>
      <v-row class="mt-4" justify="center" align="center">
        <transition name="console-fade">
          <Console id="code" v-show="isConsoleShown" />
        </transition>
      </v-row>
      <v-row class="img-wrapper" v-dragscroll="true" v-if="false">
        <img src="@/assets/big.jpg" />
      </v-row>
      <v-row><v-spacer></v-spacer></v-row>
      <v-row class="mt-4" justify="center" align="center">
        <transition name="console-fade">
          <v-text-field
            v-model="clientAction"
            v-show="isConsoleInputShown"
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
        </transition>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import Console from '@/components/Console'

export default {
  name: 'Game',
  components: { Console },
  mounted() {
    this.$nextTick(function() {
      window.addEventListener('keydown', event => {
        if (event.ctrlKey && event.key === '`') {
          this.toggleConsole()
          this.toggleConsoleInput()
        }
      })
    })
  },
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
    toggleConsoleInput() {
      this.isConsoleInputShown = !this.isConsoleInputShown
    },
    restart() {
      console.log('Requesting for game restart.')
      this.$socket.client.emit('client_restart')
    }
  },
  sockets: {
    'server-move': data => {
      console.log(`Received from server: data = ${data.server_move}`)
    }
  },
  data() {
    return {
      clientAction: '',
      state: {},
      isConsoleShown: true,
      isConsoleInputShown: true,
      consoleGameLog: 'Console Game Log'
    }
  }
}
</script>

<style>
html {
  /* overflow: hidden; */
  overflow: auto;
}

.img-wrapper {
  overflow: hidden;
  height: 70vh;
  background-color: black;
  position: relative;
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

#code {
  font-family: 'Inconsolata', 'Monaco', 'Consolas', 'Courier New', 'Courier';
}
</style>
