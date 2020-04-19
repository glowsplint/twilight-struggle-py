<template>
  <div>
    <v-container class="my-n3" fluid app>
      <v-row class="img-wrapper" v-dragscroll="true">
        <img src="@/assets/big.jpg" />
      </v-row>
      <v-row class="mt-4" justify="center" align="center">
        <v-text-field
          v-model="clientAction"
          label="Action for this turn"
          hide-details
          style="margin-right: 15px; max-width: 460px"
          @keyup.enter="post"
          clearable
          autocomplete="false"
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
import Vue from 'vue'
export default {
  name: 'Game',
  methods: {
    post() {
      if (this.clientAction != '') {
        console.log('Sending to server..')
        this.$socket.emit('client-move', { move: this.clientAction })
        this.clientAction = ''
      }
    }
  },
  sockets: {
    'server-move': function(data) {
      console.log(
        `Received from server: data = ${data.data}`
      )
    }
  },
  data() {
    return {
      clientAction: '',
      socket: {},
      context: {},
      state: {}
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
</style>
