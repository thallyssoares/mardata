import { ref, computed, watch } from 'vue'

// Initialize user from localStorage to persist login state across page reloads
const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

// Watch for changes in the user ref and update localStorage accordingly
watch(user, (newUser) => {
  if (newUser) {
    // When user logs in, store user object in localStorage
    localStorage.setItem('user', JSON.stringify(newUser))
  } else {
    // When user logs out, remove user object from localStorage
    localStorage.removeItem('user')
  }
})

// isAuthenticated is a computed property that reactively checks if the user is logged in
const isAuthenticated = computed(() => !!user.value)

export function useAuth() {
  const login = async (email, password) => {
    // This is a mock login. In a real app, you would validate credentials against a server.
    const loggedInUser = {
      id: '1',
      email,
      name: email.split('@')[0],
      // A simple mock token to simulate a real session
      token: `mock-token-${Date.now()}`
    }
    user.value = loggedInUser
    return user.value
  }

  const loginWithGoogle = async () => {
    // This is a mock Google login.
    const loggedInUser = {
      id: '1',
      email: 'user@example.com',
      name: 'User',
      token: `mock-token-google-${Date.now()}`
    }
    user.value = loggedInUser
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
