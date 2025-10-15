<script setup>
import { ref, watch, nextTick } from 'vue'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

const props = defineProps({
  messages: { type: Array, required: true },
})

const chatContainer = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

watch(
  () => props.messages,
  () => {
    scrollToBottom()
  },
  { deep: true, immediate: true },
)
</script>

<template>
  <div ref="chatContainer" class="flex-1 p-4 overflow-y-auto bg-gray-50">
    <div
      v-for="message in messages"
      :key="message.id"
      :class="[
        'flex mb-4',
        message.sender === 'User' ? 'justify-end' : 'justify-start',
      ]"
    >
      <div
        :class="[
          'flex items-end max-w-[70%]',
          message.sender === 'User' ? 'flex-row-reverse' : 'flex-row',
        ]"
      >
        <Avatar class="h-8 w-8">
          <AvatarImage
            :src="message.sender === 'User' ? 'https://github.com/radix-vue.png' : 'https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y'"
            :alt="message.sender"
          />
          <AvatarFallback>{{ message.sender.substring(0, 2) }}</AvatarFallback>
        </Avatar>
        <Card
          :class="[
            'mx-2 p-3 rounded-lg',
            message.sender === 'User'
              ? 'bg-blue-500 text-white rounded-br-none'
              : 'bg-gray-200 text-gray-800 rounded-bl-none',
          ]"
        >
          <CardContent class="p-0">
            <p>{{ message.text }}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  </div>
</template>
