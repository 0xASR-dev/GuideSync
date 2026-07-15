<template>
  <div>
    <PageHeader title="My Bookings" subtitle="Your full trekking history">
      <button class="btn btn-success" :disabled="exporting" @click="exportCsv">
        {{ exporting ? 'Preparing…' : 'Export CSV' }}
      </button>
    </PageHeader>

    <div v-if="message" class="alert alert-info py-2">{{ message }}</div>

    <div class="table-wrap">
      <table class="table table-hover align-middle">
        <thead>
          <tr><th>Trek</th><th>Location</th><th>Status</th><th>Booked On</th><th>Starts</th><th class="text-end">Action</th></tr>
        </thead>
        <tbody>
          <tr v-for="b in bookings" :key="b.id">
            <td class="fw-semibold">{{ b.trek_name }}</td>
            <td>{{ b.location }}</td>
            <td><StatusPill :status="b.status" /></td>
            <td>{{ b.booking_date }}</td>
            <td>{{ b.start_date }}</td>
            <td class="text-end">
              <button v-if="b.status === 'Booked'" class="btn btn-sm btn-outline-danger" @click="cancel(b.id)">
                Cancel
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="bookings.length === 0" class="empty-state mb-0">You have no bookings yet.</p>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import PageHeader from '../../components/PageHeader.vue'
import StatusPill from '../../components/StatusPill.vue'

export default {
  name: 'TrekkerBookings',
  components: { PageHeader, StatusPill },
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
      this.message = 'Generating CSV in the background…'
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
        const file = await api.get(`/trekker/export/${taskId}/download`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([file.data]))
        const link = document.createElement('a')
        link.href = url
        link.download = 'my_bookings.csv'
        link.click()
        this.message = 'CSV downloaded! (also emailed to you)'
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
