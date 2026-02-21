<template>
  <v-container fluid app>
    <v-row justify="center">
      <v-col>
        <v-row style="height: 400px">
          <v-img src="@/assets/TitleSplash.png" height="400px" contain eager />
        </v-row>
      </v-col>
    </v-row>

    <!-- Main buttons row -->
    <v-row justify="center">
      <v-tooltip
        top
        v-for="clickable in filteredClickables"
        :key="clickable.title"
      >
        <template v-slot:activator="{ on }">
          <v-btn
            class="ma-2"
            @click="clickable.onPress"
            :disabled="clickable.disabled"
            v-on="on"
          >
            <v-icon class="mr-3">{{ clickable.icon }}</v-icon>
            {{ clickable.title }}
          </v-btn>
        </template>
        <span>{{ clickable.tooltip }}</span>
      </v-tooltip>
    </v-row>

    <!-- AI Game Dialog -->
    <v-dialog v-model="showAiDialog" max-width="400" persistent>
      <v-card>
        <v-card-title>Play vs AI</v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12">
              <div class="subtitle-2 mb-2">Choose your side:</div>
              <v-btn-toggle v-model="aiGameSide" mandatory>
                <v-btn value="ussr" color="red darken-3" dark>
                  <v-icon left>mdi-hammer-sickle</v-icon>USSR
                </v-btn>
                <v-btn value="us" color="blue darken-3" dark>
                  <v-icon left>mdi-flag</v-icon>US
                </v-btn>
              </v-btn-toggle>
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="12">
              <div class="subtitle-2 mb-2">AI Difficulty:</div>
              <v-btn-toggle v-model="aiDifficulty" mandatory>
                <v-btn value="easy">Easy</v-btn>
                <v-btn value="medium">Medium</v-btn>
                <v-btn value="hard">Hard</v-btn>
              </v-btn-toggle>
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="showAiDialog = false">Cancel</v-btn>
          <v-btn color="primary" @click="startAiGame">Start Game</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Home',
  data() {
    return {
      justify: 'space-around',
      showAiDialog: false,
      aiGameSide: 'us',
      aiDifficulty: 'medium',
      clickables: [
        {
          title: 'Play vs AI',
          icon: 'mdi-robot',
          onPress: this.openAiDialog,
          disabled: false,
          tooltip: 'Start a new game against the AI.',
        },
        {
          title: 'New Game',
          icon: 'mdi-controller-classic-outline',
          onPress: this.newGame,
          disabled: false,
          tooltip: 'Start a new hotseat game.',
        },
        {
          title: 'Continue Game',
          icon: 'mdi-controller-classic-outline',
          onPress: this.continueGame,
          disabled: false,
          tooltip: 'Continue the current game.',
        },
        {
          title: 'Load Game',
          icon: 'mdi-folder-upload-outline',
          onPress: this.loadGame,
          disabled: true,
          tooltip: 'Load a .tsg file for playback.',
        },
        {
          title: 'Save Game',
          icon: 'mdi-content-save-move-outline',
          onPress: this.saveGame,
          disabled: true,
          tooltip: 'Save the current game to a .tsg file.',
        },
      ],
    }
  },
  computed: {
    display() {
      return [!this.gameInProgress, this.gameInProgress, true, true]
    },
    filteredClickables() {
      if (this.gameInProgress) {
        // Show: Continue, Load, Save (skip New Game and Play vs AI)
        return this.clickables.slice(2)
      } else {
        // Show: Play vs AI, New Game, Load, Save (skip Continue)
        return this.clickables.slice(0, 2).concat(this.clickables.slice(3))
      }
    },
    ...mapState({
      gameInProgress: (state) => state.locals.gameInProgress,
      replayInProgress: (state) => state.locals.replayInProgress,
    }),
  },
  methods: {
    openAiDialog() {
      this.showAiDialog = true
    },
    startAiGame() {
      this.showAiDialog = false
      const config = {
        opponent: 'ai',
        side: this.aiGameSide,
        difficulty: this.aiDifficulty,
      }
      this.$socket.client.emit('client_new_ai_game', config)
      this.$router.push('/game')
    },
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
    },
  },
}
</script>

<style>
html {
  overflow: hidden;
}
</style>
