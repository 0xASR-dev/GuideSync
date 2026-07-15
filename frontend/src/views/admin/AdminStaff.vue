<template>
  <div>
    <PageHeader title="Manage Staff" subtitle="Create trek staff accounts and control access" />

    <div v-if="message" class="alert alert-info py-2">{{ message }}</div>

    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3">
        <StatCard label="Total Staff" :value="staff.length" variant="amber" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Active" :value="activeCount" variant="green" />
      </div>
    </div>

    <!-- Create staff -->
    <div class="card mb-4">
      <div class="card-body">
        <h5 class="section-title">Create Staff Account</h5>
        <form @submit.prevent="create" class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Full name</label>
            <input v-model="form.full_name" class="form-control" required />
          </div>
          <div class="col-md-4">
            <label class="form-label">Email</label>
            <input v-model="form.email" type="email" class="form-control" required />
          </div>
          <div class="col-md-4">
            <label class="form-label">Phone</label>
            <input v-model="form.phone" type="tel" class="form-control" />
          </div>
          <div class="col-md-4">
            <label class="form-label">Password</label>
            <input v-model="form.password" type="password" class="form-control" minlength="4" required />
          </div>
          <div class="col-md-8">
            <label class="form-label">Bio (optional)</label>
            <input v-model="form.bio" class="form-control" />
          </div>
          <div class="col-12">
            <button class="btn btn-success" type="submit">Create Staff</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Staff table -->
    <div class="table-wrap">
      <table class="table table-hover align-middle">
        <thead>
          <tr>
            <th>Name</th><th>Email</th><th>Phone</th><th>Bio</th>
            <th>Status</th><th class="text-end">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in staff" :key="s.id">
            <td class="fw-semibold">{{ s.full_name }}</td>
            <td>{{ s.email }}</td>
            <td>{{ s.phone }}</td>
            <td class="text-muted">{{ s.bio }}</td>
            <td><StatusPill :status="statusOf(s)" /></td>
            <td class="text-end text-nowrap">
              <button class="btn btn-sm btn-outline-warning" @click="deactivate(s.id)">
                {{ s.is_active ? 'Deactivate' : 'Activate' }}
              </button>
              <button class="btn btn-sm btn-outline-danger ms-1" @click="blacklist(s.id)">
                {{ s.is_blacklisted ? 'Un-blacklist' : 'Blacklist' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="staff.length === 0" class="empty-state mb-0">No staff accounts yet.</p>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'
import StatusPill from '../../components/StatusPill.vue'

export default {
  name: 'AdminStaff',
  components: { PageHeader, StatCard, StatusPill },
  data() {
    return {
      staff: [],
      form: { full_name: '', email: '', phone: '', password: '', bio: '' },
      message: '',
    }
  },
  computed: {
    activeCount() {
      return this.staff.filter((s) => s.is_active && !s.is_blacklisted).length
    },
  },
  async mounted() {
    await this.load()
  },
  methods: {
    statusOf(s) {
      if (s.is_blacklisted) return 'Blacklisted'
      if (!s.is_active) return 'Deactivated'
      return 'Active'
    },
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
    // Staff share the same account toggle endpoints as users (any non-admin id).
    async deactivate(id) {
      await api.patch(`/admin/users/${id}/deactivate`)
      this.message = 'Staff account updated'
      await this.load()
    },
    async blacklist(id) {
      await api.patch(`/admin/users/${id}/blacklist`)
      this.message = 'Staff account updated'
      await this.load()
    },
  },
}
</script>
