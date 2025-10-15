<template>
  <Card class="border-ocean-100 shadow-ocean-md">
    <CardHeader class="border-b border-ocean-50">
      <CardTitle class="text-ocean-800 flex items-center">
        <svg
          class="w-5 h-5 mr-2 text-ocean-600"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
        Upload de Dados
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-6">
      <div class="space-y-5">
        <div class="space-y-2">
          <Label for="business-problem" class="text-foam-700 font-medium">
            Problema de Negócio
          </Label>
          <Textarea
            id="business-problem"
            v-model="businessProblem"
            placeholder="Ex: Por que minhas vendas caíram na última semana?"
            class="min-h-[80px] border-ocean-200 focus:border-ocean-500 focus:ring-ocean-500"
          />
        </div>

        <div class="space-y-2">
          <Label class="text-foam-700 font-medium">
            Arquivo de Dados
          </Label>
          <div
            @drop.prevent="handleDrop"
            @dragover.prevent="isDragging = true"
            @dragleave="isDragging = false"
            :class="[
              'border-2 border-dashed rounded-lg p-6 text-center transition-all cursor-pointer',
              isDragging
                ? 'border-ocean-500 bg-ocean-50'
                : 'border-ocean-200 hover:border-ocean-400 bg-foam-50',
            ]"
            @click="$refs.fileInput.click()"
          >
            <input
              ref="fileInput"
              type="file"
              class="hidden"
              @change="handleFileChange"
              accept=".csv,.xls,.xlsx"
            />
            <svg
              class="w-12 h-12 mx-auto mb-3 text-ocean-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>
            <p class="text-foam-700 font-medium mb-1">
              Clique ou arraste o arquivo aqui
            </p>
            <p class="text-sm text-foam-500">
              CSV, Excel (.xlsx, .xls)
            </p>
          </div>
        </div>

        <div v-if="selectedFiles.length > 0" class="bg-ocean-50 rounded-lg p-4">
          <div class="flex items-center">
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
                {{ selectedFiles[0].name }}
              </p>
              <p class="text-xs text-foam-600">
                {{ formatFileSize(selectedFiles[0].size) }}
              </p>
            </div>
            <button
              @click.stop="selectedFiles = []"
              class="ml-3 text-foam-500 hover:text-ocean-600"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        <Button
          @click="uploadFiles"
          :disabled="isUploading || selectedFiles.length === 0 || businessProblem.trim() === ''"
          class="w-full bg-ocean-600 hover:bg-ocean-700 text-white shadow-ocean-md"
        >
          <svg
            v-if="!isUploading"
            class="w-5 h-5 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
          <svg
            v-else
            class="w-5 h-5 mr-2 animate-spin"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            ></circle>
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
          {{ isUploading ? 'Analisando...' : 'Upload & Analisar' }}
        </Button>
      </div>
    </CardContent>
  </Card>
</template>

<script setup>
import { ref } from 'vue'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'

const selectedFiles = ref([])
const businessProblem = ref('')
const isDragging = ref(false)
const isUploading = ref(false)
const emits = defineEmits(['files-uploaded'])

function handleFileChange(event) {
  selectedFiles.value = Array.from(event.target.files)
}

function handleDrop(event) {
  isDragging.value = false
  const files = Array.from(event.dataTransfer.files)
  if (files.length > 0) {
    selectedFiles.value = files
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

async function uploadFiles() {
  if (selectedFiles.value.length === 0 || businessProblem.value.trim() === '') {
    return
  }

  isUploading.value = true
  const formData = new FormData()
  formData.append('file', selectedFiles.value[0])
  formData.append('business_problem', businessProblem.value)

  try {
    const response = await fetch('http://localhost:8000/api/upload/', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'File upload failed')
    }

    const result = await response.json()
    emits('files-uploaded', {
      files: selectedFiles.value,
      sessionId: result.session_id,
      aiInsight: result.ai_insight,
    })
    selectedFiles.value = []
    businessProblem.value = ''
  } catch (error) {
    console.error('Error uploading files:', error)
    alert(`Erro: ${error.message}`)
  } finally {
    isUploading.value = false
  }
}
</script>
