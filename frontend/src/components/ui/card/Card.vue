<script setup>
import { cn } from '@/lib/utils'

const props = defineProps({
  class: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div
    :class="
      cn(
        'rounded-xl border-2 border-ocean-100 bg-white text-foam-900 shadow-ocean-sm transition-shadow',
        props.class,
      )
    "
  >
    <slot />
  </div>
</template>
