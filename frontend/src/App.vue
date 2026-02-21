<script setup lang="ts">
import { onMounted } from 'vue'
import NavBar from '@/components/NavBar.vue'
import FooterBar from '@/components/FooterBar.vue'
import { useGameStore } from '@/stores/game'
import { registerSocketListeners } from '@/composables/useSocket'

const store = useGameStore()

onMounted(() => {
  registerSocketListeners(store)
})
</script>

<template>
  <div class="flex min-h-screen flex-col bg-background text-foreground">
    <NavBar />
    <main class="flex-1">
      <router-view v-slot="{ Component }">
        <Transition name="slide-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>
    <FooterBar />
  </div>
</template>

<style>
.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(10px);
  opacity: 0;
}
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.2s ease;
}
</style>
