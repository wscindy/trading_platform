import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Login', component: () => import('../views/LoginView.vue') },
  { path: '/register', name: 'Register', component: () => import('../views/RegisterView.vue') },
  { path: '/dashboard', name: 'Dashboard', component: () => import('../views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/trade', name: 'Trade', component: () => import('../views/TradeView.vue'), meta: { requiresAuth: true } },
  { path: '/fund', name: 'Fund', component: () => import('../views/FundView.vue'), meta: { requiresAuth: true } },
  { path: '/orders', name: 'Orders', component: () => import('../views/OrdersView.vue'), meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('user')
  if (to.meta.requiresAuth && !isLoggedIn) {
    next('/')
  } else {
    next()
  }
})

export default router
