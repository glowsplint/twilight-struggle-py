<script setup lang="ts">
import { ref } from 'vue'
import { useGameStore } from '@/stores/game'
import { useSocket } from '@/composables/useSocket'
import { storeToRefs } from 'pinia'
import { ChevronRight } from 'lucide-vue-next'
import UiButton from '@/components/ui/button.vue'

const store = useGameStore()
const { gameLog } = storeToRefs(store)
const { sendMove, restart } = useSocket()

const clientAction = ref('')

function post() {
  if (clientAction.value !== '') {
    console.log(`Sending to server: ${clientAction.value}`)
    if (clientAction.value === 'restart') {
      restart()
    } else {
      sendMove(clientAction.value)
    }
    clientAction.value = ''
  }
}
</script>

<template>
  <div class="flex h-full flex-col items-center justify-center p-4">
    <pre class="h-[70vh] w-full max-w-2xl overflow-auto font-mono text-sm text-neutral-300">{{ gameLog }}</pre>
    <div class="mt-4 flex w-full max-w-lg items-center gap-2">
      <input
        v-model="clientAction"
        :placeholder="gameLog ? 'Action for this turn' : `Enter 'new' to begin or 'm' to continue`"
        class="flex-1 rounded-md border border-border bg-transparent px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
        @keyup.enter="post"
      />
      <UiButton variant="outline" size="sm" :disabled="clientAction === ''" @click="post">
        <ChevronRight :size="14" />
        Submit
      </UiButton>
    </div>
  </div>
</template>
