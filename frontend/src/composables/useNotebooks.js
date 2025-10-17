import { ref } from 'vue'
import apiClient from '@/lib/apiClient'

export function useNotebooks() {
  const notebooks = ref([])

  const fetchNotebooks = async () => {
    try {
      const response = await apiClient.get('/notebooks');
      notebooks.value = response.data;
    } catch (error) {
      console.error('Error fetching notebooks:', error);
      // Optionally, handle the error in the UI
    }
  };

  const createNotebook = (title, description) => {
    // This would now be a POST request to the backend
    // For now, we'll just add it locally for optimistic UI
    const newNotebook = {
      id: Date.now().toString(),
      title,
      description,
      created_at: new Date().toISOString(),
      // These would come from the backend response
      filesCount: 0,
      lastInsight: 'Aguardando upload de dados',
    }
    notebooks.value.unshift(newNotebook)
    return newNotebook
  }

  const deleteNotebook = (id) => {
    // This would be a DELETE request
    const index = notebooks.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notebooks.value.splice(index, 1)
    }
  }

  const getNotebook = (id) => {
    return notebooks.value.find(n => n.id === id)
  }

  return {
    notebooks,
    fetchNotebooks,
    createNotebook,
    deleteNotebook,
    getNotebook,
  }
}
