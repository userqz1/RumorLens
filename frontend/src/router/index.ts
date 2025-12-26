import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/auth',
      component: () => import('@/layouts/AuthLayout.vue'),
      children: [
        {
          path: 'login',
          name: 'Login',
          component: () => import('@/views/auth/LoginView.vue'),
        },
        {
          path: 'register',
          name: 'Register',
          component: () => import('@/views/auth/RegisterView.vue'),
        },
      ],
    },
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Home',
          component: () => import('@/views/HomeView.vue'),
        },
        {
          path: 'detection',
          name: 'Detection',
          component: () => import('@/views/detection/SingleDetection.vue'),
        },
        {
          path: 'detection/batch',
          name: 'BatchDetection',
          component: () => import('@/views/detection/BatchDetection.vue'),
        },
        {
          path: 'history',
          name: 'History',
          component: () => import('@/views/history/HistoryView.vue'),
        },
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/analysis/DashboardView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

// Navigation guard
router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.accessToken) {
      // No token, redirect to login
      return next({ name: 'Login', query: { redirect: to.fullPath } })
    }

    // Token exists but no user data - try to fetch
    if (!authStore.user) {
      try {
        await authStore.fetchUser()
      } catch (e) {
        // Failed to fetch user, redirect to login
        return next({ name: 'Login', query: { redirect: to.fullPath } })
      }
    }
  }

  // Redirect authenticated users away from auth pages
  if (to.path.startsWith('/auth') && authStore.isAuthenticated) {
    return next({ name: 'Home' })
  }

  next()
})

export default router
