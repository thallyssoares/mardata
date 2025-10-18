<template>
  <div class="w-80 border-r border-ocean-100 bg-white flex flex-col h-full">
    <div class="p-6 border-b border-ocean-50">
      <h2 class="text-xl font-semibold text-ocean-800 mb-1">
        Fontes de Dados
      </h2>
      <p class="text-sm text-foam-600">
        Arquivos enviados para análise
      </p>
    </div>

    <div class="flex-1 overflow-y-auto p-4">
      <FileUpload @files-uploaded="$emit('files-uploaded', $event)" />

      <div v-if="uploadedFiles.length > 0" class="mt-6">
        <h3 class="text-sm font-semibold text-foam-700 mb-3 px-2">
          Arquivos Carregados
        </h3>
        <div class="space-y-2">
          <div
            v-for="file in uploadedFiles"
            :key="file.name"
            class="flex items-center p-3 rounded-lg bg-ocean-50 border border-ocean-100"
          >
            <svg
              class="w-5 h-5 text-ocean-600 mr-3 flex-shrink-0"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-ocean-800 truncate">
                {{ file.name }}
              </p>
            </div>
            <span class="ml-2 px-2 py-1 text-xs font-medium text-ocean-700 bg-ocean-100 rounded">
              Ativo
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import FileUpload from './FileUpload.vue'

defineProps({
  uploadedFiles: {
    type: Array,
    default: () => [],
  },
})

defineEmits(['files-uploaded'])
</script>
