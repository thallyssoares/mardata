<template>
  <Card
    class="hover:shadow-ocean-lg transition-all duration-300 border-ocean-100 group relative"
  >
    <div @click="$emit('click')" class="cursor-pointer">
      <CardHeader>
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <CardTitle class="text-ocean-800 group-hover:text-ocean-600 transition-colors pr-8">
              {{ notebook.title }}
            </CardTitle>
          </div>
          <div
            class="w-10 h-10 ocean-gradient-subtle rounded-lg flex items-center justify-center flex-shrink-0 ml-3"
          >
            <svg
              class="w-6 h-6 text-ocean-600"
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
        </div>
      </CardHeader>
      <CardContent>
          <div class="flex items-center text-sm text-foam-600">
            <svg
              class="w-4 h-4 mr-2 text-ocean-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            Criado em: {{ formatDate(notebook.created_at) }}
          </div>
      </CardContent>
    </div>
    <button
      @click.stop="$emit('delete', notebook.id)"
      class="absolute top-3 right-3 text-gray-400 hover:text-red-500 transition-colors p-1 rounded-full bg-white/50 hover:bg-red-100/50 opacity-0 group-hover:opacity-100"
      aria-label="Deletar notebook"
    >
      <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm4 0a1 1 0 012 0v6a1 1 0 11-2 0V8z" clip-rule="evenodd"></path>
      </svg>
    </button>
  </Card>
</template>

<script setup>
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

defineProps({
  notebook: {
    type: Object,
    required: true,
  },
})

defineEmits(['click', 'delete'])

function formatDate(dateString) {
  if (!dateString) return 'Data inválida';
  const date = new Date(dateString)
  if (isNaN(date.getTime())) {
    return 'Data inválida';
  }
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}
</script>
