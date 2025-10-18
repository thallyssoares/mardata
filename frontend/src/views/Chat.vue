<template>
  <div class="min-h-screen bg-foam-50 flex flex-col">
    <AppHeader />

    <FileUploadModal 
      v-if="isUploadModalVisible" 
      @close="isUploadModalVisible = false"
      @upload-success="handleUploadSuccess"
    />

    <div class="flex flex-1 overflow-hidden">
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

        <div v-if="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong class="font-bold">Erro!</strong>
          <span class="block sm:inline">{{ errorMessage }}</span>
        </div>

        <div class="flex-1 overflow-y-auto p-4 sm:p-6">
          <ChatMessages :messages="messages" />
        </div>
        
        <ChatInput
          :is-loading="isLoading"
          :session-id="notebookId" 
          @send-message="handleSendMessage"
          @open-upload-modal="isUploadModalVisible = true"
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
import ChatMessages from '@/components/ChatMessages.vue';
import ChatInput from '@/components/ChatInput.vue';
import FileUploadModal from '@/components/FileUploadModal.vue'; // Import the modal
import { useChat } from '@/composables/useChat';

const route = useRoute();
const router = useRouter();
const { messages, isLoading, sendMessage, addMessage, setMessages } = useChat();

const isUploadModalVisible = ref(false); // State for modal visibility
const errorMessage = ref(null);

const uploadedFiles = ref([]);
const notebookId = ref(route.query.id || null);
const statisticalSummary = ref(null); // New ref to store the statistical summary

// Function to handle successful upload from the modal
function handleUploadSuccess(data) {
  isUploadModalVisible.value = false;
  router.push({ path: '/chat', query: { id: data.notebook_id } });
}

const loadNotebook = async (id) => {
    if (!id) {
        setMessages([]);
        uploadedFiles.value = [];
        notebookId.value = null;
        statisticalSummary.value = null; // Clear summary
        addMessage('AI', 'Olá! Faça upload dos seus dados para começar a análise.');
        return;
    }
    notebookId.value = id;
    isLoading.value = true;
    errorMessage.value = null;
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
        statisticalSummary.value = notebookData.analysis_cache; // Store the summary

    } catch (error) {
        console.error('Error fetching notebook data:', error);
        errorMessage.value = error.response?.data?.detail || error.message;
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


async function handleSendMessage(userMessageText) {
  if (!notebookId.value) {
    addMessage('System', 'Por favor, faça o upload de um arquivo antes de conversar.');
    return;
  }
  // Pass the statisticalSummary to sendMessage
  await sendMessage(userMessageText, notebookId.value, statisticalSummary.value);
}

</script>
