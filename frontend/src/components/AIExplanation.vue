<script setup lang="ts">
import { ref, computed } from 'vue'
import { useGameStore } from '@/stores/game'
import { storeToRefs } from 'pinia'
import { Bot, ChevronUp, ChevronDown } from 'lucide-vue-next'

const store = useGameStore()
const { aiExplanation } = storeToRefs(store)

const expanded = ref(true)

const hasExplanation = computed(() => aiExplanation.value?.chosen_action)
const chosenAction = computed(() => aiExplanation.value?.chosen_action ?? '')
const confidence = computed(() => aiExplanation.value?.confidence ?? '0%')
const reasoning = computed(() => aiExplanation.value?.reasoning ?? '')
const alternatives = computed(() => aiExplanation.value?.alternatives ?? [])
const totalSimulations = computed(() => aiExplanation.value?.total_simulations ?? 0)
const numWorlds = computed(() => aiExplanation.value?.num_worlds ?? 0)
const rawConfidence = computed(() => aiExplanation.value?.raw_confidence ?? 0)

const confidenceBadgeClass = computed(() => {
  if (rawConfidence.value >= 0.7) return 'bg-emerald-700 text-white'
  if (rawConfidence.value >= 0.4) return 'bg-amber-600 text-black'
  return 'bg-red-800 text-white'
})
</script>

<template>
  <div v-if="hasExplanation" class="border-b border-border bg-card text-xs">
    <!-- Header -->
    <button
      class="flex w-full items-center gap-2 px-3 py-2 text-sm font-semibold text-sky-300 hover:bg-muted/50"
      @click="expanded = !expanded"
    >
      <Bot :size="14" />
      AI Analysis
      <div class="flex-1" />
      <ChevronUp v-if="expanded" :size="14" />
      <ChevronDown v-else :size="14" />
    </button>

    <!-- Body -->
    <Transition name="collapse">
      <div v-show="expanded" class="px-3 pb-3">
        <!-- Chosen action -->
        <div class="mb-1.5 flex items-center gap-2">
          <span class="text-[11px] font-bold text-muted-foreground">Played:</span>
          <span class="text-[13px] font-bold">{{ chosenAction }}</span>
          <span :class="confidenceBadgeClass" class="rounded px-1.5 py-0.5 text-[11px] font-bold">
            {{ confidence }}
          </span>
        </div>

        <!-- Reasoning -->
        <div v-if="reasoning" class="mb-2 border-l-2 border-neutral-600 pl-2 text-[11px] italic text-neutral-400">
          {{ reasoning }}
        </div>

        <!-- Alternatives -->
        <div v-if="alternatives.length" class="mb-1.5 space-y-1">
          <div class="text-[11px] font-bold text-muted-foreground">Top alternatives:</div>
          <div v-for="(alt, idx) in alternatives" :key="idx" class="flex items-center gap-1.5">
            <span class="min-w-[100px] truncate text-[11px] text-neutral-400">{{ alt.action }}</span>
            <div class="h-2 flex-1 overflow-hidden rounded bg-neutral-800">
              <div
                class="h-full rounded transition-all"
                :class="idx === 0 ? 'bg-us-light' : 'bg-neutral-600'"
                :style="{ width: (alt.raw_confidence * 100) + '%' }"
              />
            </div>
            <span class="min-w-[28px] text-right text-[11px] text-neutral-500">{{ alt.confidence }}</span>
          </div>
        </div>

        <!-- Sim info -->
        <div class="text-right text-[10px] text-neutral-600">
          {{ totalSimulations }} simulations across {{ numWorlds }} worlds
        </div>
      </div>
    </Transition>
  </div>
</template>

<style>
.collapse-enter-active, .collapse-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}
.collapse-enter-from, .collapse-leave-to {
  opacity: 0;
  max-height: 0;
}
.collapse-enter-to, .collapse-leave-from {
  max-height: 500px;
}
</style>
