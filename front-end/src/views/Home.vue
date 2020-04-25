<template>
  <v-container fluid app>
    <v-row justify="center">
      <v-col>
        <v-row style="height:400px">
          <v-img src="@/assets/TitleSplash.png" height="400px" contain eager />
        </v-row>
      </v-col>
    </v-row>

    <v-row justify="center">
      <v-tooltip top v-for="clickable in clickables" :key="clickable.title">
        <template v-slot:activator="{ on }">
          <v-btn
            class="ma-2"
            @click="clickable.onPress"
            :disabled="clickable.disabled"
            v-on="on"
            v-if="clickable.display"
          >
            <v-icon class="mr-3">{{ clickable.icon }}</v-icon>
            {{ clickable.title }}
          </v-btn>
        </template>
        <span>{{ clickable.tooltip }}</span>
      </v-tooltip>
    </v-row>
    <v-row justify="center"> </v-row>
  </v-container>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Home',
  methods: {
    newGame() {
      this.$socket.client.emit('client_move', { move: 'new' })
      this.$router.push('/game')
    },
    continueGame() {
      this.$router.push('/game')
    },
    loadGame() {
      this.$socket.client.emit('client_load_game')
      console.log('Game loading..')
    },
    saveGame() {
      this.$socket.client.emit('client_save_game')
      console.log('Game saving..')
    }
  },
  mounted() {
    if (this.gameInProgress) {
      this.clickables.find(item => item.title == 'New Game').display = false
      this.clickables.find(item => item.title == 'Continue Game').display = true
    }
  },
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
      justify: 'space-around',
      clickables: [
        {
          title: 'New Game',
          icon: 'mdi-controller-classic-outline',
          onPress: this.newGame,
          disabled: false,
          tooltip: 'Start a new game.',
          display: true
        },
        {
          title: 'Continue Game',
          icon: 'mdi-controller-classic-outline',
          onPress: this.continueGame,
          disabled: false,
          tooltip: 'Continue the current game.',
          display: false
        },
        {
          title: 'Load Game',
          icon: 'mdi-folder-upload-outline',
          onPress: this.loadGame,
          disabled: true,
          tooltip: 'Load a .tsg file for playback.',
          display: true
        },
        {
          title: 'Save Game',
          icon: 'mdi-content-save-move-outline',
          onPress: this.saveGame,
          disabled: true,
          tooltip: 'Save the current game to a .tsg file.',
          display: true
        }
      ]
    }
  }
}
</script>

<style>
html {
  overflow: hidden;
}
</style>
