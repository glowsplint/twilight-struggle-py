<script setup lang="ts">
import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { useSocket } from '@/composables/useSocket'
import { storeToRefs } from 'pinia'
import Console from '@/components/Console.vue'
import GameMap from '@/components/Map.vue'
import GameInfo from '@/components/GameInfo.vue'
import AIExplanation from '@/components/AIExplanation.vue'
import UiButton from '@/components/ui/button.vue'
import { ChevronRight, Loader2 } from 'lucide-vue-next'

const store = useGameStore()
const { gameLog, aiThinking } = storeToRefs(store)
const { sendMove } = useSocket()

const isConsoleShown = ref(false)
const showSidePanel = ref(true)
const clientAction = ref('')
const consoleLogEl = ref<HTMLElement | null>(null)

function toggleConsole() {
  isConsoleShown.value = !isConsoleShown.value
}

function post() {
  if (clientAction.value !== '') {
    sendMove(clientAction.value)
    clientAction.value = ''
  }
}

function onKeydown(event: KeyboardEvent) {
  if (event.ctrlKey && event.key === '`') {
    toggleConsole()
  }
  if (event.ctrlKey && event.key === 'p') {
    event.preventDefault()
    showSidePanel.value = !showSidePanel.value
  }
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

// Auto-scroll console log
watch(gameLog, () => {
  nextTick(() => {
    if (consoleLogEl.value) {
      consoleLogEl.value.scrollTop = consoleLogEl.value.scrollHeight
    }
  })
})
</script>

<template>
  <div class="flex" style="height: calc(100vh - 5rem)">
    <!-- Main: Map or Console -->
    <div class="flex-1 overflow-hidden" :class="{ 'max-w-[65%]': showSidePanel }">
      <Transition name="console-fade" mode="out-in">
        <Console v-if="isConsoleShown" />
        <GameMap v-else />
      </Transition>
    </div>

    <!-- Side Panel -->
    <div
      v-if="showSidePanel"
      class="flex w-[35%] flex-col overflow-hidden border-l border-border bg-card"
    >
      <GameInfo />
      <AIExplanation />

      <!-- Game Log -->
      <div class="flex flex-1 flex-col overflow-hidden">
        <div class="border-b border-border px-3 py-1.5 text-sm font-semibold text-sky-300">
          Game Log
        </div>
        <div ref="consoleLogEl" class="flex-1 overflow-y-auto px-3 py-1.5">
          <pre class="whitespace-pre-wrap break-words font-mono text-[11px] leading-relaxed text-neutral-400">{{ gameLog }}</pre>
        </div>
      </div>

      <!-- Input -->
      <div class="border-t border-border bg-neutral-900 p-2">
        <div class="flex items-center gap-2">
          <input
            v-model="clientAction"
            placeholder="Enter action"
            class="flex-1 rounded-md border border-border bg-transparent px-2 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            @keyup.enter="post"
          />
          <UiButton variant="outline" size="sm" :disabled="clientAction === ''" @click="post">
            <ChevronRight :size="12" />
            Go
          </UiButton>
        </div>
      </div>
    </div>

    <!-- AI Thinking toast -->
    <Transition name="toast">
      <div
        v-if="aiThinking"
        class="fixed left-1/2 top-16 z-50 -translate-x-1/2 rounded-md border border-border bg-neutral-800 px-4 py-2 text-sm text-neutral-200 shadow-lg"
      >
        <Loader2 :size="14" class="mr-2 inline animate-spin" />
        AI is thinking...
      </div>
    </Transition>
  </div>
</template>

<style>
.console-fade-enter-from,
.console-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
.console-fade-enter-active,
.console-fade-leave-active {
  transition: all 0.2s ease;
}

.toast-enter-active, .toast-leave-active {
  transition: all 0.2s ease;
}
.toast-enter-from, .toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}
</style>
