<template>
  <div class="row justify-content-center">
    <div class="col-md-7 col-lg-6">
      <PageHeader title="My Profile" subtitle="Update your personal details" />
      <div v-if="message" class="alert alert-info py-2">{{ message }}</div>

      <div class="card">
        <div class="card-body p-4">
          <form @submit.prevent="save">
            <div class="mb-3">
              <label class="form-label">Email (cannot change)</label>
              <input :value="email" class="form-control" disabled />
            </div>
            <div class="mb-3">
              <label class="form-label">Full Name</label>
              <input v-model="fullName" class="form-control" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Phone</label>
              <input v-model="phone" class="form-control" />
            </div>
            <button class="btn btn-success" type="submit">Save Changes</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import PageHeader from '../../components/PageHeader.vue'

export default {
  name: 'TrekkerProfile',
  components: { PageHeader },
  data() {
    return { email: '', fullName: '', phone: '', message: '' }
  },
  async mounted() {
    const res = await api.get('/auth/me')
    this.email = res.data.email
    this.fullName = res.data.full_name
    this.phone = res.data.phone || ''
  },
  methods: {
    async save() {
      await api.put('/trekker/profile', { full_name: this.fullName, phone: this.phone })
      this.message = 'Profile updated'
      // keep the name in the navbar fresh
      const auth = useAuthStore()
      auth.fullName = this.fullName
      localStorage.setItem('fullName', this.fullName)
    },
  },
}
</script>
