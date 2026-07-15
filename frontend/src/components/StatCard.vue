<template>
  <div class="stat-card" :class="variantClass">
    <p class="stat-label">{{ label }}</p>
    <div class="stat-value">{{ value }}</div>
    <p v-if="hint" class="stat-hint">{{ hint }}</p>
  </div>
</template>

<script>
export default {
  name: 'StatCard',
  props: {
    label: { type: String, required: true },
    value: { type: [Number, String], default: 0 },
    hint: { type: String, default: '' },
    variant: { type: String, default: 'green' }, 
  },
  computed: {
    variantClass() {
      return `g-${this.variant}`
    },
  },
}
</script>
