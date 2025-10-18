<template>
  <div class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 animate-fade-in">
    <Card class="w-full max-w-lg bg-white shadow-ocean-xl border-ocean-100 transform animate-slide-up">
      <CardHeader class="border-b border-ocean-100">
        <div class="flex justify-between items-center">
          <CardTitle class="text-ocean-800">Iniciar Nova Análise</CardTitle>
          <button @click="$emit('close')" class="text-foam-500 hover:text-ocean-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
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
                isDragging ? 'border-ocean-500 bg-ocean-50' : 'border-ocean-200 hover:border-ocean-400 bg-foam-50',
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
              <svg class="w-12 h-12 mx-auto mb-3 text-ocean-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p class="text-foam-700 font-medium mb-1">Clique ou arraste o arquivo aqui</p>
              <p class="text-sm text-foam-500">CSV, Excel (.xlsx, .xls)</p>
            </div>
          </div>

          <div v-if="selectedFile" class="bg-ocean-50 rounded-lg p-4">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-ocean-600 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-ocean-800 truncate">{{ selectedFile.name }}</p>
                <p class="text-xs text-foam-600">{{ formatFileSize(selectedFile.size) }}</p>
              </div>
              <button @click.stop="selectedFile = null" class="ml-3 text-foam-500 hover:text-ocean-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          <div v-if="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong class="font-bold">Erro!</strong>
            <span class="block sm:inline">{{ errorMessage }}</span>
          </div>

          <Button
            @click="uploadAndAnalyze"
            :disabled="isUploading || !selectedFile || !businessProblem.trim()"
            class="w-full bg-ocean-600 hover:bg-ocean-700 text-white shadow-ocean-md"
          >
            <svg v-if="isUploading" class="w-5 h-5 mr-2 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isUploading ? 'Analisando...' : 'Upload & Analisar' }}
          </Button>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import apiClient from '@/lib/apiClient';

const businessProblem = ref('');
const selectedFile = ref(null);
const isDragging = ref(false);
const isUploading = ref(false);
const errorMessage = ref(null);

const emit = defineEmits(['close', 'upload-success']);

function handleFileChange(event) {
  if (event.target.files.length) {
    selectedFile.value = event.target.files[0];
  }
}

function handleDrop(event) {
  isDragging.value = false;
  if (event.dataTransfer.files.length) {
    selectedFile.value = event.dataTransfer.files[0];
  }
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

async function uploadAndAnalyze() {
  if (!selectedFile.value || !businessProblem.value.trim()) return;

  isUploading.value = true;
  errorMessage.value = null;
  const file = selectedFile.value;

  try {
    // Step 1: Get presigned URL
    const presignedUrlFormData = new FormData();
    presignedUrlFormData.append('business_problem', businessProblem.value);
    presignedUrlFormData.append('file_name', file.name);
    presignedUrlFormData.append('file_type', file.type);

    const presignedUrlResponse = await apiClient.post('/upload/presigned-url/', presignedUrlFormData);
    const { presigned_url, storage_path, notebook_id } = presignedUrlResponse.data;

    // Step 2: Upload file to Supabase
    await apiClient.put(presigned_url, file, {
      headers: { 'Content-Type': file.type },
    });

    // Step 3: Notify backend to process the file
    const processFormData = new FormData();
    processFormData.append('notebook_id', notebook_id);
    processFormData.append('business_problem', businessProblem.value);
    processFormData.append('file_name', file.name);
    processFormData.append('storage_path', storage_path);

    await apiClient.post('/process-upload/', processFormData);

    // Step 4: Emit success and close
    emit('upload-success', { notebook_id });
    emit('close');

  } catch (error) {
    console.error('Error during upload process:', error);
    errorMessage.value = error.response?.data?.detail || error.message;
  } finally {
    isUploading.value = false;
  }
}
</script>
