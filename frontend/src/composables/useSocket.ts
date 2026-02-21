import { ref, readonly } from 'vue'
import { io } from 'socket.io-client'
import type { AIGameConfig, ServerMovePayload, AIExplanation } from '@/types/game'
import type { useGameStore } from '@/stores/game'

// Module-level singleton - no URL means same origin (Vite proxy in dev)
const socket = io({ autoConnect: true })

const connected = ref(false)

socket.on('connect', () => {
  connected.value = true
  console.log('Socket connected: now querying game state..')
  socket.emit('client_move', { move: 's' })
})

socket.on('disconnect', () => {
  connected.value = false
  console.log('Socket disconnected.')
})

export function useSocket() {
  function sendMove(move: string) {
    socket.emit('client_move', { move })
  }

  function startAiGame(config: AIGameConfig) {
    socket.emit('client_new_ai_game', config)
  }

  function restart() {
    console.log('Requesting for game restart.')
    socket.emit('client_restart')
  }

  function loadGame() {
    socket.emit('client_load_game')
    console.log('Game loading..')
  }

  function saveGame() {
    socket.emit('client_save_game')
    console.log('Game saving..')
  }

  return {
    socket,
    connected: readonly(connected),
    sendMove,
    startAiGame,
    restart,
    loadGame,
    saveGame,
  }
}

// Register store listeners - call once from App.vue
export function registerSocketListeners(store: ReturnType<typeof useGameStore>) {
  socket.on('server_move', (payload: ServerMovePayload) => {
    store.processServerMove(payload)
  })

  socket.on('ai_thinking', () => {
    store.aiThinking = true
  })

  socket.on('ai_explanation', (payload: AIExplanation) => {
    store.aiExplanation = payload
  })
}
