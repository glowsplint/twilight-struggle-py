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
          <v-btn class="ma-2" @click="clickable.onPress" :disabled="clickable.disabled" v-on="on">
            <v-icon class="mr-3">{{ clickable.icon }}</v-icon>
            {{ clickable.title }}
          </v-btn>
        </template>
        <span>{{ clickable.tooltip }}</span>
      </v-tooltip>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'Home',
  methods: {
    newGame() {
      this.$router.push('/game')
      this.$socket.emit('client-new-game')
    },
    loadGame() {
      this.$socket.emit('client-load-game')
      console.log('Game loading..')
    },
    saveGame() {
      this.$socket.emit('client-save-game')
      console.log('Game saving..')
    }
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
          tooltip: 'Start a new game.'
        },
        {
          title: 'Load Game',
          icon: 'mdi-folder-upload-outline',
          onPress: this.loadGame,
          disabled: true,
          tooltip: 'Load a .tsg file for playback.'
        },
        {
          title: 'Save Game',
          icon: 'mdi-content-save-move-outline',
          onPress: this.saveGame,
          disabled: true,
          tooltip: 'Save the current game to a .tsg file.'
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
