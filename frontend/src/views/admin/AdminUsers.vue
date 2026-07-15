<template>
  <div>
    <PageHeader title="Manage Users" subtitle="Trekker accounts — blacklist or delete" />

    <div v-if="message" class="alert alert-info py-2">{{ message }}</div>

    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3">
        <StatCard label="Total Users" :value="users.length" variant="blue" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Active" :value="activeCount" variant="green" />
      </div>
    </div>

    <div class="table-wrap">
      <table class="table table-hover align-middle">
        <thead>
          <tr>
            <th>Name</th><th>Email</th><th>Phone</th><th>Status</th><th class="text-end">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in users" :key="u.id">
            <td class="fw-semibold">{{ u.full_name }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.phone }}</td>
            <td><StatusPill :status="statusOf(u)" /></td>
            <td class="text-end text-nowrap">
              <button class="btn btn-sm btn-outline-danger" @click="blacklist(u.id)">
                {{ u.is_blacklisted ? 'Un-blacklist' : 'Blacklist' }}
              </button>
              <button class="btn btn-sm btn-danger ms-1" @click="remove(u.id, u.full_name)">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="users.length === 0" class="empty-state mb-0">No trekkers registered yet.</p>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'
import StatusPill from '../../components/StatusPill.vue'

export default {
  name: 'AdminUsers',
  components: { PageHeader, StatCard, StatusPill },
  data() {
    return { users: [], message: '' }
  },
  computed: {
    activeCount() {
      return this.users.filter((u) => !u.is_blacklisted).length
    },
  },
  async mounted() {
    await this.load()
  },
  methods: {
    statusOf(u) {
      return u.is_blacklisted ? 'Blacklisted' : 'Active'
    },
    async load() {
      const res = await api.get('/admin/users')
      this.users = res.data.users
    },
    async blacklist(id) {
      await api.patch(`/admin/users/${id}/blacklist`)
      await this.load()
    },
    async remove(id, name) {
      if (!confirm(`Permanently delete "${name}"? This also removes their booking history and cannot be undone.`)) return
      await api.delete(`/admin/users/${id}`)
      this.message = 'User deleted'
      await this.load()
    },
  },
}
</script>
