import { ref } from 'vue'
import apiClient from '@/lib/apiClient'

const VITE_API_WEBSOCKET_URL = import.meta.env.VITE_API_WEBSOCKET_URL || 'ws://localhost:8000';

export function useChat() {
  const messages = ref([])
  const notebookTitle = ref('Nova Análise')
  const uploadedFiles = ref([])
  const isLoading = ref(false)
  const isHistoryLoading = ref(false)
  let socket = null;

  const addMessage = (role, content, type = 'text', isStreaming = false) => {
    messages.value.push({
      id: Date.now() + Math.random(),
      role,
      content,
      type,
      isStreaming,
      created_at: new Date().toISOString(),
    })
  }

  const loadNotebook = async (notebookId) => {
    isHistoryLoading.value = true;
    clearMessages();
    try {
      const response = await apiClient.get(`/notebooks/${notebookId}`);
      const notebook = response.data;
      notebookTitle.value = notebook.title;
      uploadedFiles.value = notebook.files;
      // The backend returns messages with role/content, which now matches our format
      messages.value = notebook.messages.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      connectWebSocket(notebookId);
    } catch (error) {
      console.error('Error loading notebook:', error);
      addMessage('System', `Erro ao carregar o notebook: ${error.message}`);
    } finally {
      isHistoryLoading.value = false;
    }
  };

  const connectWebSocket = (notebookId) => {
    if (socket) {
      socket.close();
    }

    const wsUrl = `${VITE_API_WEBSOCKET_URL}/api/ws/chat/${notebookId}`;
    socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('WebSocket connected');
    };

    socket.onmessage = (event) => {
      console.log("WebSocket message received:", event.data);
      const data = JSON.parse(event.data);
      const lastMessage = messages.value.length > 0 ? messages.value[messages.value.length - 1] : null;

      if (data.type === 'progress') {
        if (lastMessage && lastMessage.type === 'progress') {
          messages.value.pop();
        }
        addMessage('system', `Agente [${data.agent}]: ${data.status}...`, 'progress');
      } else if (data.type === 'token') {
        isLoading.value = false; 
        if (lastMessage && lastMessage.isStreaming) {
          lastMessage.content += data.content;
        } else {
          if (lastMessage && lastMessage.type === 'progress') {
            messages.value.pop();
          }
          addMessage('assistant', data.content, 'text', true);
        }
      } else if (data.type === 'stream_end') {
        if (lastMessage && lastMessage.isStreaming) {
          lastMessage.isStreaming = false;
        }
      } else if (data.type === 'error') {
        if (lastMessage && lastMessage.type === 'progress') {
          messages.value.pop();
        }
        addMessage('system', `Erro na análise: ${data.message}`, 'text');
        isLoading.value = false;
      }
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      addMessage('system', 'WebSocket connection error.', 'text');
      isLoading.value = false;
    };
  };

  const disconnectWebSocket = () => {
    if (socket) {
      socket.close();
      socket = null;
    }
  };

  const sendMessage = async (text, notebookId) => {
    if (!text.trim()) return

    addMessage('user', text)
    isLoading.value = true

    try {
      const response = await apiClient.post(`/chat/${notebookId}`, { question: text })
      const result = response.data
      addMessage('assistant', result.answer)
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = error.response?.data?.detail || error.message
      addMessage('system', `Error: ${errorMessage}`)
    } finally {
      isLoading.value = false
    }
  }

  const clearMessages = () => {
    messages.value = []
    uploadedFiles.value = []
    notebookTitle.value = 'Nova Análise'
  }

  return {
    messages,
    notebookTitle,
    uploadedFiles,
    isLoading,
    isHistoryLoading,
    addMessage,
    sendMessage,
    clearMessages,
    connectWebSocket,
    disconnectWebSocket,
    loadNotebook,
  }
}
