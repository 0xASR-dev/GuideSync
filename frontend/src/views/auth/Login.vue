<template>
  <div class="auth-wrap">
    <div class="card auth-card">
      <div class="card-body p-4 p-md-5">
        <div class="auth-brand">GuideSync</div>
        <p class="text-center text-muted mb-4">Sign in to your account</p>

        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" type="email" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" required />
          </div>
          <button class="btn btn-success w-100 py-2" type="submit">Login</button>
        </form>

        <p class="mt-4 mb-0 text-center text-muted small">
          No account? <router-link to="/register" class="fw-semibold">Register as trekker</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { useAuthStore } from '../../stores/auth'

export default {
  name: 'Login',
  data() {
    return { email: '', password: '', error: '' }
  },
  methods: {
    async submit() {
      this.error = ''
      try {
        const auth = useAuthStore()
        const role = await auth.login(this.email, this.password)
        // send each role to its own home page
        if (role === 'admin') this.$router.push('/admin')
        else if (role === 'staff') this.$router.push('/staff')
        else this.$router.push('/trekker')
      } catch (err) {
        this.error = err.response?.data?.message || 'Login failed'
      }
    },
  },
}
</script>
