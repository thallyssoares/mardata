import { ref } from 'vue'

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

      const response = await fetch('http://localhost:8000/api/upload/', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'File upload failed')
      }

      const result = await response.json()
      uploadProgress.value = 100
      return result
    } catch (error) {
      console.error('Upload error:', error)
      throw error
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
