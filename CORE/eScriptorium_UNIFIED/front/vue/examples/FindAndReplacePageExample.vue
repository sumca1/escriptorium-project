<!-- 
    דוגמה מלאה - Find & Replace Page with Progress & Help
    Created: 2 נובמבר 2025
-->

<template>
    <div class="find-replace-container">
        <!-- Page Header -->
        <div class="page-header">
            <h1 class="page-title">
                {{ $t('Find & Replace') }}
            </h1>
            <!-- 🆕 Help Button! -->
            <HelpButton topic="find-replace" />
        </div>

        <!-- Search Form -->
        <form @submit.prevent="handleSearch" class="search-form">
            <div class="form-group">
                <label for="find-input">{{ $t('Find') }}:</label>
                <input 
                    id="find-input"
                    v-model="findText" 
                    type="text" 
                    class="form-control"
                    :placeholder="$t('Enter text to find...')"
                    required
                />
            </div>

            <div class="form-group">
                <label for="replace-input">{{ $t('Replace with') }}:</label>
                <input 
                    id="replace-input"
                    v-model="replaceText" 
                    type="text" 
                    class="form-control"
                    :placeholder="$t('Enter replacement text...')"
                />
            </div>

            <div class="form-group">
                <label>
                    <input type="checkbox" v-model="useRegex" />
                    {{ $t('Use Regular Expression') }}
                </label>
            </div>

            <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="isReplacing">
                    {{ $t('Search') }}
                </button>
                <button 
                    v-if="searchResults.length > 0 && !isReplacing"
                    @click="applyReplace" 
                    type="button" 
                    class="btn btn-success"
                >
                    {{ $t('Apply Replacement') }} ({{ searchResults.length }})
                </button>
            </div>
        </form>

        <!-- Search Results Preview -->
        <div v-if="searchResults.length > 0 && !isReplacing" class="results-preview">
            <h3>{{ $t('Preview') }} ({{ searchResults.length }} {{ $t('results') }})</h3>
            <div class="results-list">
                <div 
                    v-for="(result, index) in searchResults.slice(0, 10)" 
                    :key="index"
                    class="result-item"
                >
                    <div class="result-before">
                        <span class="result-label">{{ $t('Before') }}:</span>
                        <span v-html="result.highlighted_content"></span>
                    </div>
                    <div class="result-after">
                        <span class="result-label">{{ $t('After') }}:</span>
                        <span>{{ result.replaced_content }}</span>
                    </div>
                </div>
                <div v-if="searchResults.length > 10" class="more-results">
                    {{ $t('And') }} {{ searchResults.length - 10 }} {{ $t('more results') }}...
                </div>
            </div>
        </div>

        <!-- 🆕 Progress Indicator! -->
        <ProgressIndicator
            :active="isReplacing"
            :title="$t('Applying Replacements')"
            :total="progress.total"
            :processed="progress.processed"
            :errors="progress.errors"
            :elapsedTime="progress.elapsed"
            :estimatedRemaining="progress.remaining"
            :speed="progress.speed"
            :canceling="isCanceling"
            @cancel="cancelReplacement"
        />
    </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue';
import HelpButton from '@/components/HelpButton/HelpButton.vue';
import ProgressIndicator from '@/components/ProgressIndicator/ProgressIndicator.vue';

