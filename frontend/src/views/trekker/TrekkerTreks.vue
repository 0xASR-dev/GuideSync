<template>
  <div>
    <h2 class="mb-4">Browse Treks</h2>
    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <!-- Filters -->
    <div class="row g-2 mb-4">
      <div class="col-md-3">
        <select v-model="filters.difficulty" class="form-select">
          <option value="">Any difficulty</option>
          <option>Easy</option><option>Moderate</option><option>Hard</option>
        </select>
      </div>
      <div class="col-md-3">
        <input v-model="filters.location" class="form-control" placeholder="Location" />
      </div>
      <div class="col-md-3">
        <input v-model.number="filters.duration" type="number" min="1" class="form-control" placeholder="Days" />
      </div>
      <div class="col-md-3">
        <button class="btn btn-success me-2" @click="load">Search</button>
        <button class="btn btn-outline-secondary" @click="clearFilters">Clear</button>
      </div>
    </div>

    <!-- Trek cards -->
    <div class="row g-3">
      <div class="col-md-4" v-for="t in treks" :key="t.id">
        <div class="card h-100">
          <div class="card-body">
            <h5>{{ t.name }}</h5>
            <p class="mb-1 text-muted">{{ t.location }}</p>
            <span class="badge bg-info">{{ t.difficulty }}</span>
            <span class="badge bg-secondary">{{ t.duration_days }} days</span>
            <p class="mt-2 mb-1">{{ t.description }}</p>
            <p class="mb-1"><strong>₹{{ t.price }}</strong></p>
            <p class="mb-1">Dates: {{ t.start_date }} → {{ t.end_date }}</p>
            <p class="mb-2">Slots left: {{ t.available_slots }}</p>
            <button class="btn btn-success btn-sm" :disabled="t.available_slots <= 0" @click="book(t.id)">
              {{ t.available_slots > 0 ? 'Book Now' : 'Full' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <p v-if="treks.length === 0" class="text-muted">No treks found.</p>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'TrekkerTreks',
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
