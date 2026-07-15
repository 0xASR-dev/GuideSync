<template>
  <div class="auth-wrap">
    <div class="card auth-card">
      <div class="card-body p-4 p-md-5">
        <div class="auth-brand">GuideSync</div>
        <p class="text-center text-muted mb-4">Create your trekker account</p>

        <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
        <div v-if="success" class="alert alert-success py-2">{{ success }}</div>

        <form @submit.prevent="submit">
          <div class="mb-3">
            <label class="form-label">Full Name</label>
            <input v-model="fullName" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Email</label>
            <input v-model="email" type="email" class="form-control" required />
          </div>
          <div class="mb-3">
            <label class="form-label">Phone</label>
            <input v-model="phone" type="tel" class="form-control" />
          </div>
          <div class="mb-3">
            <label class="form-label">Password</label>
            <input v-model="password" type="password" class="form-control" minlength="4" required />
          </div>
          <button class="btn btn-success w-100 py-2" type="submit">Register</button>
        </form>

        <p class="mt-4 mb-0 text-center text-muted small">
          Already have an account? <router-link to="/login" class="fw-semibold">Login</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'Register',
  data() {
    return { fullName: '', email: '', phone: '', password: '', error: '', success: '' }
  },
  methods: {
    async submit() {
      this.error = ''
      this.success = ''
      try {
        await api.post('/auth/register', {
          full_name: this.fullName,
          email: this.email,
          phone: this.phone,
          password: this.password,
        })
        this.success = 'Registered! Redirecting to login...'
        setTimeout(() => this.$router.push('/login'), 1200)
      } catch (err) {
        this.error = err.response?.data?.message || 'Registration failed'
      }
    },
  },
}
</script>
