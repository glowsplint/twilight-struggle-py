<template>
  <div class="game-layout">
    <!-- Main area: Map or Console -->
    <div class="game-main" :class="{ 'with-panel': showSidePanel }">
      <transition name="console-fade" mode="out-in">
        <Console v-if="isConsoleShown" />
        <Map v-else />
      </transition>
    </div>

    <!-- Side panel: Game info + AI explanation + Console log -->
    <div v-if="showSidePanel" class="game-side-panel">
      <GameInfo />
      <AIExplanation />
      <div class="side-console">
        <v-card flat class="console-card">
          <v-card-title class="py-1 console-header">Game Log</v-card-title>
          <v-card-text class="py-1 console-body" ref="consoleLog">
            <pre class="console-text">{{ gameLog }}</pre>
          </v-card-text>
        </v-card>
      </div>
      <!-- Input area in side panel -->
      <div class="side-input">
        <v-text-field
          v-model="clientAction"
          label="Enter action"
          @keyup.enter="post"
          autocomplete="false"
          hide-details
          clearable
          dense
          dark
          class="action-input"
        >
          <template slot="append">
            <v-btn
              x-small
              outlined
              dark
              @click="post"
              :disabled="clientAction === ''"
            >
              <v-icon left x-small>mdi-chevron-triple-right</v-icon>Go
            </v-btn>
          </template>
        </v-text-field>
      </div>
    </div>

    <!-- AI Thinking Overlay -->
    <v-snackbar v-model="aiThinking" :timeout="-1" color="blue-grey darken-3" top>
      <v-progress-circular indeterminate size="16" width="2" class="mr-2" />
      AI is thinking...
    </v-snackbar>
  </div>
</template>

<script>
import { mapState, mapGetters } from 'vuex'
import Console from '@/components/Console'
import Map from '@/components/Map'
import GameInfo from '@/components/GameInfo'
import AIExplanation from '@/components/AIExplanation'

export default {
  name: 'Game',
  components: { Console, Map, GameInfo, AIExplanation },
  mounted() {
    this.$nextTick(function () {
      window.addEventListener('keydown', (event) => {
        if (event.ctrlKey && event.key === '`') {
          this.toggleConsole()
        }
        if (event.ctrlKey && event.key === 'p') {
          event.preventDefault()
          this.showSidePanel = !this.showSidePanel
        }
      })
    })
  },
  data() {
    return {
      state: {},
      isConsoleShown: false,
      showSidePanel: true,
      clientAction: '',
    }
  },
  computed: {
    ...mapState({
      gameInProgress: (state) => state.locals.gameInProgress,
      aiThinking: (state) => state.aiThinking,
    }),
    ...mapGetters({
      gameLog: 'gameLog',
    }),
  },
  methods: {
    toggleConsole() {
      this.isConsoleShown = !this.isConsoleShown
    },
    post() {
      if (this.clientAction !== '') {
        this.$socket.client.emit('client_move', { move: this.clientAction })
        this.clientAction = ''
      }
    },
  },
  watch: {
    gameLog() {
      // Auto-scroll console log
      this.$nextTick(() => {
        const el = this.$refs.consoleLog
        if (el && el.$el) {
          el.$el.scrollTop = el.$el.scrollHeight
        }
      })
    },
  },
}
</script>

<style scoped>
.game-layout {
  display: flex;
  height: calc(100vh - 112px);
  overflow: hidden;
}

.game-main {
  flex: 1;
  overflow: hidden;
}

.game-main.with-panel {
  flex: 0 0 65%;
  max-width: 65%;
}

.game-side-panel {
  flex: 0 0 35%;
  max-width: 35%;
  display: flex;
  flex-direction: column;
  background: #1a1a1a;
  border-left: 1px solid #333;
  overflow: hidden;
}

.side-console {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.console-card {
  background: rgba(30, 30, 30, 0.95) !important;
  color: #e0e0e0;
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.console-header {
  font-size: 13px !important;
  color: #90CAF9;
  border-bottom: 1px solid #333;
  flex-shrink: 0;
}

.console-body {
  flex: 1;
  overflow-y: auto;
}

.console-text {
  font-size: 11px;
  font-family: 'Inconsolata', 'Monaco', 'Consolas', 'Courier New', monospace;
  color: #B0BEC5;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.side-input {
  flex-shrink: 0;
  padding: 8px;
  background: #212121;
  border-top: 1px solid #333;
}

.action-input {
  font-size: 12px;
}

@media (max-width: 960px) {
  .game-layout {
    flex-direction: column;
  }
  .game-main.with-panel {
    flex: 0 0 60%;
    max-width: 100%;
  }
  .game-side-panel {
    flex: 0 0 40%;
    max-width: 100%;
    border-left: none;
    border-top: 1px solid #333;
  }
}
</style>

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