export default {
    name: 'FindAndReplacePage',
    components: {
        HelpButton,
        ProgressIndicator
    },
    setup() {
        // Form data
        const findText = ref('');
        const replaceText = ref('');
        const useRegex = ref(false);
        const searchResults = ref([]);

        // Progress tracking
        const isReplacing = ref(false);
        const isCanceling = ref(false);
        const progress = ref({
            task_id: null,
            total: 0,
            processed: 0,
            errors: 0,
            elapsed: 0,
            remaining: 0,
            speed: 0
        });

        // WebSocket
        let ws = null;

        // Get document ID from URL or context
        const getDocumentId = () => {
            const match = window.location.pathname.match(/\/document\/(\d+)\//);
            return match ? match[1] : null;
        };

        // Connect to WebSocket for real-time updates
        const connectWebSocket = () => {
            const documentId = getDocumentId();
            if (!documentId) {
                console.warn('No document ID found - progress updates disabled');
                return;
            }

            ws = new ReconnectingWebSocket(
                `ws://${window.location.host}/ws/notif/document/${documentId}/`
            );

            ws.onopen = () => {
                console.log('WebSocket connected - ready for progress updates');
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                
                if (data.type === 'notification_event') {
                    handleProgressEvent(data);
                }
            };

            ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };

            ws.onclose = () => {
                console.log('WebSocket closed');
            };
        };

        // Handle progress events from WebSocket
        const handleProgressEvent = (data) => {
            const eventType = data.event_name;
            const eventData = data.data;

            console.log('Progress event:', eventType, eventData);

            if (eventType === 'replace:start') {
                isReplacing.value = true;
                isCanceling.value = false;
                progress.value.task_id = eventData.task_id;
                progress.value.total = eventData.total;
                progress.value.processed = 0;
                progress.value.errors = 0;
                progress.value.elapsed = 0;
                progress.value.remaining = 0;
                progress.value.speed = 0;
            }
            else if (eventType === 'replace:progress') {
                progress.value.processed = eventData.processed;
                progress.value.errors = eventData.errors;
                progress.value.elapsed = eventData.elapsed_time;
                progress.value.remaining = eventData.estimated_remaining;
                progress.value.speed = eventData.speed;
            }
            else if (eventType === 'replace:done') {
                // Final update
                progress.value.processed = eventData.processed;
                progress.value.errors = eventData.errors;
                progress.value.elapsed = eventData.total_time;
                progress.value.remaining = 0;

                // Wait 2 seconds to show final state, then hide
                setTimeout(() => {
                    isReplacing.value = false;
                    isCanceling.value = false;
                    
                    // Refresh results or show success message
                    console.log('Replacement completed successfully!');
                    searchResults.value = []; // Clear results
                }, 2000);
            }
        };

        // Search for matches
        const handleSearch = async () => {
            if (!findText.value) return;

            try {
                const formData = new FormData();
                formData.append('find', findText.value);
                formData.append('mode', useRegex.value ? 'regex' : 'word');

                const response = await fetch(window.location.pathname, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCsrfToken()
                    }
                });

                if (response.ok) {
                    const html = await response.text();
                    // Parse results from response
                    // (In real app, you'd parse the returned HTML or use JSON API)
                    console.log('Search completed');
                    
                    // Demo: simulate results
                    searchResults.value = Array(25).fill(null).map((_, i) => ({
                        highlighted_content: `Line ${i + 1}: ...${findText.value}...`,
                        replaced_content: `Line ${i + 1}: ...${replaceText.value}...`
                    }));
                }
            } catch (error) {
                console.error('Search error:', error);
            }
        };

        // Apply replacement
        const applyReplace = async () => {
            if (!confirm(`Apply replacement to ${searchResults.value.length} lines?`)) {
                return;
            }

            try {
                const formData = new FormData();
                formData.append('find', findText.value);
                formData.append('replace', replaceText.value);
                formData.append('mode', useRegex.value ? 'regex' : 'word');
                formData.append('apply_replace', 'true');

                const response = await fetch(window.location.pathname, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCsrfToken()
                    }
                });

                if (response.ok) {
                    console.log('Replacement task started - progress updates via WebSocket');
                    // Progress updates will come via WebSocket
                }
            } catch (error) {
                console.error('Replace error:', error);
            }
        };

        // Cancel replacement
        const cancelReplacement = async () => {
            if (!progress.value.task_id) return;

            isCanceling.value = true;

            try {
                const response = await fetch(`/api/tasks/${progress.value.task_id}/cancel/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCsrfToken()
                    }
                });

                if (response.ok) {
                    console.log('Cancellation requested');
                }
            } catch (error) {
                console.error('Cancel error:', error);
                isCanceling.value = false;
            }
        };

        // Get CSRF token
        const getCsrfToken = () => {
            const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
            return cookie ? cookie.split('=')[1] : '';
        };

        // Lifecycle
        onMounted(() => {
            connectWebSocket();
        });

        onUnmounted(() => {
            if (ws) {
                ws.close();
            }
        });

        return {
            // Form
            findText,
            replaceText,
            useRegex,
            searchResults,
            handleSearch,
            applyReplace,

            // Progress
            isReplacing,
            isCanceling,
            progress,
            cancelReplacement
        };
    }
};
</script>

<style scoped>
.find-replace-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    padding-bottom: 15px;
    border-bottom: 2px solid var(--border);
}

.page-title {
    margin: 0;
    font-size: 28px;
    font-weight: 600;
    color: var(--text1);
}

.search-form {
    background: var(--background1);
    padding: 24px;
    border-radius: 8px;
    border: 1px solid var(--border);
    margin-bottom: 24px;
}

.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--text1);
}

.form-control {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 4px;
    font-size: 14px;
}

.form-actions {
    display: flex;
    gap: 12px;
    margin-top: 20px;
}

.btn {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-primary {
    background: var(--primary);
    color: white;
}

.btn-primary:hover:not(:disabled) {
    background: var(--primary-hover);
}

.btn-success {
    background: var(--success);
    color: white;
}

.btn-success:hover {
    background: #218838;
}

.btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.results-preview {
    background: var(--background1);
    padding: 24px;
    border-radius: 8px;
    border: 1px solid var(--border);
}

.results-preview h3 {
    margin: 0 0 16px 0;
    font-size: 18px;
    color: var(--text1);
}

.results-list {
    max-height: 400px;
    overflow-y: auto;
}

.result-item {
    padding: 12px;
    margin-bottom: 12px;
    background: var(--background2);
    border-radius: 4px;
    border-left: 3px solid var(--primary);
}

.result-before,
.result-after {
    margin-bottom: 6px;
}

.result-label {
    font-weight: 600;
    margin-right: 8px;
    color: var(--text2);
}

.more-results {
    padding: 12px;
    text-align: center;
    color: var(--text3);
    font-style: italic;
}
</style>
