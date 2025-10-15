<script setup>
import { ref, defineEmits } from 'vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label' // Assuming Label component exists or will be created

const selectedFiles = ref([])
const businessProblem = ref('')
const emits = defineEmits(['files-uploaded'])

function handleFileChange(event) {
  selectedFiles.value = Array.from(event.target.files)
}

async function uploadFiles() {
  if (selectedFiles.value.length === 0 || businessProblem.value.trim() === '') {
    alert('Please select a file and enter a business problem.')
    return
  }

  const formData = new FormData()
  formData.append('file', selectedFiles.value[0]) // Assuming single file upload for simplicity
  formData.append('business_problem', businessProblem.value)

  try {
    const response = await fetch('http://localhost:8000/api/upload/', {
      method: 'POST',
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || 'File upload failed')
    }

    const result = await response.json()
    emits('files-uploaded', { 
      files: selectedFiles.value,
      sessionId: result.session_id,
      aiInsight: result.ai_insight
    })
    selectedFiles.value = []
    businessProblem.value = ''
  } catch (error) {
    console.error('Error uploading files:', error)
    alert(`Error: ${error.message}`)
  }
}
</script>

<template>
  <Card>
    <CardHeader>
      <CardTitle>Upload Data Files</CardTitle>
    </CardHeader>
    <CardContent>
      <div class="grid w-full items-center gap-4">
        <div class="flex flex-col space-y-1.5">
          <Label for="business-problem">Business Problem</Label>
          <Input id="business-problem" v-model="businessProblem" placeholder="e.g., Why did sales drop last week?" />
        </div>
        <div class="flex flex-col space-y-1.5">
          <Label for="data-file">Data File</Label>
          <Input id="data-file" type="file" @change="handleFileChange" accept=".csv,.xls,.xlsx" />
        </div>
        <div v-if="selectedFiles.length > 0">
          <p class="text-sm text-muted-foreground mb-2">Selected File:</p>
          <ul class="list-disc list-inside text-sm">
            <li :key="selectedFiles[0].name">{{ selectedFiles[0].name }}</li>
          </ul>
        </div>
        <Button @click="uploadFiles" :disabled="selectedFiles.length === 0 || businessProblem.trim() === ''">Upload & Analyze</Button>
      </div>
    </CardContent>
  </Card>
</template>
