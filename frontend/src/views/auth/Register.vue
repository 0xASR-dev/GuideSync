<template>
  <div class="row justify-content-center">
    <div class="col-md-5">
      <div class="card shadow-sm">
        <div class="card-body">
          <h3 class="card-title mb-3">Register as Trekker</h3>

          <div v-if="error" class="alert alert-danger">{{ error }}</div>
          <div v-if="success" class="alert alert-success">{{ success }}</div>

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
              <input v-model="phone" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" required />
            </div>
            <button class="btn btn-success w-100" type="submit">Register</button>
          </form>
        </div>
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
