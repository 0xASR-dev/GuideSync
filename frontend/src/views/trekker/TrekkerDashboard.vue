<template>
  <div>
    <h2 class="mb-4">Welcome, {{ auth.fullName }} 👋</h2>
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card text-bg-success"><div class="card-body">
          <h6>Open Treks</h6><h2>{{ openTreks.length }}</h2>
        </div></div>
      </div>
      <div class="col-md-4">
        <div class="card text-bg-primary"><div class="card-body">
          <h6>My Bookings</h6><h2>{{ myBookingsCount }}</h2>
        </div></div>
      </div>
    </div>

    <h4>Open Treks</h4>
    <div class="row g-3">
      <div class="col-md-4" v-for="t in openTreks" :key="t.id">
        <div class="card h-100">
          <div class="card-body">
            <h5>{{ t.name }}</h5>
            <p class="mb-1 text-muted">{{ t.location }}</p>
            <span class="badge bg-info">{{ t.difficulty }}</span>
            <p class="mt-2 mb-0">Slots left: {{ t.available_slots }}</p>
          </div>
        </div>
      </div>
    </div>
    <router-link to="/trekker/treks" class="btn btn-success mt-3">Browse & Book</router-link>
  </div>
</template>

<script>
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'

export default {
  name: 'TrekkerDashboard',
  data() {
    return { openTreks: [], myBookingsCount: 0 }
  },
  computed: {
    auth() {
      return useAuthStore()
    },
  },
  async mounted() {
    const res = await api.get('/trekker/dashboard')
    this.openTreks = res.data.open_treks
    this.myBookingsCount = res.data.my_bookings_count
  },
}
</script>
