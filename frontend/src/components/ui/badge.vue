<script setup lang="ts">
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = withDefaults(defineProps<{
  variant?: 'default' | 'secondary' | 'destructive' | 'outline' | 'ussr' | 'us' | 'success' | 'warning'
}>(), {
  variant: 'default',
})

const variantClasses: Record<string, string> = {
  default: 'bg-primary text-primary-foreground',
  secondary: 'bg-muted text-muted-foreground',
  destructive: 'bg-destructive text-white',
  outline: 'border border-border text-foreground',
  ussr: 'bg-ussr text-white',
  us: 'bg-us text-white',
  success: 'bg-emerald-700 text-white',
  warning: 'bg-amber-600 text-black',
}

const classes = computed(() =>
  cn(
    'inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium transition-colors',
    variantClasses[props.variant],
  ),
)
</script>

<template>
  <span :class="classes"><slot /></span>
</template>
