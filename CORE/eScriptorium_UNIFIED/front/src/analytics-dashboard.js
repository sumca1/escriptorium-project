/**
 * Analytics Dashboard - Model Training Analytics
 * Created: 21 אוקטובר 2025
 * 
 * דשבורד ניתוח מתקדם למודלי OCR:
 * - גרפים של accuracy per epoch
 * - Timeline של אימונים
 * - Data quality analysis
 * - Comparison בין models
 */

import Chart from 'chart.js/auto';

export default {
    name: 'AnalyticsDashboard',
    
    data() {
        return {
            selectedModelId: null,
            modelsList: [],
            currentModelData: null,
            trainingHistory: [],
            comparisonModels: [],
            charts: {
                accuracyChart: null,
                timelineChart: null,
                dataQualityChart: null
            },
            loading: false,
            error: null,
            autoRefresh: false,
            refreshInterval: null
        };
    },
    
    mounted() {
        this.loadModels();
        this.setupEventListeners();
    },
    
    beforeUnmount() {
        this.destroyCharts();
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
    },
    
    methods: {
        async loadModels() {
            try {
                this.loading = true;
                const response = await fetch('/api/models/');
                const data = await response.json();
                this.modelsList = data.results || data;
                this.loading = false;
            } catch (error) {
                console.error('Error loading models:', error);
                this.error = 'Failed to load models';
                this.loading = false;
            }
        },
        
        async loadModelAnalytics(modelId) {
            try {
                this.loading = true;
                this.selectedModelId = modelId;
                
                // טעינת נתוני המודל
                const statusResponse = await fetch(`/api/models/${modelId}/training-status/`);
                this.currentModelData = await statusResponse.json();
                
                // טעינת היסטוריית אימון (אם קיים endpoint)
                try {
                    const historyResponse = await fetch(`/api/models/${modelId}/training-history/`);
                    if (historyResponse.ok) {
                        this.trainingHistory = await historyResponse.json();
                    }
                } catch (e) {
                    console.log('Training history not available:', e);
                }
                
                // עדכון הגרפים
                this.updateCharts();
                
                this.loading = false;
            } catch (error) {
                console.error('Error loading model analytics:', error);
                this.error = `Failed to load analytics for model ${modelId}`;
                this.loading = false;
            }
        },
        
        updateCharts() {
            this.$nextTick(() => {
                this.createAccuracyChart();
                this.createTimelineChart();
                this.createDataQualityChart();
            });
        },
        
        createAccuracyChart() {
            const ctx = document.getElementById('accuracyChart');
            if (!ctx) return;
            
            // הרס גרף קודם אם קיים
            if (this.charts.accuracyChart) {
                this.charts.accuracyChart.destroy();
            }
            
            // נתונים לדוגמה - יש להחליף בנתונים אמיתיים מה-API
            const epochs = Array.from({length: this.currentModelData.current_epoch + 1}, (_, i) => i);
            const accuracyData = this.generateMockAccuracyData(epochs.length);
            
            this.charts.accuracyChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: epochs,
                    datasets: [
                        {
                            label: 'Validation Accuracy',
                            data: accuracyData,
                            borderColor: 'rgb(75, 192, 192)',
                            backgroundColor: 'rgba(75, 192, 192, 0.1)',
                            tension: 0.4,
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: `${this.currentModelData.model_name} - Training Progress`,
                            font: { size: 16 }
                        },
                        legend: {
                            display: true,
                            position: 'top'
                        },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: (context) => {
                                    return `Accuracy: ${(context.parsed.y * 100).toFixed(2)}%`;
                                }
                            }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 1.0,
                            ticks: {
                                callback: (value) => `${(value * 100).toFixed(0)}%`
                            },
                            title: {
                                display: true,
                                text: 'Accuracy'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Epoch'
                            }
                        }
                    },
                    interaction: {
                        mode: 'nearest',
                        axis: 'x',
                        intersect: false
                    }
                }
            });
        },
        
        createTimelineChart() {
            const ctx = document.getElementById('timelineChart');
            if (!ctx) return;
            
            if (this.charts.timelineChart) {
                this.charts.timelineChart.destroy();
            }
            
            // נתונים על משך כל epoch
            const epochs = Array.from({length: this.currentModelData.current_epoch + 1}, (_, i) => i);
            const durations = this.generateMockDurations(epochs.length);
            
            this.charts.timelineChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: epochs,
                    datasets: [{
                        label: 'Duration (minutes)',
                        data: durations,
                        backgroundColor: 'rgba(54, 162, 235, 0.6)',
                        borderColor: 'rgb(54, 162, 235)',
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Training Duration per Epoch',
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Minutes'
                            }
                        },
                        x: {
                            title: {
                                display: true,
                                text: 'Epoch'
                            }
                        }
                    }
                }
            });
        },
        
        createDataQualityChart() {
            const ctx = document.getElementById('dataQualityChart');
            if (!ctx) return;
            
            if (this.charts.dataQualityChart) {
                this.charts.dataQualityChart.destroy();
            }
            
            const stats = this.currentModelData.data_stats;
            
            this.charts.dataQualityChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Training Lines', 'Validation Lines'],
                    datasets: [{
                        data: [stats.training_lines, stats.validation_lines],
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.6)',
                            'rgba(54, 162, 235, 0.6)'
                        ],
                        borderColor: [
                            'rgb(255, 99, 132)',
                            'rgb(54, 162, 235)'
                        ],
                        borderWidth: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Data Split',
                            font: { size: 16 }
                        },
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        },
        
        generateMockAccuracyData(length) {
            // יצירת נתונים מדומים - להחלפה בנתונים אמיתיים
            // מדמה learning curve עם שיפור הדרגתי
            const data = [];
            const finalAccuracy = this.currentModelData.current_accuracy || 0.19;
            
            for (let i = 0; i < length; i++) {
                // מדמה עקומת למידה לוגיסטית
                const progress = i / length;
                const noise = (Math.random() - 0.5) * 0.05;
                const accuracy = finalAccuracy * (1 - Math.exp(-3 * progress)) + noise;
                data.push(Math.max(0, Math.min(1, accuracy)));
            }
            
            return data;
        },
        
        generateMockDurations(length) {
            // יצירת נתוני זמן מדומים - בממוצע 22 דקות per epoch
            return Array.from({length}, () => 18 + Math.random() * 8);
        },
        
        destroyCharts() {
            Object.values(this.charts).forEach(chart => {
                if (chart) chart.destroy();
            });
        },
        
        setupEventListeners() {
            // האזנה לאירועי WebSocket של training updates
            if (window.eventBus) {
                window.eventBus.$on('training:eval', this.handleTrainingUpdate);
                window.eventBus.$on('training:done', this.handleTrainingComplete);
            }
        },
        
        handleTrainingUpdate(data) {
            if (data.model_id === this.selectedModelId) {
                // עדכון הגרפים עם נתונים חדשים
                this.loadModelAnalytics(this.selectedModelId);
            }
        },
        
        handleTrainingComplete(data) {
            if (data.model_id === this.selectedModelId) {
                this.loadModelAnalytics(this.selectedModelId);
            }
        },
        
        toggleAutoRefresh() {
            this.autoRefresh = !this.autoRefresh;
            
            if (this.autoRefresh) {
                this.refreshInterval = setInterval(() => {
                    if (this.selectedModelId) {
                        this.loadModelAnalytics(this.selectedModelId);
                    }
                }, 30000); // רענון כל 30 שניות
            } else {
                if (this.refreshInterval) {
                    clearInterval(this.refreshInterval);
                    this.refreshInterval = null;
                }
            }
        },
        
        exportData() {
            // ייצוא נתוני הדשבורד ל-JSON
            const exportData = {
                model: this.currentModelData,
                history: this.trainingHistory,
                timestamp: new Date().toISOString()
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `model_${this.selectedModelId}_analytics_${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
        }
    },
    
    template: `
        <div class="analytics-dashboard">
            <div class="dashboard-header">
                <h2><i class="fas fa-chart-line"></i> Analytics Dashboard</h2>
                <div class="dashboard-controls">
                    <select v-model="selectedModelId" @change="loadModelAnalytics(selectedModelId)" class="form-control">
                        <option :value="null">Select a model...</option>
                        <option v-for="model in modelsList" :key="model.id" :value="model.id">
                            {{ model.name }} ({{ model.job === 2 ? 'Segmentation' : 'Recognition' }})
                        </option>
                    </select>
                    
                    <button @click="toggleAutoRefresh" class="btn btn-sm" :class="autoRefresh ? 'btn-success' : 'btn-secondary'">
                        <i class="fas" :class="autoRefresh ? 'fa-pause' : 'fa-sync'"></i>
                        {{ autoRefresh ? 'Auto-refresh ON' : 'Auto-refresh OFF' }}
                    </button>
                    
                    <button @click="exportData" class="btn btn-sm btn-primary" :disabled="!currentModelData">
                        <i class="fas fa-download"></i> Export
                    </button>
                </div>
            </div>
            
            <div v-if="loading" class="loading-indicator">
                <i class="fas fa-spinner fa-spin"></i> Loading analytics...
            </div>
            
            <div v-if="error" class="alert alert-danger">
                {{ error }}
            </div>
            
            <div v-if="currentModelData && !loading" class="dashboard-content">
                <!-- Model Info Card -->
                <div class="info-card">
                    <h3>{{ currentModelData.model_name }}</h3>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">Type:</span>
                            <span class="value">{{ currentModelData.model_type }}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Status:</span>
                            <span class="value" :class="currentModelData.training ? 'text-success' : 'text-muted'">
                                {{ currentModelData.training ? 'Training' : 'Completed' }}
                            </span>
                        </div>
                        <div class="info-item">
                            <span class="label">Current Epoch:</span>
                            <span class="value">{{ currentModelData.current_epoch }}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Best Accuracy:</span>
                            <span class="value" :class="currentModelData.current_accuracy > 0.9 ? 'text-success' : currentModelData.current_accuracy > 0.5 ? 'text-warning' : 'text-danger'">
                                {{ (currentModelData.current_accuracy * 100).toFixed(2) }}%
                            </span>
                        </div>
                        <div class="info-item">
                            <span class="label">File Size:</span>
                            <span class="value">{{ currentModelData.file_size_mb }} MB</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Duration:</span>
                            <span class="value">{{ currentModelData.training_duration_human || 'N/A' }}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Data Stats Card -->
                <div class="info-card">
                    <h4>Data Statistics</h4>
                    <div class="info-grid">
                        <div class="info-item">
                            <span class="label">Total Lines:</span>
                            <span class="value">{{ currentModelData.data_stats.total_lines }}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Training Lines:</span>
                            <span class="value">{{ currentModelData.data_stats.training_lines }}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Validation Lines:</span>
                            <span class="value">{{ currentModelData.data_stats.validation_lines }}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Documents:</span>
                            <span class="value">{{ currentModelData.data_stats.documents_count }}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Parts:</span>
                            <span class="value">{{ currentModelData.data_stats.parts_count }}</span>
                        </div>
                        <div class="info-item">
                            <span class="label">Avg Lines/Part:</span>
                            <span class="value">{{ currentModelData.data_stats.avg_lines_per_part }}</span>
                        </div>
                    </div>
                </div>
                
                <!-- Charts Grid -->
                <div class="charts-grid">
                    <div class="chart-container">
                        <canvas id="accuracyChart"></canvas>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="timelineChart"></canvas>
                    </div>
                    
                    <div class="chart-container">
                        <canvas id="dataQualityChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    `
};
