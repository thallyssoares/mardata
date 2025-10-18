<template>
  <div class="min-h-screen bg-foam-50 flex flex-col">
    <AppHeader />

    <div class="flex flex-1 overflow-hidden">
      <ChatSidebar
        :class="['hidden lg:flex']"
        :uploaded-files="uploadedFiles"
        @files-uploaded="handleFilesUploaded"
      />

      <div class="flex-1 flex flex-col bg-white overflow-hidden">
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

        <div class="flex-1 overflow-y-auto">
          <ChatMessages :messages="messages" />
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
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import apiClient from '@/lib/apiClient';
import AppHeader from '@/components/AppHeader.vue';
import ChatSidebar from '@/components/ChatSidebar.vue';
import ChatMessages from '@/components/ChatMessages.vue';
import ChatInput from '@/components/ChatInput.vue';
import { useChat } from '@/composables/useChat';

const route = useRoute();
const router = useRouter();
const { messages, isLoading, sendMessage, addMessage, setMessages } = useChat();

const uploadedFiles = ref([]);
const notebookId = ref(route.query.id || null);

const loadNotebook = async (id) => {
    if (!id) {
        setMessages([]);
        uploadedFiles.value = [];
        notebookId.value = null;
        addMessage('AI', 'Olá! Faça upload dos seus dados para começar a análise.');
        return;
    }
    notebookId.value = id;
    isLoading.value = true;
    try {
        const response = await apiClient.get(`/notebooks/${id}`);
        const notebookData = response.data;

        const formattedMessages = notebookData.messages.map(msg => ({
            id: msg.id,
            sender: msg.role === 'user' ? 'User' : 'AI',
            text: msg.content,
            timestamp: msg.created_at,
        }));
        setMessages(formattedMessages);

        if (notebookData.files) {
            uploadedFiles.value = notebookData.files.map(file => ({
                name: file.file_name,
                size: file.file_size_bytes,
            }));
        }
    } catch (error) {
        console.error('Error fetching notebook data:', error);
        addMessage('System', 'Erro ao carregar o notebook.');
    } finally {
        isLoading.value = false;
    }
};

onMounted(() => {
  loadNotebook(route.query.id);
});

watch(() => route.query.id, (newId) => {
    loadNotebook(newId);
});

async function handleFilesUploaded(data) {
  router.push({ path: '/chat', query: { id: data.notebook_id } });
}

async function handleSendMessage(userMessageText) {
  if (!notebookId.value) {
    addMessage('System', 'Por favor, faça o upload de um arquivo antes de conversar.');
    return;
  }
  await sendMessage(userMessageText, notebookId.value);
}

</script>
