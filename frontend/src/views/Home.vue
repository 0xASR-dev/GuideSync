<template>
  <div class="text-center py-5">
    <h1 class="display-4 fw-bold text-success">🏔️ GuideSync</h1>
    <p class="lead">A simple trekking management platform.</p>
    <p class="text-muted">Browse open treks, book your slot, and track your adventures.</p>
    <div class="mt-4">
      <router-link to="/login" class="btn btn-success me-2">Login</router-link>
      <router-link to="/register" class="btn btn-outline-success">Register as Trekker</router-link>
    </div>
  </div>
</template>

<script>
export default { name: 'Home' }
</script>
