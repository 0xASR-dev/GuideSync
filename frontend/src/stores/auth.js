import { defineStore } from 'pinia'
import api from '../services/api'


export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    role: localStorage.getItem('role') || '',
    fullName: localStorage.getItem('fullName') || '',
  }),

  getters: {
    isLoggedIn: (s) => !!s.token,
  },

  actions: {
    async login(email, password) {
      const res = await api.post('/auth/login', { email, password })
      this.token = res.data.access_token
      this.role = res.data.role
      this.fullName = res.data.full_name

      localStorage.setItem('token', this.token)
      localStorage.setItem('role', this.role)
      localStorage.setItem('fullName', this.fullName)
      return this.role
    },

    logout() {
      this.token = ''
      this.role = ''
      this.fullName = ''
      localStorage.clear()
    },
  },
})
