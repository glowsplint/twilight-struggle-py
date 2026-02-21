<script setup lang="ts">
import { computed } from 'vue'
import { useGameStore } from '@/stores/game'
import { storeToRefs } from 'pinia'

const store = useGameStore()
const { playerView } = storeToRefs(store)

const vpTrack = computed(() => playerView.value?.vp_track ?? 0)
const defconTrack = computed(() => playerView.value?.defcon_track ?? 5)
const turnTrack = computed(() => playerView.value?.turn_track ?? 1)
const arTrack = computed(() => playerView.value?.ar_track ?? 0)
const arSideLabel = computed(() => playerView.value?.ar_side === 0 ? 'USSR' : 'US')
const arSideClass = computed(() => playerView.value?.ar_side === 0 ? 'text-ussr-light' : 'text-us-light')
const milopsUssr = computed(() => playerView.value?.milops_track?.[0] ?? 0)
const milopsUs = computed(() => playerView.value?.milops_track?.[1] ?? 0)
const spaceUssr = computed(() => playerView.value?.space_track?.[0] ?? 0)
const spaceUs = computed(() => playerView.value?.space_track?.[1] ?? 0)
const hand = computed<string[]>(() => {
  if (!playerView.value?.hand) return []
  return Array.from(playerView.value.hand).sort()
})

const ussrVpWidth = computed(() => {
  const vp = vpTrack.value
  return vp > 0 ? Math.min(50, (vp / 20) * 50) : 0
})
const usVpWidth = computed(() => {
  const vp = vpTrack.value
  return vp < 0 ? Math.min(50, (-vp / 20) * 50) : 0
})

function formatCardName(name: string): string {
  return name.replace(/_/g, ' ')
}

const defconColors = ['', 'bg-red-800', 'bg-orange-700', 'bg-amber-600', 'bg-green-700', 'bg-green-800']
</script>

<template>
  <div class="border-b border-border bg-card p-3 text-xs">
    <h3 class="mb-2 text-sm font-semibold text-sky-300">Game Status</h3>

    <!-- VP Track -->
    <div class="mb-1.5 flex items-center gap-2">
      <span class="w-14 font-bold text-muted-foreground">VP:</span>
      <div class="relative flex h-4 flex-1 overflow-hidden rounded bg-neutral-800">
        <div class="h-full bg-ussr transition-all" :style="{ width: ussrVpWidth + '%' }" />
        <div class="absolute right-0 h-full bg-us transition-all" :style="{ width: usVpWidth + '%' }" />
        <span class="absolute inset-0 flex items-center justify-center text-[11px] font-bold text-white">
          {{ vpTrack }}
        </span>
      </div>
    </div>

    <!-- DEFCON -->
    <div class="mb-1.5 flex items-center gap-2">
      <span class="w-14 font-bold text-muted-foreground">DEFCON:</span>
      <div class="flex gap-1">
        <span
          v-for="level in 5"
          :key="level"
          class="flex h-5 w-5 items-center justify-center rounded text-[10px] font-bold"
          :class="level <= defconTrack ? [defconColors[level], 'text-white'] : 'bg-neutral-800 text-neutral-600'"
        >{{ level }}</span>
      </div>
    </div>

    <!-- Turn / AR -->
    <div class="mb-1.5 flex items-center gap-2">
      <span class="w-14 font-bold text-muted-foreground">Turn:</span>
      <span>{{ turnTrack }} / AR {{ arTrack }}</span>
      <span :class="arSideClass" class="ml-1 text-[11px] font-bold">{{ arSideLabel }}</span>
    </div>

    <!-- Mil Ops -->
    <div class="mb-1.5 flex items-center gap-2">
      <span class="w-14 font-bold text-muted-foreground">Mil Ops:</span>
      <span><span class="text-ussr-light">USSR {{ milopsUssr }}</span> / <span class="text-us-light">US {{ milopsUs }}</span></span>
    </div>

    <!-- Space -->
    <div class="mb-1.5 flex items-center gap-2">
      <span class="w-14 font-bold text-muted-foreground">Space:</span>
      <span><span class="text-ussr-light">USSR {{ spaceUssr }}</span> / <span class="text-us-light">US {{ spaceUs }}</span></span>
    </div>

    <!-- Hand -->
    <div v-if="hand.length" class="mt-2 border-t border-border pt-2">
      <div class="mb-1 font-bold text-muted-foreground">Hand ({{ hand.length }} cards):</div>
      <div class="flex flex-wrap gap-1">
        <span
          v-for="card in hand"
          :key="card"
          class="rounded bg-neutral-700 px-1.5 py-0.5 text-[10px] text-neutral-200"
        >{{ formatCardName(card) }}</span>
      </div>
    </div>
  </div>
</template>
