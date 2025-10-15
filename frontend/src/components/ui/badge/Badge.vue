<script setup>
import { computed } from 'vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  variant: {
    type: String,
    default: 'default',
  },
  class: {
    type: String,
    default: '',
  },
})

const badgeClass = computed(() => {
  const baseClass = 'inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold transition-colors'
  const variants = {
    default: 'bg-ocean-100 text-ocean-800 border border-ocean-200',
    ocean: 'bg-ocean-600 text-white',
    wave: 'bg-wave-100 text-wave-800 border border-wave-200',
    success: 'bg-green-100 text-green-800 border border-green-200',
    warning: 'bg-yellow-100 text-yellow-800 border border-yellow-200',
    error: 'bg-red-100 text-red-800 border border-red-200',
    secondary: 'bg-foam-200 text-foam-800',
  }
  return cn(baseClass, variants[props.variant] || variants.default, props.class)
})
</script>

<template>
  <span :class="badgeClass">
    <slot />
  </span>
</template>
