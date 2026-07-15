<template>
  <div>
    <PageHeader :title="`Welcome, ${auth.fullName} 👋`" subtitle="Your treks and bookings at a glance" />

    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3">
        <StatCard label="Open Treks" :value="openTreks.length" variant="green" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="My Bookings" :value="bookings.length" variant="blue" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Active" :value="count('Booked')" variant="violet" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Completed" :value="count('Completed')" variant="slate" />
      </div>
    </div>

    
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h5 class="section-title mb-0">My Booked Treks</h5>
      <router-link to="/trekker/bookings" class="btn btn-sm btn-outline-success">View all</router-link>
    </div>
    <div class="table-wrap mb-4">
      <table class="table table-hover align-middle">
        <thead>
          <tr><th>Trek</th><th>Location</th><th>Status</th><th>Starts</th></tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td class="fw-semibold">{{ b.trek_name }}</td>
            <td>{{ b.location }}</td>
            <td><StatusPill :status="b.status" /></td>
            <td>{{ b.start_date }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="bookings.length === 0" class="empty-state mb-0">
        You have no bookings yet — browse open treks below.
      </p>
    </div>

    <!-- Available treks -->
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h5 class="section-title mb-0">Available Treks</h5>
      <router-link to="/trekker/treks" class="btn btn-sm btn-success">Browse &amp; Book</router-link>
    </div>
    <div v-if="openTreks.length === 0" class="empty-state">No open treks right now.</div>
    <div class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="t in openTreks" :key="t.id">
        <div class="card hoverable h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-1">
              <h5 class="mb-0">{{ t.name }}</h5>
              <span class="badge bg-info text-dark">{{ t.difficulty }}</span>
            </div>
            <p class="mb-2 text-muted">{{ t.location }}</p>
            <p class="mb-0">Slots left: <strong>{{ t.available_slots }}</strong></p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import { useAuthStore } from '../../stores/auth'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'
import StatusPill from '../../components/StatusPill.vue'

export default {
  name: 'TrekkerDashboard',
  components: { PageHeader, StatCard, StatusPill },
  data() {
    return { openTreks: [], bookings: [] }
  },
  computed: {
    auth() {
      return useAuthStore()
    },
  },
  async mounted() {
    const [dash, booked] = await Promise.all([
      api.get('/trekker/dashboard'),
      api.get('/trekker/bookings'),
    ])
    this.openTreks = dash.data.open_treks
    this.bookings = booked.data.bookings
  },
  methods: {
    count(status) {
      return this.bookings.filter((b) => b.status === status).length
    },
  },
}
</script>
