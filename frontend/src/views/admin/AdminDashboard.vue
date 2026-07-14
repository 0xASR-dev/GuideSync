<template>
  <div>
    <h2 class="mb-4">Admin Dashboard</h2>
    <div class="row g-3">
      <div class="col-md-3">
        <div class="card text-bg-success"><div class="card-body">
          <h6>Total Treks</h6><h2>{{ stats.total_treks }}</h2>
        </div></div>
      </div>
      <div class="col-md-3">
        <div class="card text-bg-primary"><div class="card-body">
          <h6>Trekkers</h6><h2>{{ stats.total_trekkers }}</h2>
        </div></div>
      </div>
      <div class="col-md-3">
        <div class="card text-bg-warning"><div class="card-body">
          <h6>Staff</h6><h2>{{ stats.total_staff }}</h2>
        </div></div>
      </div>
      <div class="col-md-3">
        <div class="card text-bg-dark"><div class="card-body">
          <h6>Bookings</h6><h2>{{ stats.total_bookings }}</h2>
        </div></div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'AdminDashboard',
  data() {
    return { stats: { total_treks: 0, total_trekkers: 0, total_staff: 0, total_bookings: 0 } }
  },
  async mounted() {
    const res = await api.get('/admin/dashboard')
    this.stats = res.data
  },
}
</script>
