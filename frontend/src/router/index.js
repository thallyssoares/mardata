import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import Chat from '../views/Chat.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }, // This route should only be accessible to unauthenticated users
  },
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }, // This route requires authentication
  },
  {
    path: '/chat',
    name: 'Chat',
    component: Chat,
    meta: { requiresAuth: true }, // This route requires authentication
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Global navigation guard
router.beforeEach((to, from, next) => {
  const { isAuthenticated } = useAuth()

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)

  if (requiresAuth && !isAuthenticated.value) {
    // If the route requires authentication and the user is not logged in,
    // redirect to the login page.
    next({ name: 'Login' })
  } else if (requiresGuest && isAuthenticated.value) {
    // If the route is for guests (like the login page) and the user is already logged in,
    // redirect to the home page.
    next({ name: 'Home' })
  } else {
    // Otherwise, allow the navigation to proceed.
    next()
  }
})

export default router
