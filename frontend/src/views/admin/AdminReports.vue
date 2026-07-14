<template>
  <div>
    <h2 class="mb-4">Analytics</h2>

    <div class="row g-4">
      <!-- Popular treks: bar chart -->
      <div class="col-lg-7">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="mb-3">Popular Treks (by bookings)</h5>
            <p v-if="popular.labels.length === 0" class="text-muted">No treks yet.</p>
            <Bar v-else :data="barData" :options="barOptions" />
          </div>
        </div>
      </div>

      <!-- Booking status: doughnut chart -->
      <div class="col-lg-5">
        <div class="card h-100">
          <div class="card-body">
            <h5 class="mb-3">Booking Status</h5>
            <p v-if="totalBookings === 0" class="text-muted">No bookings yet.</p>
            <Doughnut v-else :data="statusData" :options="doughnutOptions" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import { Bar, Doughnut } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
} from 'chart.js'

// Register only the pieces we use.
ChartJS.register(
  Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale, ArcElement,
)

export default {
  name: 'AdminReports',
  components: { Bar, Doughnut },
  data() {
    return {
      popular: { labels: [], counts: [] },
      status: { Booked: 0, Completed: 0, Cancelled: 0 },
    }
  },
  computed: {
    // Chart.js redraws automatically whenever these reactive computed
    // objects change -> no manual re-render, no page reload.
    barData() {
      return {
        labels: this.popular.labels,
        datasets: [
          {
            label: 'Bookings',
            data: this.popular.counts,
            backgroundColor: '#198754',
            borderRadius: 4,
          },
        ],
      }
    },
    barOptions() {
      return {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
      }
    },
    totalBookings() {
      return this.status.Booked + this.status.Completed + this.status.Cancelled
    },
    statusData() {
      return {
        labels: ['Booked', 'Completed', 'Cancelled'],
        datasets: [
          {
            data: [this.status.Booked, this.status.Completed, this.status.Cancelled],
            backgroundColor: ['#0d6efd', '#198754', '#dc3545'],
          },
        ],
      }
    },
    doughnutOptions() {
      return {
        responsive: true,
        plugins: { legend: { position: 'bottom' } },
      }
    },
  },
  async mounted() {
    const res = await api.get('/admin/reports/analytics')
    this.popular = res.data.popular_treks
    this.status = res.data.booking_status
  },
}
</script>
