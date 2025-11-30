<template>
    <div class="segmonto-panel">
        <!-- Trigger Button -->
        <button 
            class="btn btn-outline-primary segmonto-trigger"
            @click="togglePanel"
            :title="translate('Check SegmOnto Compliance')"
        >
            <i class="fas fa-check-circle"></i>
            <span class="d-none d-md-inline">SegmOnto</span>
            <span v-if="lastResults && lastResults.overall" 
                  :class="['badge', 'ms-2', `bg-${getBadgeClass(lastResults.overall.percentage)}`]">
                {{ lastResults.overall.percentage }}%
            </span>
        </button>

        <!-- Results Panel (Collapsible) -->
        <div v-if="showPanel" class="segmonto-results-panel card mt-2">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5 class="mb-0">
                    <i class="fas fa-check-circle text-primary"></i>
                    {{ translate('SegmOnto Compliance Check') }}
                </h5>
                <button class="btn btn-sm btn-outline-secondary" @click="togglePanel">
                    <i class="fas fa-times"></i>
                </button>
            </div>

            <div class="card-body">
                <!-- Loading State -->
                <div v-if="isChecking" class="text-center py-4">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">{{ translate('Checking...') }}</span>
                    </div>
                    <p class="mt-2">{{ translate('Analyzing document...') }}</p>
                </div>

                <!-- Results -->
                <div v-else-if="lastResults">
                    <!-- Overall Status -->
                    <div :class="['alert', `alert-${getAlertClass(lastResults.overall.percentage)}`]">
                        <strong>{{ translate('Overall Status') }}:</strong>
                        {{ lastResults.overall.totalValid }} / {{ lastResults.overall.totalItems }} 
                        {{ translate('items valid') }} ({{ lastResults.overall.percentage }}%)
                    </div>

                    <!-- Regions Section -->
                    <div class="segmonto-section mb-3">
                        <h6>
                            <i class="fas fa-vector-square"></i>
                            {{ translate('Regions') }}
                            <span :class="['badge', `bg-${lastResults.regions.badgeClass}`]">
                                {{ lastResults.regions.valid }} / {{ lastResults.regions.total }}
                            </span>
                        </h6>
                        
                        <div v-if="lastResults.regions.errors.length === 0" class="text-success">
                            <i class="fas fa-check"></i> {{ translate('All regions are valid!') }}
                        </div>
                        
                        <ul v-else class="segmonto-errors list-unstyled">
                            <li v-for="(error, idx) in lastResults.regions.errors" 
                                :key="`region-${idx}`"
                                :class="['error-item', error.severity === 'error' ? 'text-danger' : 'text-warning']">
                                <i :class="error.severity === 'error' ? 'fas fa-times-circle' : 'fas fa-exclamation-triangle'"></i>
                                <strong>{{ translate('Region') }} {{ error.id }}:</strong>
                                {{ error.error }}
                                <span v-if="error.typology" class="badge bg-secondary ms-1">{{ error.typology }}</span>
                            </li>
                        </ul>
                    </div>

                    <!-- Lines Section -->
                    <div class="segmonto-section">
                        <h6>
                            <i class="fas fa-align-left"></i>
                            {{ translate('Lines') }}
                            <span :class="['badge', `bg-${lastResults.lines.badgeClass}`]">
                                {{ lastResults.lines.valid }} / {{ lastResults.lines.total }}
                            </span>
                        </h6>
                        
                        <div v-if="lastResults.lines.errors.length === 0" class="text-success">
                            <i class="fas fa-check"></i> {{ translate('All lines are valid!') }}
                        </div>
                        
                        <ul v-else class="segmonto-errors list-unstyled" style="max-height: 300px; overflow-y: auto;">
                            <li v-for="(error, idx) in lastResults.lines.errors" 
                                :key="`line-${idx}`"
                                :class="['error-item', error.severity === 'error' ? 'text-danger' : 'text-warning']">
                                <i :class="error.severity === 'error' ? 'fas fa-times-circle' : 'fas fa-exclamation-triangle'"></i>
                                <strong>{{ translate('Line') }} {{ error.id }}</strong>
                                <span v-if="error.order !== undefined" class="text-muted">({{ translate('Order') }} {{ error.order + 1 }})</span>:
                                {{ error.error }}
                                <span v-if="error.typology" class="badge bg-secondary ms-1">{{ error.typology }}</span>
                            </li>
                        </ul>
                    </div>

                    <!-- Actions -->
                    <div class="segmonto-actions mt-3 border-top pt-3">
                        <button class="btn btn-sm btn-primary" @click="runCheck">
                            <i class="fas fa-sync-alt"></i> {{ translate('Re-check') }}
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" @click="exportResults">
                            <i class="fas fa-download"></i> {{ translate('Export') }}
                        </button>
                        <a 
                            href="https://segmonto.github.io/" 
                            target="_blank" 
                            class="btn btn-sm btn-outline-info"
                        >
                            <i class="fas fa-info-circle"></i> {{ translate('SegmOnto Docs') }}
                        </a>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-else class="text-center text-muted py-4">
                    <i class="fas fa-check-circle fa-3x mb-3"></i>
                    <p>{{ translate('Click "Check" to validate SegmOnto compliance') }}</p>
                    <button class="btn btn-primary" @click="runCheck">
                        <i class="fas fa-play"></i> {{ translate('Run Check') }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { segmontoChecker } from '../../src/segmonto-checker.js';

export default {
    name: 'SegmontoPanel',
    
    data() {
        return {
            showPanel: false,
            isChecking: false,
            lastResults: null,
            autoCheckEnabled: false
        };
    },

    mounted() {
        // Auto-check on load if enabled
        if (this.autoCheckEnabled) {
            this.runCheck();
        }

        // Listen to document changes and re-check if panel is open
        this.$store.subscribe((mutation) => {
            if (this.showPanel && this.autoCheckEnabled) {
                // Re-check on relevant mutations
                if (mutation.type.includes('region') || mutation.type.includes('line')) {
                    this.debouncedCheck();
                }
            }
        });
    },

    methods: {
        togglePanel() {
            this.showPanel = !this.showPanel;
            
            // Run check when opening panel if no results yet
            if (this.showPanel && !this.lastResults) {
                this.runCheck();
            }
        },

        async runCheck() {
            this.isChecking = true;
            
            try {
                // Small delay for visual feedback
                await new Promise(resolve => setTimeout(resolve, 300));
                
                // Run the check
                this.lastResults = segmontoChecker.checkDocument(this.$store);
                
                console.log('SegmOnto Check Results:', this.lastResults);
            } catch (error) {
                console.error('SegmOnto check failed:', error);
                alert(this.translate('Failed to run SegmOnto check. See console for details.'));
            } finally {
                this.isChecking = false;
            }
        },

        debouncedCheck() {
            // Debounce auto-checks to avoid too many
            clearTimeout(this._checkTimeout);
            this._checkTimeout = setTimeout(() => {
                this.runCheck();
            }, 1000);
        },

        getBadgeClass(percentage) {
            const perc = parseFloat(percentage);
            if (perc === 100) return 'success';
            if (perc >= 50) return 'warning';
            return 'danger';
        },

        getAlertClass(percentage) {
            const perc = parseFloat(percentage);
            if (perc === 100) return 'success';
            if (perc >= 75) return 'info';
            if (perc >= 50) return 'warning';
            return 'danger';
        },

        exportResults() {
            if (!this.lastResults) return;

            // Create CSV content
            const csv = this.generateCSV(this.lastResults);
            
            // Download
            const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `segmonto-check-${new Date().toISOString().split('T')[0]}.csv`;
            link.click();
        },

        generateCSV(results) {
            let csv = 'Type,ID,Order,Error,Typology,Severity\n';
            
            // Add region errors
            results.regions.errors.forEach(err => {
                csv += `Region,${err.id},,${err.error},"${err.typology || ''}",${err.severity}\n`;
            });
            
            // Add line errors
            results.lines.errors.forEach(err => {
                csv += `Line,${err.id},${err.order !== undefined ? err.order + 1 : ''},${err.error},"${err.typology || ''}",${err.severity}\n`;
            });
            
            return csv;
        },

        // Translation helper - renamed from $t to avoid conflict with Vue i18n
        translate(key) {
            // Simple translation function - use window.EDITOR_TRANSLATIONS if available
            if (window.EDITOR_TRANSLATIONS && window.EDITOR_TRANSLATIONS[key]) {
                return window.EDITOR_TRANSLATIONS[key];
            }
            return key;
        }
    }
};
</script>

<style scoped>
.segmonto-panel {
    position: relative;
}

.segmonto-trigger {
    white-space: nowrap;
}

.segmonto-results-panel {
    position: absolute;
    right: 0;
    top: 100%;
    width: 500px;
    max-width: 90vw;
    max-height: 80vh;
    overflow-y: auto;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.segmonto-section {
    padding: 0.75rem;
    background: #f8f9fa;
    border-radius: 0.25rem;
}

.segmonto-section h6 {
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.segmonto-errors {
    margin: 0;
    padding: 0;
}

.segmonto-errors .error-item {
    padding: 0.5rem;
    margin-bottom: 0.5rem;
    background: white;
    border-left: 3px solid;
    border-radius: 0.25rem;
    font-size: 0.9rem;
}

.segmonto-errors .error-item.text-danger {
    border-color: #dc3545;
}

.segmonto-errors .error-item.text-warning {
    border-color: #ffc107;
}

.segmonto-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

@media (max-width: 768px) {
    .segmonto-results-panel {
        width: 100%;
        max-width: 100%;
    }
}
</style>
