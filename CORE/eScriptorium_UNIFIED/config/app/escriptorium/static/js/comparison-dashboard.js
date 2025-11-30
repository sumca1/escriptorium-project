/**
 * BiblIA OCR Engine Comparison - Dashboard
 * Interactive dashboard for viewing and managing comparisons
 * Created: 22 October 2025
 */

class ComparisonDashboard {
    constructor() {
        this.statsData = null;
        this.init();
    }
    
    init() {
        console.log('📊 Initializing Comparison Dashboard');
        this.loadStats();
        this.setupEventListeners();
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/engine-comparison-stats/');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.statsData = await response.json();
            console.log('✅ Stats loaded:', this.statsData);
            
            this.displayStats();
            
        } catch (error) {
            console.error('❌ Error loading stats:', error);
            this.showError(`Failed to load statistics: ${error.message}`);
        }
    }
    
    displayStats() {
        if (!this.statsData) return;
        
        // Update stat cards
        this.updateStatCard('total-comparisons', this.statsData.total);
        this.updateStatCard('avg-accuracy', this.statsData.avg_accuracy.toFixed(1) + '%');
        this.updateStatCard('best-engine', this.statsData.best_engine);
        this.updateStatCard('documents-count', this.statsData.documents_with_comparisons);
        
        // Update engine wins
        if (document.getElementById('kraken-wins')) {
            document.getElementById('kraken-wins').textContent = this.statsData.kraken_wins;
        }
        if (document.getElementById('tesseract-wins')) {
            document.getElementById('tesseract-wins').textContent = this.statsData.tesseract_wins;
        }
        
        // Show/hide no-data message
        const noDataMessage = document.getElementById('no-data-message');
        const dataContent = document.getElementById('data-content');
        
        if (this.statsData.total === 0) {
            if (noDataMessage) noDataMessage.style.display = 'block';
            if (dataContent) dataContent.style.display = 'none';
        } else {
            if (noDataMessage) noDataMessage.style.display = 'none';
            if (dataContent) dataContent.style.display = 'block';
        }
    }
    
    updateStatCard(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            element.textContent = value;
            
            // Add animation
            element.classList.add('stat-updated');
            setTimeout(() => element.classList.remove('stat-updated'), 500);
        }
    }
    
    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-stats');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadStats();
                this.showNotification('🔄 Statistics refreshed', 'info');
            });
        }
        
        // View comparison buttons
        document.querySelectorAll('.view-comparison-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const trans1Id = e.target.dataset.trans1;
                const trans2Id = e.target.dataset.trans2;
                
                if (trans1Id && trans2Id) {
                    window.location.href = `/comparison/viewer/?trans1=${trans1Id}&trans2=${trans2Id}`;
                }
            });
        });
        
        // Batch comparison
        const batchBtn = document.getElementById('run-batch-comparison');
        if (batchBtn) {
            batchBtn.addEventListener('click', () => this.runBatchComparison());
        }
    }
    
    async runBatchComparison() {
        // Get selected documents
        const checkboxes = document.querySelectorAll('.document-checkbox:checked');
        const documentIds = Array.from(checkboxes).map(cb => cb.value);
        
        if (documentIds.length === 0) {
            this.showNotification('⚠️ Please select at least one document', 'warning');
            return;
        }
        
        try {
            this.showNotification('🔄 Running batch comparison...', 'info');
            
            const formData = new FormData();
            documentIds.forEach(id => formData.append('document_ids[]', id));
            
            const response = await fetch('/api/comparison/batch/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const result = await response.json();
            console.log('✅ Batch comparison complete:', result);
            
            this.displayBatchResults(result);
            this.showNotification(`✅ Compared ${result.count} documents`, 'success');
            
        } catch (error) {
            console.error('❌ Batch comparison error:', error);
            this.showNotification('❌ Batch comparison failed', 'error');
        }
    }
    
    displayBatchResults(result) {
        // Create results modal or panel
        const resultsHtml = `
            <div class="batch-results-modal">
                <h3>Batch Comparison Results</h3>
                <p>Compared ${result.count} documents</p>
                <table class="results-table">
                    <thead>
                        <tr>
                            <th>Document</th>
                            <th>CER</th>
                            <th>Accuracy</th>
                            <th>Winner</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${result.results.map(r => `
                            <tr>
                                <td>${r.document_name}</td>
                                <td>${r.cer.toFixed(1)}%</td>
                                <td>${r.accuracy.toFixed(1)}%</td>
                                <td>${r.winner}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        // Display results (you can customize this)
        console.log('Batch results ready for display');
    }
    
    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${this.getNotificationColor(type)};
            color: white;
            padding: 15px 25px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    getNotificationColor(type) {
        const colors = {
            'success': '#28a745',
            'error': '#dc3545',
            'warning': '#ffc107',
            'info': '#667eea'
        };
        return colors[type] || colors.info;
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.comparisonDashboard = new ComparisonDashboard();
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
    
    @keyframes statUpdate {
        0% { transform: scale(1); }
        50% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
    
    .stat-updated {
        animation: statUpdate 0.5s ease-out;
        color: #667eea !important;
    }
`;
document.head.appendChild(style);
