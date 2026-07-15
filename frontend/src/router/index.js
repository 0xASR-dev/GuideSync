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

// Where each role lands when logged in.
export function roleHome(role) {
  if (role === 'admin') return '/admin'
  if (role === 'staff') return '/staff'
  return '/trekker'
}

router.beforeEach((to) => {
  const auth = useAuthStore()

  // A logged-in user should never see the public landing / login / register
  // pages — send them to their own dashboard instead.
  if (auth.isLoggedIn && ['/', '/login', '/register'].includes(to.path)) {
    return roleHome(auth.role)
  }

  if (to.meta.public) return true
  if (!auth.isLoggedIn) return '/login'
  if (to.meta.role && auth.role !== to.meta.role) return roleHome(auth.role)
  return true
})

export default router
