<template>
  <div class="min-h-screen bg-foam-50 flex flex-col">
    <AppHeader />

    <div class="flex flex-1 overflow-hidden">
      <ChatSidebar
        :class="['hidden lg:flex']"
        :uploaded-files="uploadedFiles"
        @files-uploaded="handleFilesUploaded"
      />

      <div class="flex-1 flex flex-col bg-white">
        <div class="px-4 sm:px-6 py-4 border-b border-ocean-100 bg-white">
          <div class="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h1 class="text-xl sm:text-2xl font-bold text-ocean-800">
                Análise de Dados
              </h1>
              <p class="text-xs sm:text-sm text-foam-600 mt-1">
                Converse com seus dados e extraia insights valiosos
              </p>
            </div>
            <div v-if="notebookId" class="flex items-center space-x-2 px-3 py-2 bg-ocean-50 rounded-lg">
              <div class="w-2 h-2 bg-ocean-500 rounded-full animate-pulse"></div>
              <span class="text-xs sm:text-sm font-medium text-ocean-700">Notebook Ativo</span>
            </div>
          </div>
        </div>

        <ChatMessages :messages="messages" />
        <ChatInput
          :is-loading="isLoading"
          :session-id="notebookId" 
          @send-message="handleSendMessage"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AppHeader from '@/components/AppHeader.vue';
import ChatSidebar from '@/components/ChatSidebar.vue';
import ChatMessages from '@/components/ChatMessages.vue';
import ChatInput from '@/components/ChatInput.vue';
import { useChat } from '@/composables/useChat';

const { messages, isLoading, sendMessage, addMessage } = useChat();

const uploadedFiles = ref([]);
const notebookId = ref(null);

// Initialize with a welcome message
addMessage('AI', 'Olá! Faça upload dos seus dados para começar a análise.');

async function handleFilesUploaded(data) {
  uploadedFiles.value = data.files;
  notebookId.value = data.notebook_id;

  addMessage(
    'System',
    `Upload concluído: ${data.files.length} arquivo(s) - ${data.files.map(f => f.name).join(', ')}`
  );
  addMessage('AI', data.aiInsight);
}

async function handleSendMessage(userMessageText) {
  if (!notebookId.value) {
    addMessage('System', 'Por favor, faça o upload de um arquivo antes de conversar.');
    return;
  }
  // The useChat composable now handles adding the user message and the API call
  await sendMessage(userMessageText, notebookId.value);
}
</script>
