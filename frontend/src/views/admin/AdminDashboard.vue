<template>
  <div>
    <PageHeader title="Admin Dashboard" subtitle="Overview of treks, people and bookings" />

    <div class="row g-3">
      <div class="col-6 col-lg-3">
        <StatCard label="Total Treks" :value="stats.total_treks" variant="green" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Trekkers" :value="stats.total_trekkers" variant="blue" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Trek Staff" :value="stats.total_staff" variant="amber" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Bookings" :value="stats.total_bookings" variant="slate" />
      </div>
    </div>

    <div class="row g-3 mt-1">
      <div class="col-md-6">
        <div class="card hoverable h-100"><div class="card-body">
          <h5 class="section-title">Manage</h5>
          <div class="d-flex flex-wrap gap-2">
            <router-link to="/admin/treks" class="btn btn-success btn-sm">Manage Treks</router-link>
            <router-link to="/admin/staff" class="btn btn-outline-success btn-sm">Manage Staff</router-link>
            <router-link to="/admin/users" class="btn btn-outline-success btn-sm">Manage Users</router-link>
          </div>
        </div></div>
      </div>
      <div class="col-md-6">
        <div class="card hoverable h-100"><div class="card-body">
          <h5 class="section-title">Insights</h5>
          <div class="d-flex flex-wrap gap-2">
            <router-link to="/admin/bookings" class="btn btn-outline-secondary btn-sm">All Bookings</router-link>
            <router-link to="/admin/reports" class="btn btn-outline-secondary btn-sm">Analytics & Charts</router-link>
          </div>
        </div></div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'

export default {
  name: 'AdminDashboard',
  components: { PageHeader, StatCard },
  data() {
    return { stats: { total_treks: 0, total_trekkers: 0, total_staff: 0, total_bookings: 0 } }
  },
  async mounted() {
    const res = await api.get('/admin/dashboard')
    this.stats = res.data
  },
}
</script>
