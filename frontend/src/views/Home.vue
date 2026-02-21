<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useGameStore } from '@/stores/game'
import { useSocket } from '@/composables/useSocket'
import { storeToRefs } from 'pinia'
import UiButton from '@/components/ui/button.vue'
import UiTooltip from '@/components/ui/tooltip.vue'
import UiDialog from '@/components/ui/dialog.vue'
import type { ClickableItem } from '@/types/game'
import {
  Bot,
  Gamepad2,
  Play,
  FolderUp,
  Save,
} from 'lucide-vue-next'

const router = useRouter()
const store = useGameStore()
const { gameInProgress } = storeToRefs(store)
const { sendMove, startAiGame, loadGame, saveGame } = useSocket()

const showAiDialog = ref(false)
const aiGameSide = ref<'us' | 'ussr'>('us')
const aiDifficulty = ref<'easy' | 'medium' | 'hard'>('medium')

const clickables: ClickableItem[] = [
  {
    title: 'Play vs AI',
    icon: Bot,
    onPress: () => { showAiDialog.value = true },
    disabled: false,
    tooltip: 'Start a new game against the AI.',
    showWhenGameInProgress: false,
  },
  {
    title: 'New Game',
    icon: Gamepad2,
    onPress: () => {
      sendMove('new')
      router.push('/game')
    },
    disabled: false,
    tooltip: 'Start a new hotseat game.',
    showWhenGameInProgress: false,
  },
  {
    title: 'Continue Game',
    icon: Play,
    onPress: () => router.push('/game'),
    disabled: false,
    tooltip: 'Continue the current game.',
    showWhenGameInProgress: true,
  },
  {
    title: 'Load Game',
    icon: FolderUp,
    onPress: () => loadGame(),
    disabled: true,
    tooltip: 'Load a .tsg file for playback.',
    showAlways: true,
  },
  {
    title: 'Save Game',
    icon: Save,
    onPress: () => saveGame(),
    disabled: true,
    tooltip: 'Save the current game to a .tsg file.',
    showAlways: true,
  },
]

const filteredClickables = computed(() => {
  if (gameInProgress.value) {
    return clickables.filter((c) => c.showWhenGameInProgress || c.showAlways)
  }
  return clickables.filter((c) => !c.showWhenGameInProgress || c.showAlways)
})

function doStartAiGame() {
  showAiDialog.value = false
  startAiGame({
    opponent: 'ai',
    side: aiGameSide.value,
    difficulty: aiDifficulty.value,
  })
  router.push('/game')
}
</script>

<template>
  <div class="flex flex-col items-center justify-center px-4 pt-8">
    <!-- Splash -->
    <img src="@/assets/TitleSplash.png" alt="Twilight Struggle" class="mb-8 h-[400px] object-contain" />

    <!-- Buttons -->
    <div class="flex flex-wrap justify-center gap-3">
      <UiTooltip
        v-for="item in filteredClickables"
        :key="item.title"
        :text="item.tooltip"
      >
        <UiButton
          variant="outline"
          :disabled="item.disabled"
          @click="item.onPress"
        >
          <component :is="item.icon" :size="16" />
          {{ item.title }}
        </UiButton>
      </UiTooltip>
    </div>

    <!-- AI Dialog -->
    <UiDialog v-model:open="showAiDialog" max-width="max-w-sm">
      <h2 class="mb-4 text-lg font-semibold">Play vs AI</h2>

      <div class="mb-4">
        <div class="mb-2 text-sm font-medium text-muted-foreground">Choose your side:</div>
        <div class="flex gap-2">
          <button
            class="flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors"
            :class="aiGameSide === 'ussr' ? 'bg-ussr text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80'"
            @click="aiGameSide = 'ussr'"
          >USSR</button>
          <button
            class="flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors"
            :class="aiGameSide === 'us' ? 'bg-us text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80'"
            @click="aiGameSide = 'us'"
          >US</button>
        </div>
      </div>

      <div class="mb-6">
        <div class="mb-2 text-sm font-medium text-muted-foreground">AI Difficulty:</div>
        <div class="flex gap-2">
          <button
            v-for="d in (['easy', 'medium', 'hard'] as const)"
            :key="d"
            class="rounded-md px-4 py-2 text-sm font-medium capitalize transition-colors"
            :class="aiDifficulty === d ? 'bg-primary text-white' : 'bg-muted text-muted-foreground hover:bg-muted/80'"
            @click="aiDifficulty = d"
          >{{ d }}</button>
        </div>
      </div>

      <div class="flex justify-end gap-2">
        <UiButton variant="ghost" @click="showAiDialog = false">Cancel</UiButton>
        <UiButton @click="doStartAiGame">Start Game</UiButton>
      </div>
    </UiDialog>
  </div>
</template>
