<template>
  <div class="stats-card" :style="{ borderTop: `4px solid ${color}` }">
    <div class="card-icon">{{ icon }}</div>
    <div class="card-content">
      <h3 class="card-title">{{ title }}</h3>
      <p class="card-value">{{ value }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CERStatsCard',
  props: {
    title: {
      type: String,
      required: true
    },
    value: {
      type: [String, Number],
      required: true
    },
    icon: {
      type: String,
      default: '📊'
    },
    color: {
      type: String,
      default: '#3498db'
    }
  }
}
</script>

<style scoped>
.stats-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 1.5rem;
  transition: transform 0.3s, box-shadow 0.3s;
}

.stats-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 2.5rem;
  text-align: center;
  min-width: 60px;
}

.card-content {
  flex: 1;
}

.card-title {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  margin: 0.5rem 0 0 0;
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
}

@media (max-width: 768px) {
  .stats-card {
    flex-direction: column;
    text-align: center;
    gap: 1rem;
  }
  
  .card-value {
    font-size: 1.5rem;
  }
}
</style>
