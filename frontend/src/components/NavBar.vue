<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useGameStore } from '@/stores/game'
import { useSocket } from '@/composables/useSocket'
import { storeToRefs } from 'pinia'
import type { SidebarItem } from '@/types/game'
import {
  Home,
  Radiation,
  BarChart3,
  PlayCircle,
  CreditCard,
  Menu,
  X,
} from 'lucide-vue-next'

const store = useGameStore()
const { gameInProgress } = storeToRefs(store)
const { connected } = useSocket()

const drawer = ref(false)

const sidebar: SidebarItem[] = [
  { title: 'Home', link: '/', icon: Home, disabled: false },
  { title: 'Game', link: '/game', icon: Radiation, disabledWhenNoGame: true },
  { title: 'Analysis', link: '/analysis', icon: BarChart3, disabled: true },
  { title: 'Replay Viewer', link: '/replay', icon: PlayCircle, disabled: true },
  { title: 'Card Gallery', link: '/cards', icon: CreditCard, disabled: true },
]

function toggleDrawer() {
  drawer.value = !drawer.value
}

function onKeydown(event: KeyboardEvent) {
  if (!event.ctrlKey && event.key === '`') {
    toggleDrawer()
  }
}

onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>

<template>
  <!-- Header -->
  <header class="sticky top-0 z-40 flex h-12 items-center gap-3 border-b border-border bg-primary px-4">
    <button class="text-white hover:text-white/80" @click="toggleDrawer">
      <Menu v-if="!drawer" :size="20" />
      <X v-else :size="20" />
    </button>
    <span class="text-sm font-semibold text-white tracking-wide">Twilight Struggle</span>
    <div class="flex-1" />
    <Transition name="error-fade" mode="out-in">
      <span
        :key="String(connected)"
        class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium text-white"
        :class="connected ? 'bg-emerald-600' : 'bg-red-600'"
      >
        {{ connected ? 'Connected' : 'Disconnected' }}
      </span>
    </Transition>
    <router-link to="/">
      <img src="@/assets/ts_icon_1024.png" class="h-8 w-8" alt="TS" />
    </router-link>
  </header>

  <!-- Drawer overlay -->
  <Transition name="drawer-fade">
    <div
      v-if="drawer"
      class="fixed inset-0 z-30 bg-black/40"
      @click="drawer = false"
    />
  </Transition>

  <!-- Drawer -->
  <Transition name="drawer-slide">
    <nav
      v-if="drawer"
      class="fixed left-0 top-12 z-30 h-[calc(100vh-3rem)] w-56 border-r border-border bg-card"
    >
      <ul class="py-2">
        <li v-for="item in sidebar" :key="item.title">
          <router-link
            :to="item.link"
            class="flex items-center gap-3 px-4 py-2 text-sm transition-colors"
            :class="
              (item.disabled || (item.disabledWhenNoGame && !gameInProgress))
                ? 'pointer-events-none text-muted-foreground/40'
                : 'text-foreground hover:bg-muted'
            "
            @click="drawer = false"
          >
            <component :is="item.icon" :size="16" />
            {{ item.title }}
          </router-link>
        </li>
      </ul>
    </nav>
  </Transition>
</template>

<style>
.error-fade-enter-active, .error-fade-leave-active { transition: opacity 0.2s ease; }
.error-fade-enter-from, .error-fade-leave-to { opacity: 0; }

.drawer-fade-enter-active, .drawer-fade-leave-active { transition: opacity 0.2s ease; }
.drawer-fade-enter-from, .drawer-fade-leave-to { opacity: 0; }

.drawer-slide-enter-active, .drawer-slide-leave-active { transition: transform 0.2s ease; }
.drawer-slide-enter-from, .drawer-slide-leave-to { transform: translateX(-100%); }
</style>
