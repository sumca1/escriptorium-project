/**
 * BiblIA OCR Engine Comparison - Interactive Viewer
 * Compares Kraken vs Tesseract OCR results
 * Created: 22 October 2025
 */

class ComparisonViewer {
    constructor() {
        this.comparisonData = null;
        this.trans1Id = null;
        this.trans2Id = null;
        this.charts = {};
        
        // Get IDs from URL
        const urlParams = new URLSearchParams(window.location.search);
        this.trans1Id = urlParams.get('trans1') || urlParams.get('transcription1');
        this.trans2Id = urlParams.get('trans2') || urlParams.get('transcription2');
        
        this.init();
    }
    
    init() {
        console.log('🔬 Initializing Comparison Viewer');
        
        if (!this.trans1Id || !this.trans2Id) {
            this.showError('Missing transcription IDs in URL parameters');
            return;
        }
        
        this.loadComparison();
    }
    
    async loadComparison() {
        try {
            this.showLoading(true);
            
            const response = await fetch(`/api/comparison/${this.trans1Id}/${this.trans2Id}/`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            this.comparisonData = await response.json();
            console.log('✅ Comparison data loaded:', this.comparisonData);
            
            this.displayComparison();
            
        } catch (error) {
            console.error('❌ Error loading comparison:', error);
            this.showError(`Error loading comparison: ${error.message}`);
        }
    }
    
    displayComparison() {
        this.showLoading(false);
        
        // Update metrics
        this.updateMetrics();
        
        // Update engine information
        this.updateEngineInfo();
        
        // Display side-by-side comparison
        this.displaySideBySide();
        
        // Create charts
        this.createCharts();
        
        // Show comparison content (remove hidden class)
        document.getElementById('comparison-content').classList.remove('hidden');
        document.getElementById('charts-section').classList.remove('hidden');
        
        console.log('✅ Comparison displayed successfully');
    }
    
    updateMetrics() {
        const metrics = this.comparisonData.metrics;
        
        document.getElementById('cer-value').textContent = metrics.cer.toFixed(1) + '%';
        document.getElementById('wer-value').textContent = metrics.wer.toFixed(1) + '%';
        document.getElementById('accuracy-value').textContent = metrics.accuracy.toFixed(1);
        document.getElementById('similarity-value').textContent = metrics.similarity.toFixed(1);
        
        // Add color coding based on accuracy
        const accuracyEl = document.getElementById('accuracy-value');
        if (metrics.accuracy >= 90) {
            accuracyEl.style.color = '#28a745'; // Green
        } else if (metrics.accuracy >= 70) {
            accuracyEl.style.color = '#ffc107'; // Yellow
        } else {
            accuracyEl.style.color = '#dc3545'; // Red
        }
    }
    
    updateEngineInfo() {
        const eng1 = this.comparisonData.engine1;
        const eng2 = this.comparisonData.engine2;
        
        // Engine 1 (Kraken)
        document.getElementById('kraken-model').textContent = eng1.model;
        document.getElementById('kraken-confidence').textContent = 
            (eng1.avg_confidence * 100).toFixed(1) + '%';
        document.getElementById('kraken-lines').textContent = eng1.line_count;
        document.getElementById('kraken-created').textContent = 
            this.formatDate(eng1.created);
        
        // Engine 2 (Tesseract)
        document.getElementById('tesseract-model').textContent = eng2.model;
        document.getElementById('tesseract-confidence').textContent = 
            (eng2.avg_confidence * 100).toFixed(1) + '%';
        document.getElementById('tesseract-lines').textContent = eng2.line_count;
        document.getElementById('tesseract-created').textContent = 
            this.formatDate(eng2.created);
    }
    
    displaySideBySide() {
        const diffData = this.comparisonData.diff;
        
        const lineNumbers = document.getElementById('line-numbers');
        const krakenContent = document.getElementById('kraken-lines-content');
        const tesseractContent = document.getElementById('tesseract-lines-content');
        
        // Clear existing content
        lineNumbers.innerHTML = '';
        krakenContent.innerHTML = '';
        tesseractContent.innerHTML = '';
        
        diffData.forEach(line => {
            // Line number
            const lineNum = document.createElement('div');
            lineNum.className = 'line-number';
            lineNum.textContent = line.line_num;
            lineNumbers.appendChild(lineNum);
            
            // Kraken line
            const krakenLine = this.createLineElement(
                line.text1, 
                line.diff_type, 
                line.confidence1
            );
            krakenContent.appendChild(krakenLine);
            
            // Tesseract line
            const tesseractLine = this.createLineElement(
                line.text2, 
                line.diff_type, 
                line.confidence2
            );
            tesseractContent.appendChild(tesseractLine);
        });
    }
    
    createLineElement(text, diffType, confidence) {
        const lineDiv = document.createElement('div');
        lineDiv.className = `line-content ${diffType}`;
        
        if (text) {
            // Check if text is RTL (Hebrew/Arabic)
            const isRTL = /[\u0590-\u05FF\u0600-\u06FF]/.test(text);
            if (isRTL) {
                lineDiv.dir = 'rtl';
            }
            lineDiv.textContent = text;
        } else {
            const emptyText = document.createElement('em');
            emptyText.textContent = 'Empty';
            emptyText.style.color = '#999';
            lineDiv.appendChild(emptyText);
        }
        
        // Add confidence bar
        if (confidence !== null && confidence !== undefined) {
            const bar = document.createElement('div');
            bar.className = 'confidence-bar';
            bar.style.width = (confidence * 100) + '%';
            bar.title = `Confidence: ${(confidence * 100).toFixed(1)}%`;
            lineDiv.appendChild(bar);
        }
        
        return lineDiv;
    }
    
    createCharts() {
        const data = this.comparisonData;
        
        // 1. CER/WER Bar Chart
        this.charts.cer = new Chart(document.getElementById('cerChart'), {
            type: 'bar',
            data: {
                labels: ['CER', 'WER'],
                datasets: [{
                    label: 'Error Rate (%)',
                    data: [data.metrics.cer, data.metrics.wer],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)'
                    ],
                    borderColor: [
                        'rgba(102, 126, 234, 1)',
                        'rgba(118, 75, 162, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (context) => `${context.parsed.y.toFixed(1)}%`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: (value) => value + '%'
                        }
                    }
                }
            }
        });
        
