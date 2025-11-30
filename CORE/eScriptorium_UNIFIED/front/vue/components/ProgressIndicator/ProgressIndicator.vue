<template>
    <transition name="escr-progress-slide">
        <div v-if="active" class="escr-progress-indicator" :class="{ 'canceling': canceling }">
            <!-- Header -->
            <div class="escr-progress-header">
                <div class="escr-progress-title">
                    <span class="escr-progress-icon">⚙️</span>
                    {{ title }}
                </div>
                <button 
                    v-if="!canceling" 
                    @click="$emit('cancel')" 
                    class="escr-progress-cancel-btn"
                    :aria-label="translate('Cancel')"
                >
                    ✖
                </button>
            </div>
            
            <!-- Progress Bar -->
            <div class="escr-progress-bar-container">
                <div class="escr-progress-bar">
                    <div 
                        class="escr-progress-bar-fill" 
                        :style="{ width: percent + '%' }"
                    ></div>
                </div>
                <div class="escr-progress-percentage">{{ percent }}%</div>
            </div>
            
            <!-- Stats -->
            <div class="escr-progress-stats">
                <div class="escr-progress-stat">
                    <span class="escr-progress-stat-label">{{ translate('Processed') }}:</span>
                    <span class="escr-progress-stat-value">{{ processed.toLocaleString() }} / {{ total.toLocaleString() }}</span>
                </div>
                
                <div v-if="errors > 0" class="escr-progress-stat escr-progress-stat-error">
                    <span class="escr-progress-stat-label">{{ translate('Errors') }}:</span>
                    <span class="escr-progress-stat-value">{{ errors }}</span>
                </div>
                
                <div v-if="speed" class="escr-progress-stat">
                    <span class="escr-progress-stat-label">{{ translate('Speed') }}:</span>
                    <span class="escr-progress-stat-value">{{ speed.toLocaleString() }} {{ translate('lines/sec') }}</span>
                </div>
            </div>
            
            <!-- Time -->
            <div class="escr-progress-time">
                <div class="escr-progress-time-item">
                    <span class="escr-progress-time-label">⏱️ {{ translate('Elapsed') }}:</span>
                    <span class="escr-progress-time-value">{{ formatTime(elapsedTime) }}</span>
                </div>
                
                <div v-if="estimatedRemaining > 0" class="escr-progress-time-item">
                    <span class="escr-progress-time-label">⏳ {{ translate('Remaining') }}:</span>
                    <span class="escr-progress-time-value">{{ formatTime(estimatedRemaining) }}</span>
                </div>
            </div>
            
            <!-- Canceling State -->
            <div v-if="canceling" class="escr-progress-canceling">
                <span class="escr-progress-spinner"></span>
                {{ translate('Canceling') }}...
            </div>
        </div>
    </transition>
</template>

<script>
import "./ProgressIndicator.css";

export default {
    name: "EscrProgressIndicator",
    props: {
        active: {
            type: Boolean,
            default: false
        },
        title: {
            type: String,
            default: "Processing"
        },
        total: {
            type: Number,
            default: 0
        },
        processed: {
            type: Number,
            default: 0
        },
        errors: {
            type: Number,
            default: 0
        },
        elapsedTime: {
            type: Number,
            default: 0
        },
        estimatedRemaining: {
            type: Number,
            default: 0
        },
        speed: {
            type: Number,
            default: 0
        },
        canceling: {
            type: Boolean,
            default: false
        }
    },
    emits: ['cancel'],
    computed: {
        percent() {
            if (this.total === 0) return 0;
            return Math.min(Math.round((this.processed / this.total) * 100), 100);
        }
    },
    methods: {
        formatTime(seconds) {
            if (seconds === 0) return "00:00";
            const mins = Math.floor(seconds / 60);
            const secs = Math.floor(seconds % 60);
            return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
        },
        
        translate(key) {
            // Integration with i18n
            return this.$t ? this.$t(key) : key;
        }
    }
}
</script>
