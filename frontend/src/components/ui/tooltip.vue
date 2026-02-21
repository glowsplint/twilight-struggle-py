<script setup lang="ts">
import { ref } from 'vue'

withDefaults(defineProps<{
  text?: string
  position?: 'top' | 'bottom'
}>(), {
  position: 'top',
})

const show = ref(false)
</script>

<template>
  <div class="relative inline-flex" @mouseenter="show = true" @mouseleave="show = false">
    <slot />
    <Transition name="tooltip-fade">
      <div
        v-if="show && text"
        class="absolute z-50 whitespace-nowrap rounded-md bg-neutral-800 px-2 py-1 text-xs text-neutral-200 shadow-md pointer-events-none"
        :class="{
          'bottom-full mb-2 left-1/2 -translate-x-1/2': position === 'top',
          'top-full mt-2 left-1/2 -translate-x-1/2': position === 'bottom',
        }"
      >
        {{ text }}
      </div>
    </Transition>
  </div>
</template>

<style>
.tooltip-fade-enter-active, .tooltip-fade-leave-active {
  transition: opacity 0.1s ease;
}
.tooltip-fade-enter-from, .tooltip-fade-leave-to {
  opacity: 0;
}
</style>
