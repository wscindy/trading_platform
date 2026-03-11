<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1>Create Account</h1>
      <p class="subtitle">Join MemeStrategy Platform</p>

      <div v-if="error" class="alert alert-error">{{ error }}</div>
      <div v-if="success" class="alert alert-success">{{ success }}</div>

      <form @submit.prevent="handleRegister">
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
          <label for="username">Username</label>
          <input
            id="username" type="text" v-model="form.username"
            placeholder="Choose a username" autocomplete="username"
            :class="{ error: fieldErrors.username }"
          />
          <div v-if="fieldErrors.username" class="field-error">{{ fieldErrors.username }}</div>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input
            id="password" type="password" v-model="form.password"
            placeholder="At least 8 characters" autocomplete="new-password"
            :class="{ error: fieldErrors.password }"
          />
          <div v-if="fieldErrors.password" class="field-error">{{ fieldErrors.password }}</div>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Create Account</span>
        </button>
      </form>

      <p class="auth-link">
        Already have an account? <router-link to="/">Sign in</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import api from '../api'

export default {
  name: 'RegisterView',
  data() {
    return {
      form: { email: '', username: '', password: '' },
      error: '',
      success: '',
      fieldErrors: {},
      loading: false,
    }
  },
  methods: {
    async handleRegister() {
      this.error = ''
      this.success = ''
      this.fieldErrors = {}
      this.loading = true

      try {
        const res = await api.post('/auth/register', this.form)
        localStorage.setItem('user', JSON.stringify(res.data.user))
        this.$router.push('/dashboard')
      } catch (err) {
        const data = err.response?.data
        if (data?.details) {
          this.fieldErrors = data.details
        }
        this.error = data?.error || 'Registration failed'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>
