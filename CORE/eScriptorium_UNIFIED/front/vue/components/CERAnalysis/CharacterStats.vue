<template>
  <div class="character-stats">
    <!-- Search and Filter -->
    <div class="stats-toolbar mb-3">
      <div class="row align-items-center">
        <div class="col-md-6">
          <div class="input-group">
            <span class="input-group-text">
              <i class="fas fa-search"></i>
            </span>
            <input 
              v-model="searchChar" 
              type="text"
              class="form-control"
              :placeholder="translate('cer.searchCharacter')"
            >
          </div>
        </div>
        <div class="col-md-6 text-end">
          <div class="btn-group btn-group-sm" role="group">
            <button 
              @click="showProblematic = !showProblematic"
              :class="['btn', showProblematic ? 'btn-warning' : 'btn-outline-warning']"
            >
              <i class="fas fa-exclamation-triangle"></i>
              {{ translate('cer.problematicOnly') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Table -->
    <div class="table-responsive">
      <table class="table table-sm table-hover character-stats-table">
        <thead class="table-light">
          <tr>
            <th @click="sort('character')" class="sortable">
              {{ translate('cer.character') }}
              <i v-if="sortKey === 'character'" :class="sortIcon"></i>
            </th>
            <th @click="sort('count')" class="sortable text-center">
              {{ translate('cer.total') }}
              <i v-if="sortKey === 'count'" :class="sortIcon"></i>
            </th>
            <th @click="sort('correct')" class="sortable text-center">
              {{ translate('cer.correct') }}
              <i v-if="sortKey === 'correct'" :class="sortIcon"></i>
            </th>
            <th @click="sort('incorrect')" class="sortable text-center">
              {{ translate('cer.incorrect') }}
              <i v-if="sortKey === 'incorrect'" :class="sortIcon"></i>
            </th>
            <th @click="sort('correct_ratio')" class="sortable">
              {{ translate('cer.accuracy') }}
              <i v-if="sortKey === 'correct_ratio'" :class="sortIcon"></i>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr 
            v-for="stat in filteredStats" 
            :key="stat.character"
            :class="{ 'table-warning': stat.correct_ratio < 0.8 }"
          >
            <td class="char-display">
              <span class="character-badge">{{ stat.character }}</span>
              <small class="text-muted ms-2">
                U+{{ stat.character.charCodeAt(0).toString(16).toUpperCase().padStart(4, '0') }}
              </small>
            </td>
            <td class="text-center">
              <strong>{{ stat.count }}</strong>
            </td>
            <td class="text-center text-success">
              {{ stat.correct }}
            </td>
            <td class="text-center text-danger">
              {{ stat.incorrect }}
            </td>
            <td>
              <div class="progress-wrapper">
                <div class="progress">
                  <div 
                    class="progress-bar" 
                    :class="progressClass(stat.correct_ratio)"
                    :style="{ width: (stat.correct_ratio * 100) + '%' }"
                    role="progressbar"
                  >
                    {{ (stat.correct_ratio * 100).toFixed(1) }}%
                  </div>
                </div>
              </div>
            </td>
          </tr>
          <tr v-if="filteredStats.length === 0">
            <td colspan="5" class="text-center text-muted py-4">
              <i class="fas fa-search"></i>
              {{ translate('cer.noCharactersFound') }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Summary -->
    <div class="stats-summary mt-3">
      <small class="text-muted">
        <i class="fas fa-info-circle"></i>
        {{ translate('cer.showing') }} {{ filteredStats.length }} / {{ stats.length }} {{ translate('cer.characters') }}
        <span v-if="showProblematic" class="ms-2">
          ({{ translate('cer.problematicFilter') }}: &lt; 80% {{ translate('cer.accuracy') }})
        </span>
      </small>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CharacterStats',

  props: {
    stats: {
      type: Array,
      required: true,
      default: () => []
    }
  },

  data() {
    return {
      searchChar: '',
      sortKey: 'count',
      sortDesc: true,
      showProblematic: false
    }
  },

  computed: {
    filteredStats() {
      let filtered = this.stats

      // Filter by search
      if (this.searchChar) {
        filtered = filtered.filter(s => 
          s.character.includes(this.searchChar) ||
          s.character.charCodeAt(0).toString(16).toUpperCase().includes(this.searchChar.toUpperCase())
        )
      }

      // Filter problematic only
      if (this.showProblematic) {
        filtered = filtered.filter(s => s.correct_ratio < 0.8)
      }

      // Sort
      return filtered.sort((a, b) => {
        const mult = this.sortDesc ? -1 : 1
        let aVal = a[this.sortKey]
        let bVal = b[this.sortKey]

        // Special handling for character sorting
        if (this.sortKey === 'character') {
          aVal = a.character.charCodeAt(0)
          bVal = b.character.charCodeAt(0)
        }

        if (aVal < bVal) return -1 * mult
        if (aVal > bVal) return 1 * mult
        return 0
      })
    },

    sortIcon() {
      return this.sortDesc ? 'fas fa-sort-down' : 'fas fa-sort-up'
    }
  },

  methods: {
    sort(key) {
      if (this.sortKey === key) {
        this.sortDesc = !this.sortDesc
      } else {
        this.sortKey = key
        this.sortDesc = true
      }
    },

    progressClass(ratio) {
      if (ratio > 0.95) return 'bg-success'
      if (ratio > 0.85) return 'bg-warning'
      return 'bg-danger'
    }
  }
}
</script>

<style scoped>
.character-stats {
  padding: 1rem;
}

.stats-toolbar {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.character-stats-table {
  font-size: 0.95rem;
}

.character-stats-table thead th {
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background-color: #e9ecef;
}

.char-display {
  font-size: 1.1rem;
}

.character-badge {
  display: inline-block;
  min-width: 2rem;
  text-align: center;
  font-size: 1.3rem;
  font-weight: bold;
  padding: 0.25rem 0.5rem;
  background: #e9ecef;
  border-radius: 4px;
}

.progress-wrapper {
  min-width: 150px;
}

.progress {
  height: 25px;
  font-size: 0.85rem;
  font-weight: 600;
}

.table-warning {
  background-color: #fff3cd !important;
}

.table-warning:hover {
  background-color: #ffe69c !important;
}

.stats-summary {
  background: #f8f9fa;
  padding: 0.75rem 1rem;
  border-radius: 4px;
}
</style>
