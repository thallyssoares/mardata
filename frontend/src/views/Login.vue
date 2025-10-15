<template>
  <div class="min-h-screen flex items-center justify-center wave-pattern px-4">
    <div class="w-full max-w-md animate-fade-in">
      <div class="text-center mb-8">
        <h1 class="text-5xl font-bold text-ocean-800 mb-2">
          MarData
        </h1>
        <p class="text-foam-600 text-lg">
          Análise de dados inteligente para tráfego pago
        </p>
      </div>

      <Card class="shadow-ocean-xl border-ocean-100">
        <CardHeader class="space-y-1">
          <CardTitle class="text-2xl text-center text-ocean-800">
            Bem-vindo de volta
          </CardTitle>
          <CardDescription class="text-center">
            Entre com suas credenciais para continuar
          </CardDescription>
        </CardHeader>
        <CardContent class="space-y-4">
          <div class="space-y-2">
            <Label for="email" class="text-foam-700">Email</Label>
            <Input
              id="email"
              v-model="email"
              type="email"
              placeholder="seu@email.com"
              class="border-ocean-200 focus:border-ocean-500 focus:ring-ocean-500"
              @keydown.enter="handleLogin"
            />
          </div>
          <div class="space-y-2">
            <Label for="password" class="text-foam-700">Senha</Label>
            <Input
              id="password"
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="border-ocean-200 focus:border-ocean-500 focus:ring-ocean-500"
              @keydown.enter="handleLogin"
            />
          </div>
          <div class="flex items-center justify-between text-sm">
            <a href="#" class="text-ocean-600 hover:text-ocean-700 hover:underline">
              Esqueceu a senha?
            </a>
          </div>
          <Button
            @click="handleLogin"
            :disabled="isLoading"
            class="w-full bg-ocean-600 hover:bg-ocean-700 text-white"
          >
            {{ isLoading ? 'Entrando...' : 'Entrar' }}
          </Button>

          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <span class="w-full border-t border-foam-300" />
            </div>
            <div class="relative flex justify-center text-xs uppercase">
              <span class="bg-white px-2 text-foam-500">Ou continue com</span>
            </div>
          </div>

          <Button
            @click="handleGoogleLogin"
            variant="outline"
            class="w-full border-ocean-200 hover:bg-ocean-50 text-foam-700"
          >
            <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24">
              <path
                fill="currentColor"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="currentColor"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="currentColor"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="currentColor"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Entrar com Google
          </Button>

          <p class="text-center text-sm text-foam-600">
            Não tem uma conta?
            <a href="#" class="text-ocean-600 hover:text-ocean-700 hover:underline font-medium">
              Criar conta
            </a>
          </p>
        </CardContent>
      </Card>

      <p class="text-center text-xs text-foam-500 mt-8">
        Ao continuar, você concorda com nossos Termos de Serviço e Política de Privacidade
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

const router = useRouter()
const email = ref('')
const password = ref('')
const isLoading = ref(false)

async function handleLogin() {
  if (!email.value || !password.value) {
    alert('Por favor, preencha todos os campos')
    return
  }

  isLoading.value = true

  setTimeout(() => {
    isLoading.value = false
    router.push('/')
  }, 1000)
}

async function handleGoogleLogin() {
  router.push('/')
}
</script>
