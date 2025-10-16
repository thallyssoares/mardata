import { defineStore } from 'pinia'
import { ref } from 'vue'
import { supabase } from '@/lib/supabaseClient'
import apiClient from '@/lib/apiClient' // Import apiClient

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)

  async function login(email, password) {
    // The backend expects URL-encoded form data for OAuth2PasswordRequestForm
    const params = new URLSearchParams()
    params.append('username', email)
    params.append('password', password)

    try {
      // Call the backend token endpoint
      const { data } = await apiClient.post('/auth/token', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })

      // The backend returns the session. Set it in the supabase-js client.
      // This will trigger onAuthStateChange and update the state automatically.
      const { error } = await supabase.auth.setSession({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
      })

      if (error) throw error

      // The onAuthStateChange listener will set user and isAuthenticated
    } catch (error) {
      console.error('Login failed:', error)
      // Re-throw the error so the component can handle it (e.g., show a message)
      throw new Error(error.response?.data?.detail || error.message)
    }
  }

  async function loginWithGoogle() {
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
    })
    if (error) throw error
  }

  async function logout() {
    try {
      // Call the backend logout endpoint first
      await apiClient.post('/auth/logout')
    } catch (error) {
      // Even if backend logout fails, try to log out locally
      console.error('Backend logout failed, proceeding with local logout:', error)
    } finally {
      // Always perform local sign out to clear session
      const { error } = await supabase.auth.signOut()
      if (error) {
        console.error('Local Supabase signout failed:', error)
        throw error
      }
      // onAuthStateChange will handle state updates
    }
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