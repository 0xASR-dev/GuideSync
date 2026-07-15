<template>
  <div>
    <PageHeader title="All Bookings" subtitle="Complete historical booking data" />

    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3">
        <StatCard label="Total" :value="bookings.length" variant="slate" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Active" :value="count('Booked')" variant="blue" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Completed" :value="count('Completed')" variant="green" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Cancelled" :value="count('Cancelled')" variant="rose" />
      </div>
    </div>

    <div class="table-wrap">
      <table class="table table-hover align-middle">
        <thead>
          <tr><th>#</th><th>Trekker</th><th>Trek</th><th>Status</th><th>Date</th></tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td class="text-muted">{{ b.id }}</td>
            <td class="fw-semibold">{{ b.trekker }}</td>
            <td>{{ b.trek }}</td>
            <td><StatusPill :status="b.status" /></td>
            <td>{{ b.booking_date }}</td>
          </tr>
        </tbody>
      </table>
      <p v-if="bookings.length === 0" class="empty-state mb-0">No bookings yet.</p>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'
import StatusPill from '../../components/StatusPill.vue'

export default {
  name: 'AdminBookings',
  components: { PageHeader, StatCard, StatusPill },
  data() {
    return { bookings: [] }
  },
  async mounted() {
    const res = await api.get('/admin/bookings')
    this.bookings = res.data.bookings
  },
  methods: {
    count(status) {
      return this.bookings.filter((b) => b.status === status).length
    },
  },
}
</script>