        // 2. Confidence Line Chart
        const confidenceData = data.diff
            .filter(line => line.confidence1 !== null && line.confidence2 !== null)
            .map(line => ({
                line_num: line.line_num,
                kraken: line.confidence1 * 100,
                tesseract: line.confidence2 * 100
            }));
        
        this.charts.confidence = new Chart(document.getElementById('confidenceChart'), {
            type: 'line',
            data: {
                labels: confidenceData.map(d => d.line_num),
                datasets: [
                    {
                        label: 'Kraken',
                        data: confidenceData.map(d => d.kraken),
                        borderColor: 'rgba(102, 126, 234, 1)',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'Tesseract',
                        data: confidenceData.map(d => d.tesseract),
                        borderColor: 'rgba(118, 75, 162, 1)',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4,
                        fill: true,
                        pointRadius: 3,
                        pointHoverRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    tooltip: {
                        callbacks: {
                            label: (context) => 
                                `${context.dataset.label}: ${context.parsed.y.toFixed(1)}%`
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: (value) => value + '%'
                        }
                    }
                }
            }
        });
        
        // 3. Accuracy Doughnut Chart
        const matches = data.diff.filter(l => l.diff_type === 'identical').length;
        const mismatches = data.diff.length - matches;
        
        this.charts.accuracy = new Chart(document.getElementById('accuracyChart'), {
            type: 'doughnut',
            data: {
                labels: ['Identical Lines', 'Different Lines'],
                datasets: [{
                    data: [matches, mismatches],
                    backgroundColor: [
                        'rgba(40, 167, 69, 0.8)',
                        'rgba(255, 193, 7, 0.8)'
                    ],
                    borderColor: [
                        'rgba(40, 167, 69, 1)',
                        'rgba(255, 193, 7, 1)'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
    
    exportComparison() {
        if (!this.trans1Id || !this.trans2Id) return;
        
        // Redirect to export endpoint
        window.location.href = `/api/comparison/${this.trans1Id}/${this.trans2Id}/export/`;
    }
    
    async copyResults() {
        if (!this.comparisonData) return;
        
        const data = this.comparisonData;
        let text = '═══════════════════════════════════\n';
        text += '  OCR ENGINE COMPARISON RESULTS\n';
        text += '═══════════════════════════════════\n\n';
        
        text += '📊 METRICS:\n';
        text += `  • CER:        ${data.metrics.cer.toFixed(1)}%\n`;
        text += `  • WER:        ${data.metrics.wer.toFixed(1)}%\n`;
        text += `  • Accuracy:   ${data.metrics.accuracy.toFixed(1)}%\n`;
        text += `  • Similarity: ${data.metrics.similarity.toFixed(1)}%\n\n`;
        
        text += '🐙 KRAKEN:\n';
        text += `  • Model:      ${data.engine1.model}\n`;
        text += `  • Confidence: ${(data.engine1.avg_confidence * 100).toFixed(1)}%\n`;
        text += `  • Lines:      ${data.engine1.line_count}\n\n`;
        
        text += '🔷 TESSERACT:\n';
        text += `  • Model:      ${data.engine2.model}\n`;
        text += `  • Confidence: ${(data.engine2.avg_confidence * 100).toFixed(1)}%\n`;
        text += `  • Lines:      ${data.engine2.line_count}\n\n`;
        
        text += '═══════════════════════════════════\n';
        text += 'LINE-BY-LINE COMPARISON:\n';
        text += '═══════════════════════════════════\n\n';
        
        data.diff.forEach(line => {
            const statusIcon = {
                'identical': '✓',
                'modified': '~',
                'added': '+',
                'removed': '-'
            }[line.diff_type] || '?';
            
            text += `${statusIcon} Line ${line.line_num} [${line.diff_type}]\n`;
            text += `  Kraken:    ${line.text1 || '(empty)'}\n`;
            text += `  Tesseract: ${line.text2 || '(empty)'}\n\n`;
        });
        
        try {
            await navigator.clipboard.writeText(text);
            this.showNotification('✅ Results copied to clipboard!', 'success');
        } catch (error) {
            console.error('Copy failed:', error);
            this.showNotification('❌ Failed to copy results', 'error');
        }
    }
    
    showLoading(show) {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = show ? 'block' : 'none';
        }
    }
    
    showError(message) {
        this.showLoading(false);
        
        const errorDiv = document.getElementById('error');
        if (errorDiv) {
            errorDiv.classList.remove('hidden');
            errorDiv.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Error:</strong> ${message}
            `;
        }
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
            background: ${type === 'success' ? '#28a745' : '#dc3545'};
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
    
    formatDate(dateString) {
        const date = new Date(dateString);
        const options = { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return date.toLocaleDateString(undefined, options);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.comparisonViewer = new ComparisonViewer();
});

// Export functions for button clicks
function exportComparison() {
    if (window.comparisonViewer) {
        window.comparisonViewer.exportComparison();
    }
}

function copyResults() {
    if (window.comparisonViewer) {
        window.comparisonViewer.copyResults();
    }
}

// Add animations CSS
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
`;
document.head.appendChild(style);
