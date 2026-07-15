<template>
  <div>
    <PageHeader title="System Report" subtitle="Full snapshot of the platform, analytics and background jobs">
      <button class="btn btn-outline-success" :disabled="exporting" @click="exportUsers">
        {{ exporting ? 'Exporting…' : 'Export Users (CSV)' }}
      </button>
    </PageHeader>

    <!-- Top-level summary tiles -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3">
        <StatCard label="Total Treks" :value="summary.treks.total" :hint="`${summary.treks.open} open`" variant="green" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Total Bookings" :value="summary.bookings.total" variant="blue" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Trekkers" :value="summary.users.trekkers" :hint="`${summary.users.active_trekkers} active`" variant="violet" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Revenue (est.)" :value="`₹${summary.revenue_estimate}`" variant="teal" />
      </div>
    </div>

    <!-- Breakdown tables -->
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <div class="card h-100"><div class="card-body">
          <h5 class="section-title">Treks by Status</h5>
          <ul class="list-group list-group-flush">
            <li v-for="(count, status) in summary.treks.by_status" :key="status"
                class="list-group-item d-flex justify-content-between align-items-center px-0">
              <StatusPill :status="status" /><span class="fw-semibold">{{ count }}</span>
            </li>
            <li v-if="isEmpty(summary.treks.by_status)" class="list-group-item px-0 text-muted">No treks yet.</li>
          </ul>
        </div></div>
      </div>
      <div class="col-md-4">
        <div class="card h-100"><div class="card-body">
          <h5 class="section-title">Bookings by Status</h5>
          <ul class="list-group list-group-flush">
            <li v-for="(count, status) in summary.bookings.by_status" :key="status"
                class="list-group-item d-flex justify-content-between align-items-center px-0">
              <StatusPill :status="status" /><span class="fw-semibold">{{ count }}</span>
            </li>
            <li v-if="isEmpty(summary.bookings.by_status)" class="list-group-item px-0 text-muted">No bookings yet.</li>
          </ul>
        </div></div>
      </div>
      <div class="col-md-4">
        <div class="card h-100"><div class="card-body">
          <h5 class="section-title">People</h5>
          <ul class="list-group list-group-flush">
            <li class="list-group-item d-flex justify-content-between px-0">New signups (this month) <span class="fw-semibold">{{ summary.users.new_signups }}</span></li>
            <li class="list-group-item d-flex justify-content-between px-0">Active trekkers <span class="fw-semibold">{{ summary.users.active_trekkers }}</span></li>
            <li class="list-group-item d-flex justify-content-between px-0">Blacklisted <span class="fw-semibold">{{ summary.users.blacklisted }}</span></li>
            <li class="list-group-item d-flex justify-content-between px-0">Total staff <span class="fw-semibold">{{ summary.staff.total }}</span></li>
            <li class="list-group-item d-flex justify-content-between px-0">Active staff <span class="fw-semibold">{{ summary.staff.active }}</span></li>
          </ul>
        </div></div>
      </div>
    </div>

    <!-- Charts -->
    <div class="row g-4 mb-4">
      <div class="col-lg-7">
        <div class="card h-100"><div class="card-body">
          <h5 class="section-title">Popular Treks (by bookings)</h5>
          <p v-if="popular.labels.length === 0" class="text-muted">No treks yet.</p>
          <Bar v-else :data="barData" :options="barOptions" />
        </div></div>
      </div>
      <div class="col-lg-5">
        <div class="card h-100"><div class="card-body">
          <h5 class="section-title">Booking Status</h5>
          <p v-if="totalBookings === 0" class="text-muted">No bookings yet.</p>
          <Doughnut v-else :data="statusData" :options="doughnutOptions" />
        </div></div>
      </div>
    </div>

    <!-- Background email jobs -->
    <div class="card">
      <div class="card-body">
        <h5 class="section-title">Background Email Jobs</h5>
        <p class="text-muted small mb-3">
          These run automatically on a schedule (daily reminders 7 AM, monthly report on the 1st).
          Trigger them here to test manually — delivered emails appear in
          <a href="http://localhost:8025" target="_blank" rel="noopener">Mailhog (http://localhost:8025)</a>.
        </p>
        <div class="d-flex flex-wrap gap-2 mb-3">
          <button class="btn btn-success" :disabled="jobRunning" @click="runJob('daily-reminders')">
            Send Daily Reminders
          </button>
          <button class="btn btn-outline-success" :disabled="jobRunning" @click="runJob('monthly-report')">
            Generate Monthly Report
          </button>
        </div>
        <div v-if="jobMessage" class="alert py-2 mb-0" :class="jobError ? 'alert-danger' : 'alert-info'">
          {{ jobMessage }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import PageHeader from '../../components/PageHeader.vue'
import StatCard from '../../components/StatCard.vue'
import StatusPill from '../../components/StatusPill.vue'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale, ArcElement,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, ArcElement)

const emptySummary = () => ({
  treks: { total: 0, by_status: {}, open: 0 },
  bookings: { total: 0, by_status: {} },
  users: { trekkers: 0, active_trekkers: 0, blacklisted: 0, new_signups: 0 },
  staff: { total: 0, active: 0 },
  revenue_estimate: 0,
  top_treks: [],
})

export default {
  name: 'AdminReports',
  components: { Bar, Doughnut, PageHeader, StatCard, StatusPill },
  data() {
    return {
      summary: emptySummary(),
      popular: { labels: [], counts: [] },
      status: { Booked: 0, Completed: 0, Cancelled: 0 },
      jobRunning: false,
      jobMessage: '',
      jobError: false,
      exporting: false,
    }
  },
  computed: {
    barData() {
      return {
        labels: this.popular.labels,
        datasets: [{ label: 'Bookings', data: this.popular.counts, backgroundColor: '#198754', borderRadius: 4 }],
      }
    },
    barOptions() {
      return { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } }
    },
    totalBookings() {
      return this.status.Booked + this.status.Completed + this.status.Cancelled
    },
    statusData() {
      return {
        labels: ['Booked', 'Completed', 'Cancelled'],
        datasets: [{ data: [this.status.Booked, this.status.Completed, this.status.Cancelled], backgroundColor: ['#0d6efd', '#198754', '#dc3545'] }],
      }
    },
    doughnutOptions() {
      return { responsive: true, plugins: { legend: { position: 'bottom' } } }
    },
  },
  async mounted() {
    const [sum, ana] = await Promise.all([
      api.get('/admin/reports/summary'),
      api.get('/admin/reports/analytics'),
    ])
    this.summary = sum.data
    this.popular = ana.data.popular_treks
    this.status = ana.data.booking_status
  },
  methods: {
    isEmpty(obj) {
      return !obj || Object.keys(obj).length === 0
    },
    // Download the allusers data
    async exportUsers() {
      this.exporting = true
      try {
        const file = await api.get('/admin/export/users', { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([file.data]))
        const link = document.createElement('a')
        link.href = url
        link.download = 'guidesync_users.csv'
        link.click()
        window.URL.revokeObjectURL(url)
      } finally {
        this.exporting = false
      }
    },
    async runJob(kind) {
      this.jobRunning = true
      this.jobError = false
      this.jobMessage = 'Queuing the job…'
      try {
        const start = await api.post(`/admin/jobs/${kind}`)
        await this.pollJob(start.data.task_id, 0)
      } catch (err) {
        this.jobError = true
        this.jobMessage = 'Could not queue the job (is Redis running?)'
        this.jobRunning = false
      }
    },
    async pollJob(taskId, attempt) {
      if (attempt > 15) {
        this.jobError = true
        this.jobMessage = 'Job timed out. Is the Celery worker running?'
        this.jobRunning = false
        return
      }
      const res = await api.get(`/admin/jobs/${taskId}`)
      if (res.data.status === 'SUCCESS') {
        this.jobMessage = `Done: ${res.data.result}. Check Mailhog at http://localhost:8025`
        this.jobRunning = false
      } else if (res.data.status === 'FAILURE') {
        this.jobError = true
        this.jobMessage = `Job failed: ${res.data.result}`
        this.jobRunning = false
      } else {
        setTimeout(() => this.pollJob(taskId, attempt + 1), 1500)
      }
    },
  },
}
</script>
