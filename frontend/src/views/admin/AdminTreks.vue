<template>
  <div>
    <h2 class="mb-4">Manage Treks</h2>

    <div v-if="message" class="alert alert-info">{{ message }}</div>

    <!-- Create / Edit form -->
    <div class="card mb-4">
      <div class="card-body">
        <h5>{{ editingId ? 'Edit Trek' : 'Add New Trek' }}</h5>
        <form @submit.prevent="save" class="row g-2">
          <div class="col-md-4">
            <input v-model="form.name" class="form-control" placeholder="Name" required />
          </div>
          <div class="col-md-4">
            <input v-model="form.location" class="form-control" placeholder="Location" required />
          </div>
          <div class="col-md-4">
            <select v-model="form.difficulty" class="form-select">
              <option>Easy</option><option>Moderate</option><option>Hard</option>
            </select>
          </div>
          <div class="col-md-3">
            <input v-model.number="form.duration_days" type="number" min="1" class="form-control" placeholder="Days" />
          </div>
          <div class="col-md-3">
            <input v-model.number="form.total_slots" type="number" min="0" class="form-control" placeholder="Total slots" />
          </div>
          <div class="col-md-3">
            <input v-model.number="form.price" type="number" min="0" class="form-control" placeholder="Price" />
          </div>
          <div class="col-md-3">
            <input v-model="form.start_date" type="date" class="form-control" />
          </div>
          <div class="col-md-6">
            <input v-model="form.end_date" type="date" class="form-control" placeholder="End date" />
          </div>
          <div class="col-md-6">
            <input v-model="form.description" class="form-control" placeholder="Description" />
          </div>
          <div class="col-12">
            <button class="btn btn-success" type="submit">{{ editingId ? 'Update' : 'Create' }}</button>
            <button v-if="editingId" class="btn btn-secondary ms-2" type="button" @click="resetForm">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Trek list -->
    <table class="table table-bordered bg-white">
      <thead class="table-light">
        <tr>
          <th>Name</th><th>Location</th><th>Difficulty</th><th>Slots</th>
          <th>Status</th><th>Staff</th><th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="t in treks" :key="t.id">
          <td>{{ t.name }}</td>
          <td>{{ t.location }}</td>
          <td>{{ t.difficulty }}</td>
          <td>{{ t.available_slots }}/{{ t.total_slots }}</td>
          <td><span class="badge bg-secondary">{{ t.status }}</span></td>
          <td>
            <span v-if="t.assigned_staff">{{ t.assigned_staff }}</span>
            <select v-else class="form-select form-select-sm" @change="assign(t.id, $event.target.value)">
              <option value="">Assign staff...</option>
              <option v-for="s in staff" :key="s.id" :value="s.id">{{ s.full_name }}</option>
            </select>
          </td>
          <td>
            <button class="btn btn-sm btn-outline-primary" @click="edit(t)">Edit</button>
            <button class="btn btn-sm btn-outline-danger ms-1" @click="remove(t.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
import api from '../../services/api'

const emptyForm = () => ({
  name: '', location: '', difficulty: 'Easy', duration_days: 1,
  total_slots: 0, price: 0, start_date: '', end_date: '', description: '',
})

export default {
  name: 'AdminTreks',
  data() {
    return { treks: [], staff: [], form: emptyForm(), editingId: null, message: '' }
  },
  async mounted() {
    await this.load()
    const s = await api.get('/admin/staff')
    this.staff = s.data.staff
  },
  methods: {
    async load() {
      const res = await api.get('/admin/treks')
      this.treks = res.data.treks
    },
    resetForm() {
      this.form = emptyForm()
      this.editingId = null
    },
    async save() {
      if (this.editingId) {
        await api.put(`/admin/treks/${this.editingId}`, this.form)
        this.message = 'Trek updated'
      } else {
        await api.post('/admin/treks', this.form)
        this.message = 'Trek created'
      }
      this.resetForm()
      await this.load()
    },
    edit(t) {
      this.editingId = t.id
      this.form = {
        name: t.name, location: t.location, difficulty: t.difficulty,
        duration_days: t.duration_days, total_slots: t.total_slots, price: t.price,
        start_date: t.start_date, end_date: t.end_date, description: t.description || '',
      }
    },
    async remove(id) {
      if (!confirm('Delete this trek?')) return
      await api.delete(`/admin/treks/${id}`)
      this.message = 'Trek deleted'
      await this.load()
    },
    async assign(trekId, staffId) {
      if (!staffId) return
      await api.post(`/admin/treks/${trekId}/assign-staff`, { staff_user_id: Number(staffId) })
      this.message = 'Staff assigned'
      await this.load()
    },
  },
}
</script>
