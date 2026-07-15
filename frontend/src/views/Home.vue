<template>
  <div class="home-hero text-center">
    <span class="badge bg-success-subtle text-success mb-3 px-3 py-2">Trekking Management Platform</span>
    <h1 class="display-4 fw-bold">Plan, book, and lead treks with <span class="text-success">GuideSync</span></h1>
    <p class="lead text-muted mt-3">
      Browse open treks, reserve your slot, and track every adventure — all in one place.
    </p>
    <div class="mt-4">
      <router-link to="/login" class="btn btn-success btn-lg me-2 px-4">Login</router-link>
      <router-link to="/register" class="btn btn-outline-success btn-lg px-4">Register as Trekker</router-link>
    </div>

    <div class="row g-3 mt-5 text-start justify-content-center">
      <div class="col-md-4">
        <div class="card hoverable h-100"><div class="card-body">
          <h5 class="section-title">Discover</h5>
          <p class="text-muted mb-0">Filter open treks by difficulty, location and duration.</p>
        </div></div>
      </div>
      <div class="col-md-4">
        <div class="card hoverable h-100"><div class="card-body">
          <h5 class="section-title">Book</h5>
          <p class="text-muted mb-0">Reserve a slot instantly — no overbooking, no duplicates.</p>
        </div></div>
      </div>
      <div class="col-md-4">
        <div class="card hoverable h-100"><div class="card-body">
          <h5 class="section-title">Track</h5>
          <p class="text-muted mb-0">Follow trek status and export your full history anytime.</p>
        </div></div>
      </div>
    </div>
  </div>
</template>

<script>
export default { name: 'Home' }
</script>

<style scoped>
.home-hero {
  padding: 3.5rem 1rem 2rem;
  max-width: 960px;
  margin: 0 auto;
}
</style>
