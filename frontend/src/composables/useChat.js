import { ref } from 'vue'
import apiClient from '@/lib/apiClient'

const VITE_API_WEBSOCKET_URL = import.meta.env.VITE_API_WEBSOCKET_URL || 'ws://localhost:8000';

export function useChat() {
  const messages = ref([])
  const isLoading = ref(false)
  let socket = null;

  const addMessage = (sender, text, type = 'text', isStreaming = false) => {
    messages.value.push({
      id: Date.now() + Math.random(),
      sender,
      text,
      type,
      isStreaming,
      timestamp: new Date().toISOString(),
    })
  }

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
        // If the last message was a progress message, replace it. Otherwise, add a new one.
        if (lastMessage && lastMessage.type === 'progress') {
          messages.value.pop();
        }
        addMessage('System', `Agente [${data.agent}]: ${data.status}...`, 'progress');
      } else if (data.type === 'token') {
        isLoading.value = false; // Analysis has started, hide main loader
        if (lastMessage && lastMessage.isStreaming) {
          lastMessage.text += data.content;
        } else {
          // First token, remove progress message and add a new streaming message
          if (lastMessage && lastMessage.type === 'progress') {
            messages.value.pop();
          }
          addMessage('AI', data.content, 'text', true);
        }
      } else if (data.type === 'stream_end') {
        if (lastMessage && lastMessage.isStreaming) {
          lastMessage.isStreaming = false;
        }
      } else if (data.type === 'error') {
        if (lastMessage && lastMessage.type === 'progress') {
          messages.value.pop();
        }
        addMessage('System', `Erro na análise: ${data.message}`, 'text');
        isLoading.value = false;
      }
    };

    socket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      addMessage('System', 'WebSocket connection error.', 'text');
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

    addMessage('User', text)
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
  }

  return {
    messages,
    isLoading,
    addMessage,
    sendMessage,
    clearMessages,
    connectWebSocket,
    disconnectWebSocket,
  }
}
