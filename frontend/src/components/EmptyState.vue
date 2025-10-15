<template>
  <div class="flex flex-col items-center justify-center py-16 px-4">
    <div class="w-32 h-32 ocean-gradient-subtle rounded-full flex items-center justify-center mb-6">
      <svg
        class="w-16 h-16 text-ocean-500 animate-wave"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
    </div>

    <h3 class="text-2xl font-semibold text-ocean-800 mb-2">
      {{ title }}
    </h3>

    <p class="text-foam-600 text-center max-w-md mb-8">
      {{ description }}
    </p>

    <slot name="action">
      <Button class="bg-ocean-600 hover:bg-ocean-700 text-white">
        {{ actionText }}
      </Button>
    </slot>
  </div>
</template>

<script setup>
import { Button } from '@/components/ui/button'

defineProps({
  title: {
    type: String,
    default: 'Nenhum notebook encontrado',
  },
  description: {
    type: String,
    default: 'Crie seu primeiro notebook para começar a analisar seus dados',
  },
  actionText: {
    type: String,
    default: 'Criar Notebook',
  },
})
</script>
