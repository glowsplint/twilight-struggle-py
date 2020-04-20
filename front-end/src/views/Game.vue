<template>
  <div>
    <v-container class="my-n3" fluid app>
      <v-row class="img-wrapper" v-dragscroll="true">
        <img src="@/assets/big.jpg" />
      </v-row>
      <v-row class="mt-4" justify="center" align="center">
        <transition name="console-fade"
          ><v-text-field
            v-model="clientAction"
            v-if="isConsoleShown"
            label="Action for this turn"
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
import Vue from 'vue'
export default {
  name: 'Game',
  mounted() {
    this.$nextTick(function() {
      window.addEventListener('keydown', event => {
        if (event.ctrlKey && event.key === 'q') {
          this.toggleConsole()
        }
      })
    })
  },
  methods: {
    post() {
      if (this.clientAction != '') {
        console.log('Sending to server..')
        if (this.clientAction === 'new') {
          this.isGameRunning()
        } else {
          this.$socket.client.emit('client_move', { move: this.clientAction })
        }
        this.clientAction = ''
      }
    },
    toggleConsole() {
      this.isConsoleShown = !this.isConsoleShown
    },
    isGameRunning() {
      console.log('Checking if game has already started..')
      this.$socket.client.emit('client_move', { move: 'new' })
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
      isConsoleShown: true
    }
  }
}
</script>

<style>
html {
  overflow: hidden;
}

.img-wrapper {
  overflow: hidden;
  height: 70vh;
  background-color: black;
  position: relative;
}

.console-fade-enter {
  transform: translateY(-10px);
  opacity: 0;
}

.console-fade-enter-active,
.console-fade-leave-active {
  transition: all 0.2s ease;
}

.console-fade-leave-to {
  transform: translateY(10px);
  opacity: 0;
}
</style>
