<script setup>
import { useVModel } from '@vueuse/core'
import { cn } from '@/lib/utils'

const props = defineProps({
  defaultValue: { type: [String, Number], default: undefined },
  modelValue: { type: [String, Number], default: undefined },
  class: { type: String, default: '' },
})

const emits = defineEmits(['update:modelValue'])

const modelValue = useVModel(props, 'modelValue', emits, {
  passive: true,
  defaultValue: props.defaultValue,
})
</script>

<template>
  <input
    v-model="modelValue"
    :class="cn(
      'flex h-10 w-full rounded-lg border-2 border-ocean-200 bg-white px-4 py-2 text-sm text-foam-900 transition-all placeholder:text-foam-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ocean-500 focus-visible:border-ocean-500 disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-foam-100 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-ocean-700',
      props.class,
    )"
  >
</template>
