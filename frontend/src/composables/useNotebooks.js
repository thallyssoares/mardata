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
    }
  };

  const deleteNotebook = async (id) => {
    try {
      await apiClient.delete(`/notebooks/${id}`);
      // Remove the notebook from the local array
      const index = notebooks.value.findIndex(n => n.id === id);
      if (index !== -1) {
        notebooks.value.splice(index, 1);
      }
    } catch (error) {
      console.error('Error deleting notebook:', error);
      // Optionally, show an error to the user
    }
  };

  const createNotebook = (title, description) => {
    // This would now be a POST request to the backend
    const newNotebook = {
      id: Date.now().toString(),
      title,
      description,
      created_at: new Date().toISOString(),
      filesCount: 0,
      lastInsight: 'Aguardando upload de dados',
    }
    notebooks.value.unshift(newNotebook)
    return newNotebook
  }

  const getNotebook = (id) => {
    return notebooks.value.find(n => n.id === id)
  }

  return {
    notebooks,
    fetchNotebooks,
    deleteNotebook,
    createNotebook,
    getNotebook,
  }
}
