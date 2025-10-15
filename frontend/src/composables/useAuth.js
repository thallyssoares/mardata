import { ref, computed } from 'vue'

const user = ref(null)
const isAuthenticated = computed(() => !!user.value)

export function useAuth() {
  const login = async (email, password) => {
    user.value = {
      id: '1',
      email,
      name: email.split('@')[0],
    }
    return user.value
  }

  const loginWithGoogle = async () => {
    user.value = {
      id: '1',
      email: 'user@example.com',
      name: 'User',
    }
    return user.value
  }

  const logout = () => {
    user.value = null
  }

  return {
    user,
    isAuthenticated,
    login,
    loginWithGoogle,
    logout,
  }
}
