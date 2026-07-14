<template>
  <div>
    <h2 class="mb-4">Manage Staff</h2>
    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <div class="card mb-4">
      <div class="card-body">
        <h5>Create Staff Account</h5>
        <form @submit.prevent="create" class="row g-2">
          <div class="col-md-4"><input v-model="form.full_name" class="form-control" placeholder="Full name" required /></div>
          <div class="col-md-4"><input v-model="form.email" type="email" class="form-control" placeholder="Email" required /></div>
          <div class="col-md-4"><input v-model="form.phone" class="form-control" placeholder="Phone" /></div>
          <div class="col-md-4"><input v-model="form.password" type="password" class="form-control" placeholder="Password" required /></div>
          <div class="col-md-8"><input v-model="form.bio" class="form-control" placeholder="Bio (optional)" /></div>
          <div class="col-12"><button class="btn btn-success" type="submit">Create Staff</button></div>
        </form>
      </div>
    </div>

    <table class="table table-bordered bg-white">
      <thead class="table-light"><tr><th>Name</th><th>Email</th><th>Phone</th><th>Bio</th></tr></thead>
      <tbody>
        <tr v-for="s in staff" :key="s.id">
          <td>{{ s.full_name }}</td><td>{{ s.email }}</td><td>{{ s.phone }}</td><td>{{ s.bio }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'AdminStaff',
  data() {
    return { staff: [], form: { full_name: '', email: '', phone: '', password: '', bio: '' }, message: '' }
  },
  async mounted() {
    await this.load()
  },
  methods: {
    async load() {
      const res = await api.get('/admin/staff')
      this.staff = res.data.staff
    },
    async create() {
      try {
        await api.post('/admin/staff', this.form)
        this.message = 'Staff created'
        this.form = { full_name: '', email: '', phone: '', password: '', bio: '' }
        await this.load()
      } catch (err) {
        this.message = err.response?.data?.message || 'Error'
      }
    },
  },
}
</script>
