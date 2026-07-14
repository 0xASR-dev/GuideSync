import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import Home from '../views/Home.vue'
import Login from '../views/auth/Login.vue'
import Register from '../views/auth/Register.vue'

import AdminDashboard from '../views/admin/AdminDashboard.vue'
import AdminTreks from '../views/admin/AdminTreks.vue'
import AdminStaff from '../views/admin/AdminStaff.vue'
import AdminUsers from '../views/admin/AdminUsers.vue'
import AdminBookings from '../views/admin/AdminBookings.vue'
import AdminReports from '../views/admin/AdminReports.vue'

import StaffDashboard from '../views/staff/StaffDashboard.vue'
import StaffTrek from '../views/staff/StaffTrek.vue'

import TrekkerDashboard from '../views/trekker/TrekkerDashboard.vue'
import TrekkerTreks from '../views/trekker/TrekkerTreks.vue'
import TrekkerBookings from '../views/trekker/TrekkerBookings.vue'
import TrekkerProfile from '../views/trekker/TrekkerProfile.vue'

const routes = [
  { path: '/', component: Home, meta: { public: true } },
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/register', component: Register, meta: { public: true } },

  // Admin
  { path: '/admin', component: AdminDashboard, meta: { role: 'admin' } },
  { path: '/admin/treks', component: AdminTreks, meta: { role: 'admin' } },
  { path: '/admin/staff', component: AdminStaff, meta: { role: 'admin' } },
  { path: '/admin/users', component: AdminUsers, meta: { role: 'admin' } },
  { path: '/admin/bookings', component: AdminBookings, meta: { role: 'admin' } },
  { path: '/admin/reports', component: AdminReports, meta: { role: 'admin' } },

  // Staff
  { path: '/staff', component: StaffDashboard, meta: { role: 'staff' } },
  { path: '/staff/treks/:id', component: StaffTrek, meta: { role: 'staff' } },

  // Trekker
  { path: '/trekker', component: TrekkerDashboard, meta: { role: 'trekker' } },
  { path: '/trekker/treks', component: TrekkerTreks, meta: { role: 'trekker' } },
  { path: '/trekker/bookings', component: TrekkerBookings, meta: { role: 'trekker' } },
  { path: '/trekker/profile', component: TrekkerProfile, meta: { role: 'trekker' } },

  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Route guard: check login + role before entering a page.
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.public) return true
  if (!auth.isLoggedIn) return '/login'
  if (to.meta.role && auth.role !== to.meta.role) return '/'
  return true
})

export default router
