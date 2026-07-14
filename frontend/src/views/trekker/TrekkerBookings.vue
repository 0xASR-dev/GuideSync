<template>
  <div>
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">My Bookings</h2>
      <button class="btn btn-outline-success" :disabled="exporting" @click="exportCsv">
        {{ exporting ? 'Preparing...' : 'Export CSV' }}
      </button>
    </div>

    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <table class="table table-bordered bg-white">
      <thead class="table-light">
        <tr><th>Trek</th><th>Location</th><th>Status</th><th>Booked On</th><th>Starts</th><th>Action</th></tr>
      </thead>
      <tbody>
        <tr v-for="b in bookings" :key="b.id">
          <td>{{ b.trek_name }}</td>
          <td>{{ b.location }}</td>
          <td>
            <span class="badge"
                  :class="{ 'bg-primary': b.status === 'Booked', 'bg-success': b.status === 'Completed', 'bg-danger': b.status === 'Cancelled' }">
              {{ b.status }}
            </span>
          </td>
          <td>{{ b.booking_date }}</td>
          <td>{{ b.start_date }}</td>
          <td>
            <button v-if="b.status === 'Booked'" class="btn btn-sm btn-outline-danger" @click="cancel(b.id)">
              Cancel
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <p v-if="bookings.length === 0" class="text-muted">You have no bookings yet.</p>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'TrekkerBookings',
  data() {
    return { bookings: [], message: '', exporting: false }
  },
  async mounted() {
    await this.load()
  },
  methods: {
    async load() {
      const res = await api.get('/trekker/bookings')
      this.bookings = res.data.bookings
    },
    async cancel(id) {
      try {
        await api.patch(`/trekker/bookings/${id}/cancel`)
        this.message = 'Booking cancelled'
        await this.load()
      } catch (err) {
        this.message = err.response?.data?.message || 'Error'
      }
    },
    // Async CSV export: start task -> poll status -> download file.
    async exportCsv() {
      this.exporting = true
      this.message = 'Generating CSV in the background...'
      try {
        const start = await api.post('/trekker/export/bookings')
        const taskId = start.data.task_id
        await this.pollAndDownload(taskId, 0)
      } catch (err) {
        this.message = 'Export failed'
        this.exporting = false
      }
    },
    async pollAndDownload(taskId, attempt) {
      if (attempt > 15) {
        this.message = 'Export timed out. Is the Celery worker running?'
        this.exporting = false
        return
      }
      const res = await api.get(`/trekker/export/${taskId}`)
      if (res.data.status === 'SUCCESS') {
        // download the file as a blob (needs the auth header, so use axios)
        const file = await api.get(`/trekker/export/${taskId}/download`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([file.data]))
        const link = document.createElement('a')
        link.href = url
        link.download = 'my_bookings.csv'
        link.click()
        this.message = 'CSV downloaded!'
        this.exporting = false
      } else if (res.data.status === 'FAILURE') {
        this.message = 'Export failed'
        this.exporting = false
      } else {
        setTimeout(() => this.pollAndDownload(taskId, attempt + 1), 2000)
      }
    },
  },
}
</script>
