<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1>MemeStrategy</h1>
      <p class="subtitle">Digital Asset Platform</p>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email" type="email" v-model="form.email"
            placeholder="you@example.com" autocomplete="email"
            :class="{ error: fieldErrors.email }"
          />
          <div v-if="fieldErrors.email" class="field-error">{{ fieldErrors.email }}</div>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password" type="password" v-model="form.password"
            placeholder="Enter your password" autocomplete="current-password"
            :class="{ error: fieldErrors.password }"
          />
          <div v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</div>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Sign In</span>
        </button>
      </form>

      <p class="auth-link">
        Don't have an account? <router-link to="/register">Sign up</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'LoginView',
  data() {
    return {
      form: { email: '', password: '' },
      error: '',
      fieldErrors: {},
      loading: false,
    }
  },
  methods: {
    async handleLogin() {
      this.error = ''
      this.fieldErrors = {}
      this.loading = true

      try {
        const res = await api.post('/auth/login', this.form)
        localStorage.setItem('user', JSON.stringify(res.data.user))
        this.$router.push('/dashboard')
      } catch (err) {
        const data = err.response?.data
        if (data?.details) {
          this.fieldErrors = data.details
        }
        this.error = data?.error || 'Login failed'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
