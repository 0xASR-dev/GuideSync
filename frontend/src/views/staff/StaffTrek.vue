<template>
  <div>
    <router-link to="/staff" class="btn btn-link px-0">&larr; Back</router-link>
    <h2 class="mb-3">Manage: {{ trekName }}</h2>
    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <div class="card mb-4">
      <div class="card-body">
        <h5>Update Slots</h5>
        <div class="input-group" style="max-width: 300px">
          <input v-model.number="slots" type="number" min="0" class="form-control" />
          <button class="btn btn-success" @click="updateSlots">Save</button>
        </div>
      </div>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <h5>Change Status</h5>
        <button v-for="s in statuses" :key="s"
                class="btn btn-outline-secondary me-2 mb-2" @click="setStatus(s)">
          {{ s }}
        </button>
      </div>
    </div>

    <div class="card">
      <div class="card-body">
        <h5>Participants</h5>
        <table class="table table-sm">
          <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="p in participants" :key="p.booking_id">
              <td>{{ p.name }}</td><td>{{ p.email }}</td><td>{{ p.phone }}</td><td>{{ p.status }}</td>
            </tr>
          </tbody>
        </table>
        <p v-if="participants.length === 0" class="text-muted">No participants yet.</p>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'

export default {
  name: 'StaffTrek',
  data() {
    return {
      trekId: this.$route.params.id,
      trekName: '',
      slots: 0,
      participants: [],
      statuses: ['Open', 'Closed', 'Started', 'Completed'],
      message: '',
    }
  },
  async mounted() {
    await this.loadParticipants()
  },
  methods: {
    async loadParticipants() {
      const res = await api.get(`/tstaff/treks/${this.trekId}/participants`)
      this.trekName = res.data.trek
      this.participants = res.data.participants
    },
    async updateSlots() {
      try {
        await api.patch(`/tstaff/treks/${this.trekId}/slots`, { available_slots: this.slots })
        this.message = 'Slots updated'
      } catch (err) {
        this.message = err.response?.data?.message || 'Error'
      }
    },
    async setStatus(status) {
      await api.patch(`/tstaff/treks/${this.trekId}/status`, { status })
      this.message = `Trek marked ${status}`
      await this.loadParticipants()
    },
  },
}
</script>
