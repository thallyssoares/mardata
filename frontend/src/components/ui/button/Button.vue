<script setup>
import { computed } from 'vue'
import { Primitive } from 'radix-vue'
import { buttonVariants } from './button'
import { cn } from '@/lib/utils'

const props = defineProps({
  variant: { type: String, default: 'default' },
  size: { type: String, default: 'default' },
  class: { type: String, default: '' },
  as: { type: String, default: 'button' },
  asChild: { type: Boolean, default: false },
})

const delegatedProps = computed(() => {
  const { variant, size, class: _, ...delegated } = props
  return delegated
})
</script>

<template>
  <Primitive
    :as="as"
    :as-child="asChild"
    :class="cn(buttonVariants({ variant, size }), props.class)"
    v-bind="delegatedProps"
  >
    <slot />
  </Primitive>
</template>
