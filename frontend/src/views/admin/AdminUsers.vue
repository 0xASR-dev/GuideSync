<template>
  <div>
    <h2 class="mb-4">Manage Users (Trekkers)</h2>
    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <table class="table table-bordered bg-white">
      <thead class="table-light">
        <tr><th>Name</th><th>Email</th><th>Phone</th><th>Status</th><th>Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id">
          <td>{{ u.full_name }}</td>
          <td>{{ u.email }}</td>
          <td>{{ u.phone }}</td>
          <td>
            <span v-if="u.is_blacklisted" class="badge bg-danger">Blacklisted</span>
            <span v-else-if="!u.is_active" class="badge bg-secondary">Deactivated</span>
            <span v-else class="badge bg-success">Active</span>
          </td>
          <td>
            <button class="btn btn-sm btn-outline-warning" @click="deactivate(u.id)">
              {{ u.is_active ? 'Deactivate' : 'Activate' }}
            </button>
            <button class="btn btn-sm btn-outline-danger ms-1" @click="blacklist(u.id)">
              {{ u.is_blacklisted ? 'Un-blacklist' : 'Blacklist' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'AdminUsers',
  data() {
    return { users: [], message: '' }
  },
  async mounted() {
    await this.load()
  },
  methods: {
    async load() {
      const res = await api.get('/admin/users')
      this.users = res.data.users
    },
    async deactivate(id) {
      await api.patch(`/admin/users/${id}/deactivate`)
      await this.load()
    },
    async blacklist(id) {
      await api.patch(`/admin/users/${id}/blacklist`)
      await this.load()
    },
  },
}
</script>
