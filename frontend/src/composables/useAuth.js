import { useAuthStore } from '@/stores/authStore'
import { storeToRefs } from 'pinia'

export function useAuth() {
  const store = useAuthStore()

  // storeToRefs makes sure we get reactive refs from the store
  const { user, isAuthenticated } = storeToRefs(store)

  // The actions can be directly destructured
  const { login, loginWithGoogle, logout } = store

  return {
    user,
    isAuthenticated,
    login,
    loginWithGoogle,
    logout,
  }
}
