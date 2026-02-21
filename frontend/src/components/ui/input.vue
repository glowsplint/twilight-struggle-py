<script setup lang="ts">
import { cn } from '@/lib/utils'

withDefaults(defineProps<{
  modelValue?: string | number
  placeholder?: string
  type?: string
  disabled?: boolean
}>(), {
  type: 'text',
})

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>

<template>
  <input
    :type="type"
    :value="modelValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :class="
      cn(
        'flex h-9 w-full rounded-md border border-border bg-transparent px-3 py-1 text-sm',
        'transition-colors placeholder:text-muted-foreground',
        'focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
        'disabled:cursor-not-allowed disabled:opacity-50',
      )
    "
    @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
  />
</template>
