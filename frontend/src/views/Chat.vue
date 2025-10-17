<template>
  <div class="min-h-screen bg-foam-50 flex flex-col">
    <AppHeader />

    <div class="flex flex-1 overflow-hidden">
      <ChatSidebar
        :class="['hidden lg:flex']"
        :uploaded-files="uploadedFiles"
        @files-uploaded="handleFilesUploaded"
        :disabled="!!notebookId" 
      />

      <div class="flex-1 flex flex-col bg-white overflow-hidden">
        <div class="px-4 sm:px-6 py-4 border-b border-ocean-100 bg-white">
          <div class="flex items-center justify-between flex-wrap gap-3">
            <div>
              <h1 class="text-xl sm:text-2xl font-bold text-ocean-800">
                {{ notebookTitle }}
              </h1>
              <p v-if="!notebookId" class="text-xs sm:text-sm text-foam-600 mt-1">
                Faça o upload de um arquivo para iniciar uma nova análise.
              </p>
            </div>
            <div v-if="notebookId" class="flex items-center space-x-2 px-3 py-2 bg-ocean-50 rounded-lg">
              <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span class="text-xs sm:text-sm font-medium text-ocean-700">Notebook Ativo</span>
            </div>
          </div>
        </div>

        <div class="flex-1 overflow-y-auto">
          <div v-if="isHistoryLoading" class="flex items-center justify-center h-full">
            <p class="text-ocean-700">Carregando histórico do notebook...</p>
          </div>
          <ChatMessages v-else :messages="messages" />
        </div>
        
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
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AppHeader from '@/components/AppHeader.vue';
import ChatSidebar from '@/components/ChatSidebar.vue';
import ChatMessages from '@/components/ChatMessages.vue';
import ChatInput from '@/components/ChatInput.vue';
import { useChat } from '@/composables/useChat';

const route = useRoute();
const router = useRouter();

const {
  messages,
  notebookTitle,
  uploadedFiles,
  isLoading,
  isHistoryLoading,
  sendMessage,
  addMessage,
  clearMessages,
  connectWebSocket,
  disconnectWebSocket,
  loadNotebook
} = useChat();

const notebookId = ref(null);

const setupNewChat = () => {
  clearMessages();
  notebookId.value = null;
  addMessage('assistant', 'Olá! Para começar, por favor, descreva seu problema de negócio e faça o upload de um arquivo de dados na barra lateral.');
}

watch(() => route.params.id, (newId) => {
  if (newId) {
    notebookId.value = newId;
    loadNotebook(newId);
  } else {
    setupNewChat();
  }
}, { immediate: true });

async function handleFilesUploaded(data) {
  // The upload service now creates the notebook and we get back the ID.
  // We just need to navigate to the new notebook's chat page.
  router.push(`/chat/${data.notebook_id}`);
}

async function handleSendMessage(userMessageText) {
  if (!notebookId.value) {
    addMessage('system', 'Por favor, inicie uma nova análise fazendo o upload de um arquivo.');
    return;
  }
  await sendMessage(userMessageText, notebookId.value);
}

// Disconnect from WebSocket when the component is unmounted
onUnmounted(() => {
  disconnectWebSocket();
});
</script>
