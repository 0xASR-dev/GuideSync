<template>
  <div>
    <PageHeader title="Browse Treks" subtitle="Find and book your next adventure" />

    <div v-if="message" class="alert alert-info py-2">{{ message }}</div>

    <!-- Filters -->
    <div class="card mb-4"><div class="card-body">
      <div class="row g-3 align-items-end">
        <div class="col-md-3">
          <label class="form-label">Difficulty</label>
          <select v-model="filters.difficulty" class="form-select">
            <option value="">Any difficulty</option>
            <option>Easy</option><option>Moderate</option><option>Hard</option>
          </select>
        </div>
        <div class="col-md-3">
          <label class="form-label">Location</label>
          <input v-model="filters.location" class="form-control" placeholder="e.g. Manali" />
        </div>
        <div class="col-md-3">
          <label class="form-label">Duration (days)</label>
          <input v-model.number="filters.duration" type="number" min="1" class="form-control" />
        </div>
        <div class="col-md-3">
          <button class="btn btn-success me-2" @click="load">Search</button>
          <button class="btn btn-outline-secondary" @click="clearFilters">Clear</button>
        </div>
      </div>
    </div></div>

    <!-- Trek cards -->
    <div v-if="treks.length === 0" class="empty-state">No treks found. Try different filters.</div>
    <div class="row g-3">
      <div class="col-md-6 col-lg-4" v-for="t in treks" :key="t.id">
        <div class="card hoverable h-100">
          <div class="card-body d-flex flex-column">
            <div class="d-flex justify-content-between align-items-start mb-1">
              <h5 class="mb-0">{{ t.name }}</h5>
              <strong class="text-success">₹{{ t.price }}</strong>
            </div>
            <p class="mb-2 text-muted">{{ t.location }}</p>
            <div class="mb-2">
              <span class="badge bg-info text-dark me-1">{{ t.difficulty }}</span>
              <span class="badge bg-secondary">{{ t.duration_days }} days</span>
            </div>
            <p class="mb-2 small text-muted">{{ t.description }}</p>
            <p class="mb-1 small"><strong>Dates:</strong> {{ t.start_date }} → {{ t.end_date }}</p>
            <p class="mb-3"><strong>Slots left:</strong> {{ t.available_slots }}</p>
            <button class="btn btn-success btn-sm mt-auto" :disabled="t.available_slots <= 0" @click="book(t.id)">
              {{ t.available_slots > 0 ? 'Book Now' : 'Full' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import PageHeader from '../../components/PageHeader.vue'

export default {
  name: 'TrekkerTreks',
  components: { PageHeader },
  data() {
    return { treks: [], filters: { difficulty: '', location: '', duration: '' }, message: '' }
  },
  async mounted() {
    await this.load()
  },
  methods: {
    async load() {
      const params = {}
      if (this.filters.difficulty) params.difficulty = this.filters.difficulty
      if (this.filters.location) params.location = this.filters.location
      if (this.filters.duration) params.duration = this.filters.duration
      const res = await api.get('/trekker/treks', { params })
      this.treks = res.data.treks
    },
    clearFilters() {
      this.filters = { difficulty: '', location: '', duration: '' }
      this.load()
    },
    async book(trekId) {
      try {
        await api.post('/trekker/bookings', { trek_id: trekId })
        this.message = 'Booked successfully!'
        await this.load()
      } catch (err) {
        this.message = err.response?.data?.message || 'Booking failed'
      }
    },
  },
}
</script>
