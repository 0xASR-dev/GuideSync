<template>
  <div>
    <PageHeader title="My Assigned Treks" subtitle="Treks assigned to you by the admin" />

    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3">
        <StatCard label="Assigned Treks" :value="treks.length" variant="green" />
      </div>
      <div class="col-6 col-lg-3">
        <StatCard label="Total Participants" :value="totalBooked" variant="blue" />
      </div>
    </div>

    <div v-if="treks.length === 0" class="empty-state">No treks assigned to you yet.</div>

    <div class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="t in treks" :key="t.id">
        <div class="card hoverable h-100">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <h5 class="mb-0">{{ t.name }}</h5>
              <StatusPill :status="t.status" />
            </div>
            <p class="mb-1 text-muted small">Slots available</p>
            <p class="mb-2 fw-semibold">{{ t.available_slots }} / {{ t.total_slots }}</p>
            <div class="progress mb-3" style="height: 8px">
              <div class="progress-bar bg-success"
                   :style="{ width: fillPct(t) + '%' }"></div>
            </div>
            <p class="mb-3"><span class="badge bg-primary">{{ t.booked_count }}</span> participants booked</p>
            <router-link :to="`/staff/treks/${t.id}`" class="btn btn-success btn-sm w-100">Manage Trek</router-link>
          </div>
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

export default {
  name: 'StaffDashboard',
  components: { PageHeader, StatCard, StatusPill },
  data() {
    return { treks: [] }
  },
  computed: {
    totalBooked() {
      return this.treks.reduce((sum, t) => sum + (t.booked_count || 0), 0)
    },
  },
  async mounted() {
    const res = await api.get('/tstaff/dashboard')
    this.treks = res.data.treks
  },
  methods: {
    fillPct(t) {
      if (!t.total_slots) return 0
      return Math.round(((t.total_slots - t.available_slots) / t.total_slots) * 100)
    },
  },
}
</script>
