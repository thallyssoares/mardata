import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/lib/supabaseClient'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  async function login(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    user.value = data.user
    isAuthenticated.value = true
  }

  async function loginWithGoogle() {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
    })
    if (error) throw error
  }

  async function logout() {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    user.value = null
    isAuthenticated.value = false
  }

  async function checkSession() {
    const { data } = await supabase.auth.getSession()
    if (data.session) {
      user.value = data.session.user
      isAuthenticated.value = true
    } else {
      user.value = null
      isAuthenticated.value = false
    }
  }

  function listenForAuthStateChange() {
    supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        user.value = session.user
        isAuthenticated.value = true
      } else {
        user.value = null
        isAuthenticated.value = false
      }
    })
  }

  return {
    user,
    isAuthenticated,
    login,
    loginWithGoogle,
    logout,
    checkSession,
    listenForAuthStateChange,
  }
})
