<template>
  <div>
    <h2 class="mb-4">My Assigned Treks</h2>
    <p v-if="treks.length === 0" class="text-muted">No treks assigned to you yet.</p>

    <div class="row g-3">
      <div class="col-md-4" v-for="t in treks" :key="t.id">
        <div class="card h-100">
          <div class="card-body">
            <h5>{{ t.name }}</h5>
            <p class="mb-1">Status: <span class="badge bg-secondary">{{ t.status }}</span></p>
            <p class="mb-1">Slots: {{ t.available_slots }}/{{ t.total_slots }}</p>
            <p class="mb-2">Booked: {{ t.booked_count }}</p>
            <router-link :to="`/staff/treks/${t.id}`" class="btn btn-success btn-sm">Manage</router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'StaffDashboard',
  data() {
    return { treks: [] }
  },
  async mounted() {
    const res = await api.get('/tstaff/dashboard')
    this.treks = res.data.treks
  },
}
</script>
