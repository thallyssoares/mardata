import { ref } from 'vue'
import apiClient from '@/lib/apiClient' // Use the configured axios client

export function useFileUpload() {
  const selectedFiles = ref([])
  const isUploading = ref(false)
  const uploadProgress = ref(0)

  const selectFiles = (files) => {
    selectedFiles.value = Array.from(files)
  }

  const clearFiles = () => {
    selectedFiles.value = []
    uploadProgress.value = 0
  }

  const uploadFiles = async (businessProblem) => {
    if (selectedFiles.value.length === 0 || !businessProblem) {
      throw new Error('Please select files and provide a business problem')
    }

    isUploading.value = true
    uploadProgress.value = 0

    try {
      const formData = new FormData()
      formData.append('file', selectedFiles.value[0])
      formData.append('business_problem', businessProblem)

      // Use apiClient to ensure the auth interceptor is used
      const response = await apiClient.post('/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          uploadProgress.value = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || 1)
          )
        },
      })

      // Axios puts the result in the `data` property
      const result = response.data
      return result
    } catch (error) {
      // Improved error handling for Axios
      const message = error.response?.data?.detail || error.message || 'File upload failed'
      console.error('Upload error:', message)
      throw new Error(message)
    } finally {
      isUploading.value = false
    }
  }

  return {
    selectedFiles,
    isUploading,
    uploadProgress,
    selectFiles,
    clearFiles,
    uploadFiles,
  }
}
