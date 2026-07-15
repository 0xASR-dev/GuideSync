<template>
  <div>
    <router-link to="/staff" class="btn btn-link px-0 mb-2">&larr; Back to my treks</router-link>
    <PageHeader :title="trekName || 'Manage Trek'" subtitle="Update slots, status and view participants" />

    <div v-if="message" class="alert alert-info py-2">{{ message }}</div>

    <div class="row g-3 mb-4">
      <div class="col-md-6">
        <div class="card h-100"><div class="card-body">
          <h5 class="section-title">Update Available Slots</h5>
          <div class="input-group" style="max-width: 320px">
            <input v-model.number="slots" type="number" min="0" class="form-control" />
            <button class="btn btn-success" @click="updateSlots">Save</button>
          </div>
        </div></div>
      </div>
      <div class="col-md-6">
        <div class="card h-100"><div class="card-body">
          <h5 class="section-title">Change Status</h5>
          <div class="d-flex flex-wrap gap-2">
            <button v-for="s in statuses" :key="s"
                    class="btn btn-outline-secondary btn-sm" @click="setStatus(s)">
              {{ s }}
            </button>
          </div>
        </div></div>
      </div>
    </div>

    <div class="d-flex justify-content-between align-items-center mb-2">
      <h5 class="section-title mb-0">Participants</h5>
      <span class="badge bg-primary">{{ participants.length }} total</span>
    </div>
    <div class="table-wrap">
      <table class="table table-hover align-middle">
        <thead>
          <tr><th>Name</th><th>Email</th><th>Phone</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in participants" :key="p.booking_id">
            <td class="fw-semibold">{{ p.name }}</td>
            <td>{{ p.email }}</td>
            <td>{{ p.phone }}</td>
            <td><StatusPill :status="p.status" /></td>
          </tr>
        </tbody>
      </table>
      <p v-if="participants.length === 0" class="empty-state mb-0">No participants yet.</p>
    </div>
  </div>
</template>

<script>
import api from '../../services/api'
import PageHeader from '../../components/PageHeader.vue'
import StatusPill from '../../components/StatusPill.vue'

export default {
  name: 'StaffTrek',
  components: { PageHeader, StatusPill },
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
