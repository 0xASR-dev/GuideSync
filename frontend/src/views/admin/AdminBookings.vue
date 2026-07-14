<template>
  <div>
    <h2 class="mb-4">All Bookings</h2>
    <table class="table table-bordered bg-white">
      <thead class="table-light">
        <tr><th>#</th><th>Trekker</th><th>Trek</th><th>Status</th><th>Date</th></tr>
      </thead>
      <tbody>
        <tr v-for="b in bookings" :key="b.id">
          <td>{{ b.id }}</td>
          <td>{{ b.trekker }}</td>
          <td>{{ b.trek }}</td>
          <td>{{ b.status }}</td>
          <td>{{ b.booking_date }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'AdminBookings',
  data() {
    return { bookings: [] }
  },
  async mounted() {
    const res = await api.get('/admin/bookings')
    this.bookings = res.data.bookings
  },
}
</script>
