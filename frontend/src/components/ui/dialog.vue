<script setup lang="ts">
import { cn } from '@/lib/utils'

withDefaults(defineProps<{
  open: boolean
  maxWidth?: string
}>(), {
  maxWidth: 'max-w-md',
})

defineEmits<{
  'update:open': [value: boolean]
}>()
</script>

<template>
  <Teleport to="body">
    <Transition name="dialog">
      <div v-if="open" class="fixed inset-0 z-50 flex items-center justify-center">
        <div
          class="fixed inset-0 bg-black/60 backdrop-blur-sm"
          @click="$emit('update:open', false)"
        />
        <div
          :class="cn('relative z-50 w-full rounded-lg border border-border bg-card p-6 shadow-xl', maxWidth)"
        >
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style>
.dialog-enter-active, .dialog-leave-active {
  transition: opacity 0.15s ease;
}
.dialog-enter-from, .dialog-leave-to {
  opacity: 0;
}
</style>
