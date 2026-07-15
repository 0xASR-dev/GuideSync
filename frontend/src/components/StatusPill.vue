<template>
  <span class="badge" :class="pillClass">{{ status }}</span>
</template>

<script>
export default {
  name: 'StatusPill',
  props: {
    status: { type: String, default: '' },
  },
  computed: {
    pillClass() {
      const map = {
        // treks
        Open: 'bg-success',
        Approved: 'bg-info text-dark',
        Pending: 'bg-warning text-dark',
        Closed: 'bg-secondary',
        Started: 'bg-primary',
        Completed: 'bg-dark',
        // bookings
        Booked: 'bg-primary',
        Cancelled: 'bg-danger',
        // accounts
        Active: 'bg-success',
        Deactivated: 'bg-secondary',
        Blacklisted: 'bg-danger',
      }
      return map[this.status] || 'bg-secondary'
    },
  },
}
</script>
