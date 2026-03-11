<template>
  <div v-if="isAuthPage">
    <router-view />
  </div>
  <div v-else class="app-layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <svg viewBox="0 0 32 32" fill="none">
          <rect x="2" y="2" width="28" height="28" rx="6" stroke="currentColor" stroke-width="2"/>
          <path d="M8 22V14l5 4 5-8v12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="24" cy="10" r="3" fill="currentColor"/>
        </svg>
        MemeStrategy
      </div>
      <nav>
        <router-link to="/dashboard">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
          Dashboard
        </router-link>
        <router-link to="/trade">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/></svg>
          Trade
        </router-link>
        <router-link to="/fund">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 3l-4 4-4-4"/><circle cx="16" cy="15" r="2"/></svg>
          Pokemon Fund
        </router-link>
        <router-link to="/orders">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          Orders
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <div class="sidebar-user" v-if="user">{{ user.username }}</div>
        <button class="btn-logout" @click="handleLogout">Log Out</button>
      </div>
    </aside>
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
import api from './api'

export default {
  name: 'App',
  data() {
    return { user: null }
  },
  computed: {
    isAuthPage() {
      return ['Login', 'Register'].includes(this.$route.name)
    },
  },
  watch: {
    '$route.name'() { this.loadUser() },
  },
  created() { this.loadUser() },
  methods: {
    loadUser() {
      const stored = localStorage.getItem('user')
      if (stored) {
        try { this.user = JSON.parse(stored) } catch { this.user = null }
      }
    },
    async handleLogout() {
      try { await api.post('/auth/logout') } catch { /* ignore */ }
      localStorage.removeItem('user')
      this.user = null
      this.$router.push('/')
    },
  },
}
</script>
