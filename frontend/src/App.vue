<template>
  <div>
    <NavBar />
    <div class="container py-4">
      <router-view />
    </div>
  </div>
</template>

<script>
import NavBar from './components/NavBar.vue'

export default {
  name: 'App',
  components: { NavBar },
}
</script>
