<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-success">
    <div class="container">
      <router-link class="navbar-brand fw-bold" to="/">🏔️ GuideSync</router-link>

      <div class="navbar-nav ms-auto">
        <!-- Not logged in -->
        <template v-if="!auth.isLoggedIn">
          <router-link class="nav-link" to="/login">Login</router-link>
          <router-link class="nav-link" to="/register">Register</router-link>
        </template>

        <!-- Admin links -->
        <template v-if="auth.role === 'admin'">
          <router-link class="nav-link" to="/admin">Dashboard</router-link>
          <router-link class="nav-link" to="/admin/treks">Treks</router-link>
          <router-link class="nav-link" to="/admin/staff">Staff</router-link>
          <router-link class="nav-link" to="/admin/users">Users</router-link>
          <router-link class="nav-link" to="/admin/bookings">Bookings</router-link>
          <router-link class="nav-link" to="/admin/reports">Reports</router-link>
        </template>

        <!-- Staff links -->
        <template v-if="auth.role === 'staff'">
          <router-link class="nav-link" to="/staff">My Treks</router-link>
        </template>

        <!-- Trekker links -->
        <template v-if="auth.role === 'trekker'">
          <router-link class="nav-link" to="/trekker">Dashboard</router-link>
          <router-link class="nav-link" to="/trekker/treks">Browse Treks</router-link>
          <router-link class="nav-link" to="/trekker/bookings">My Bookings</router-link>
          <router-link class="nav-link" to="/trekker/profile">Profile</router-link>
        </template>

        <!-- Logout -->
        <a v-if="auth.isLoggedIn" class="nav-link" href="#" @click.prevent="logout">
          Logout ({{ auth.fullName }})
        </a>
      </div>
    </div>
  </nav>
</template>

<script>
import { useAuthStore } from '../stores/auth'

export default {
  name: 'NavBar',
  computed: {
    auth() {
      return useAuthStore()
    },
  },
  methods: {
    logout() {
      this.auth.logout()
      this.$router.push('/login')
    },
  },
}
</script>
