<script setup>
import { AvatarImage } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps({
  class: { type: String, default: '' },
  src: { type: String, default: '' },
})
</script>

<template>
  <AvatarImage
    :src="src"
    :class="cn('aspect-square h-full w-full', props.class)"
  />
</template>
