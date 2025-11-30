<template>
    <div v-if="partsLoaded" id="unified-editor" class="unified-editor-container">
        <!-- Top Menu Bar - כמו ABBYY -->
        <div class="unified-menu-bar">
            <div class="menu-section">
                <button class="menu-btn" @click="openFileMenu">
                    <i class="fas fa-folder-open"></i> {{ translate('File') }}
                </button>
                <button class="menu-btn" @click="openEditMenu">
                    <i class="fas fa-edit"></i> {{ translate('Edit') }}
                </button>
                <button class="menu-btn" @click="openViewMenu">
                    <i class="fas fa-eye"></i> {{ translate('View') }}
                </button>
                <button class="menu-btn" @click="openToolsMenu">
                    <i class="fas fa-tools"></i> {{ translate('Tools') }}
                </button>
            </div>
            
            <div class="menu-section menu-right">
                <span class="document-title">{{ documentName }}</span>
                <button class="menu-btn" @click="switchToClassicMode" :title="translate('Switch to Classic Mode')">
                    <i class="fas fa-exchange-alt"></i> {{ translate('Classic') }}
                </button>
                <button class="menu-btn" :title="translate('Settings')">
                    <i class="fas fa-cog"></i>
                </button>
                <button class="menu-btn" :title="translate('User Profile')">
                    <i class="fas fa-user"></i>
                </button>
            </div>
        </div>

        <!-- Main Content Area - 3 columns -->
        <div class="unified-main-content">
            <!-- Left Sidebar: Pages List -->
            <div class="unified-sidebar unified-sidebar-left">
                <div class="sidebar-header">
                    <i class="fas fa-file-alt"></i>
                    <span>{{ translate('Pages') }}</span>
                </div>
                <div class="pages-list">
                    <div 
                        v-for="part in parts" 
                        :key="part.pk"
                        :class="['page-item', { active: part.pk === currentPartPk }]"
                        @click="selectPart(part.pk)"
                    >
                        <div class="page-thumbnail">
                            <img 
                                v-if="part.image" 
                                :src="(part.image.thumbnails && part.image.thumbnails.card) || part.image.uri" 
                                :alt="`Page ${part.order}`"
                            >
                            <div v-else class="page-placeholder">
                                <i class="fas fa-image"></i>
                            </div>
                        </div>
                        <div class="page-info">
                            <div class="page-number">{{ part.order }}</div>
                            <div class="page-name">{{ part.name || `Page ${part.order}` }}</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Center Area: Image + Text -->
            <div class="unified-center-area">
                <!-- Image View (Top) -->
                <div class="unified-image-panel">
                    <div class="panel-header">
                        <i class="fas fa-image"></i>
                        <span>{{ translate('Image View') }}</span>
                        <div class="panel-tools">
                            <button @click="zoomIn" :title="translate('Zoom In')">
                                <i class="fas fa-search-plus"></i>
                            </button>
                            <button @click="zoomOut" :title="translate('Zoom Out')">
                                <i class="fas fa-search-minus"></i>
                            </button>
                            <button @click="zoomReset" :title="translate('Reset Zoom')">
                                <i class="fas fa-expand"></i>
                            </button>
                            <button @click="rotate" :title="translate('Rotate')">
                                <i class="fas fa-redo"></i>
                            </button>
                        </div>
                    </div>
                    <div class="panel-content">
                        <!-- כאן נטמיע את SegPanel או SourcePanel הקיים -->
                        <component 
                            :is="imageViewComponent" 
                            v-if="partsLoaded"
                            :fullsizeimage="fullsizeimage"
                            :legacy-mode-enabled="false"
                            :disabled="isWorking"
                        />
                    </div>
                </div>

                <!-- Resizer -->
                <div class="unified-resizer" @mousedown="startResize"></div>

                <!-- Text View (Bottom) -->
                <div class="unified-text-panel">
                    <div class="panel-header">
                        <i class="fas fa-align-left"></i>
                        <span>{{ translate('Text Editor') }}</span>
                        <div class="panel-tools">
                            <button @click="saveTranscription" :title="translate('Save')">
                                <i class="fas fa-save"></i>
                            </button>
                            <button @click="toggleConfidence" :title="translate('Show Confidence')">
                                <i class="fas fa-percentage"></i>
                            </button>
                        </div>
                    </div>
                    <div class="panel-content">
                        <!-- כאן נטמיע את VisuPanel הקיים -->
                        <VisuPanel
                            v-if="partsLoaded"
                            :fullsizeimage="false"
                            :legacy-mode-enabled="false"
                            :disabled="isWorking"
                        />
                    </div>
                </div>
            </div>

            <!-- Right Sidebar: Tools -->
            <div class="unified-sidebar unified-sidebar-right">
                <div class="sidebar-header">
                    <i class="fas fa-toolbox"></i>
                    <span>{{ translate('Tools') }}</span>
                </div>
                
                <div class="tools-tabs">
                    <button 
                        :class="['tool-tab', { active: activeTab === 'segment' }]"
                        @click="activeTab = 'segment'"
                    >
                        <i class="fas fa-vector-square"></i>
                        <span>{{ translate('Segment') }}</span>
                    </button>
                    <button 
                        :class="['tool-tab', { active: activeTab === 'transcribe' }]"
                        @click="activeTab = 'transcribe'"
                    >
                        <i class="fas fa-keyboard"></i>
                        <span>{{ translate('Transcribe') }}</span>
                    </button>
                    <button 
                        :class="['tool-tab', { active: activeTab === 'correct' }]"
                        @click="activeTab = 'correct'"
                    >
                        <i class="fas fa-spell-check"></i>
                        <span>{{ translate('Correct') }}</span>
                    </button>
                    <button 
                        :class="['tool-tab', { active: activeTab === 'properties' }]"
                        @click="activeTab = 'properties'"
                    >
                        <i class="fas fa-info-circle"></i>
                        <span>{{ translate('Properties') }}</span>
                    </button>
                </div>

                <div class="tools-content">
                    <!-- Segmentation Tools -->
                    <div v-if="activeTab === 'segment'" class="tool-panel">
                        <h3>{{ translate('Segmentation') }}</h3>
                        <button class="tool-action-btn" @click="runSegmentation">
                            <i class="fas fa-play"></i> {{ translate('Run Segmentation') }}
                        </button>
                        <button class="tool-action-btn" @click="clearSegmentation">
                            <i class="fas fa-eraser"></i> {{ translate('Clear All') }}
                        </button>
                    </div>

                    <!-- Transcription Tools -->
                    <div v-if="activeTab === 'transcribe'" class="tool-panel">
                        <h3>{{ translate('Transcription') }}</h3>
                        <button class="tool-action-btn" @click="runTranscription">
                            <i class="fas fa-play"></i> {{ translate('Run Transcription') }}
                        </button>
                        <div class="tool-options">
                            <label>{{ translate('Model:') }}</label>
                            <select v-model="selectedModel">
                                <option v-for="model in models" :key="model.pk" :value="model.pk">
                                    {{ model.name }}
                                </option>
                            </select>
                        </div>
                    </div>

                    <!-- Error Correction Tools -->
                    <div v-if="activeTab === 'correct'" class="tool-panel">
                        <h3>{{ translate('Error Correction') }}</h3>
                        <button class="tool-action-btn" @click="runSpellCheck">
                            <i class="fas fa-spell-check"></i> {{ translate('Spell Check') }}
                        </button>
                        <button class="tool-action-btn" @click="runErrorDetection">
                            <i class="fas fa-search"></i> {{ translate('Detect Errors') }}
                        </button>
                        <button class="tool-action-btn" @click="runAutoCorrect">
                            <i class="fas fa-magic"></i> {{ translate('Auto Correct') }}
                        </button>
                        
                        <div v-if="errorResults.length > 0" class="error-results">
                            <h4>{{ translate('Found Errors:') }}</h4>
                            <div 
                                v-for="(error, index) in errorResults" 
                                :key="index"
                                class="error-item"
                            >
                                <span class="error-word">{{ error.word }}</span>
                                <span class="error-suggestion">→ {{ error.suggestion }}</span>
                                <button @click="applyCorrection(error)" class="apply-btn">
                                    <i class="fas fa-check"></i>
                                </button>
                            </div>
                        </div>
                    </div>

                    <!-- Properties -->
                    <div v-if="activeTab === 'properties'" class="tool-panel">
                        <h3>{{ translate('Document Properties') }}</h3>
                        <div class="property-item">
                            <label>{{ translate('Name:') }}</label>
                            <span>{{ documentName }}</span>
                        </div>
                        <div class="property-item">
                            <label>{{ translate('Pages:') }}</label>
                            <span>{{ partsCount }}</span>
                        </div>
                        <div class="property-item">
                            <label>{{ translate('Language:') }}</label>
                            <span>{{ mainTextDirection }}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Status Bar -->
        <div class="unified-status-bar">
            <div class="status-item">
                <i class="fas fa-file-alt"></i>
                <span>{{ translate('Page') }} {{ currentPartOrder }} / {{ partsCount }}</span>
            </div>
            <div class="status-item">
                <i class="fas fa-clock"></i>
                <span>{{ lastSaved }}</span>
            </div>
            <div class="status-item" v-if="isWorking">
                <i class="fas fa-spinner fa-spin"></i>
                <span>{{ translate('Processing...') }}</span>
            </div>
        </div>
    </div>
    <div v-else class="unified-editor-loading">
        <i class="fas fa-spinner fa-spin"></i>
        <span>{{ translate('Loading parts...') }}</span>
    </div>
</template>

<script>
import { mapState, mapActions, mapMutations } from 'vuex';
import SegPanel from './SegPanel.vue';
import VisuPanel from './VisuPanel.vue';
import SourcePanel from './SourcePanel.vue';

export default {
    name: 'UnifiedEditor',
    components: {
        SegPanel,
        VisuPanel,
        SourcePanel,
    },
    data() {
        return {
            activeTab: 'segment',
            fullsizeimage: false,
            isWorking: false,
            imageViewComponent: 'SegPanel',
            selectedModel: null,
            errorResults: [],
            lastSaved: 'Auto-saved',
            resizing: false,
            startY: 0,
            startHeight: 0,
        };
    },
    computed: {
        ...mapState({
            documentName: state => state.document?.name || '',
            currentPartPk: state => state.parts?.pk,
            currentPartOrder: state => state.parts?.order || 1,
            mainTextDirection: state => state.document?.mainTextDirection || 'ltr',
            models: state => state.models?.list || [],
        }),
        // Separate computed property for parts with proper null check
        parts() {
            return this.$store.state.document?.parts || [];
        },
        // Helper to check if parts are loaded
        partsLoaded() {
            return Array.isArray(this.parts) && this.parts.length > 0;
        },
        // Helper to safely get parts count
        partsCount() {
            return this.parts?.length || 0;
        },
    },
    methods: {
        ...mapActions('parts', ['loadPart']),
        ...mapMutations('document', ['setBlockShortcuts']),
        
        selectPart(partPk) {
            this.loadPart(partPk);
        },
        
        // Zoom controls
        zoomIn() {
            this.$emit('zoom-in');
        },
        zoomOut() {
            this.$emit('zoom-out');
        },
        zoomReset() {
            this.$emit('zoom-reset');
        },
        rotate() {
            this.$emit('rotate');
        },
        
        // Tools actions
        runSegmentation() {
            this.isWorking = true;
            // TODO: Implement segmentation API call
            setTimeout(() => { this.isWorking = false; }, 2000);
        },
        
        clearSegmentation() {
            // TODO: Implement clear segmentation
        },
        
        runTranscription() {
            this.isWorking = true;
            // TODO: Implement transcription API call
            setTimeout(() => { this.isWorking = false; }, 2000);
        },
        
        saveTranscription() {
            // TODO: Implement save
            this.lastSaved = new Date().toLocaleTimeString();
        },
        
        toggleConfidence() {
            // TODO: Toggle confidence visualization
        },
        
        // Error Correction
        async runSpellCheck() {
            this.isWorking = true;
            try {
                // TODO: Call spell check API
                this.errorResults = [
                    { word: 'שלומ', suggestion: 'שלום', line: 1 },
                    { word: 'עולאם', suggestion: 'עולם', line: 2 },
                ];
            } finally {
                this.isWorking = false;
            }
        },
        
        async runErrorDetection() {
            this.isWorking = true;
            try {
                // TODO: Call error detection API
            } finally {
                this.isWorking = false;
            }
        },
        
        async runAutoCorrect() {
            this.isWorking = true;
            try {
                // TODO: Call auto correct API
            } finally {
                this.isWorking = false;
            }
        },
        
        applyCorrection(error) {
            // TODO: Apply correction to text
            this.errorResults = this.errorResults.filter(e => e !== error);
        },
        
        // Menu actions
        openFileMenu() { /* TODO */ },
        openEditMenu() { /* TODO */ },
        openViewMenu() { /* TODO */ },
        openToolsMenu() { /* TODO */ },
        
        switchToClassicMode() {
            // Save preference
            userProfile.set('editor-mode', 'classic');
            // Reload page without mode parameter
            const url = new URL(window.location.href);
            url.searchParams.delete('mode');
            window.location.href = url.toString();
        },
        
        // Resizer
        startResize(e) {
            this.resizing = true;
            this.startY = e.clientY;
            const imagePanel = e.target.previousElementSibling;
            this.startHeight = imagePanel.offsetHeight;
            document.addEventListener('mousemove', this.doResize);
            document.addEventListener('mouseup', this.stopResize);
        },
        
        doResize(e) {
            if (!this.resizing) return;
            const delta = e.clientY - this.startY;
            const imagePanel = document.querySelector('.unified-image-panel');
            const newHeight = this.startHeight + delta;
            if (newHeight > 200 && newHeight < window.innerHeight - 400) {
                imagePanel.style.height = `${newHeight}px`;
            }
        },
        
        stopResize() {
            this.resizing = false;
            document.removeEventListener('mousemove', this.doResize);
            document.removeEventListener('mouseup', this.stopResize);
        },
        
        translate(key) {
            return window.EDITOR_TRANSLATIONS && window.EDITOR_TRANSLATIONS[key] 
                ? window.EDITOR_TRANSLATIONS[key] 
                : key;
        }
    },
};
</script>

<style scoped>
/* הכל בדף אחד - Layout כמו ABBYY FineReader */
.unified-editor-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: var(--background2, #2b2b2b);
    color: var(--text1, #e0e0e0);
    font-family: 'Noto Sans', sans-serif;
}

/* Top Menu Bar */
.unified-menu-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 48px;
    background: var(--background1, #1e1e1e);
    border-bottom: 1px solid var(--border, #444);
    padding: 0 16px;
}

.menu-section {
    display: flex;
    gap: 8px;
}

.menu-btn {
    background: transparent;
    border: none;
    color: var(--text1, #e0e0e0);
    padding: 8px 16px;
    cursor: pointer;
    border-radius: 4px;
    font-size: 14px;
    transition: background 0.2s;
}

.menu-btn:hover {
    background: var(--background3, #3a3a3a);
}

.document-title {
    font-weight: bold;
    margin-right: 16px;
}

/* Main Content - 3 Columns */
.unified-main-content {
    display: grid;
    grid-template-columns: 250px 1fr 320px;
    flex: 1;
    overflow: hidden;
}

/* Sidebars */
.unified-sidebar {
    background: var(--background1, #1e1e1e);
    border-right: 1px solid var(--border, #444);
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.unified-sidebar-right {
    border-right: none;
    border-left: 1px solid var(--border, #444);
}

.sidebar-header {
    padding: 16px;
    border-bottom: 1px solid var(--border, #444);
    font-weight: bold;
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Pages List */
.pages-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
}

.page-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px;
    border-radius: 6px;
    cursor: pointer;
    margin-bottom: 4px;
    transition: background 0.2s;
}

.page-item:hover {
    background: var(--background3, #3a3a3a);
}

.page-item.active {
    background: var(--primary, #667eea);
    color: white;
}

.page-thumbnail {
    width: 60px;
    height: 80px;
    border: 1px solid var(--border, #444);
    border-radius: 4px;
    overflow: hidden;
    flex-shrink: 0;
}

.page-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.page-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--background3, #3a3a3a);
    color: var(--text2, #888);
}

.page-info {
    flex: 1;
}

.page-number {
    font-weight: bold;
    font-size: 16px;
}

.page-name {
    font-size: 12px;
    color: var(--text2, #888);
}

/* Center Area */
.unified-center-area {
    display: flex;
    flex-direction: column;
    background: var(--background2, #2b2b2b);
}

.unified-image-panel {
    height: 50%;
    display: flex;
    flex-direction: column;
    border-bottom: 1px solid var(--border, #444);
}

.unified-text-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    background: var(--background1, #1e1e1e);
    border-bottom: 1px solid var(--border, #444);
    font-weight: bold;
}

.panel-header > span {
    margin-left: 8px;
}

.panel-tools {
    display: flex;
    gap: 4px;
}

.panel-tools button {
    background: transparent;
    border: none;
    color: var(--text1, #e0e0e0);
    padding: 6px 12px;
    cursor: pointer;
    border-radius: 4px;
    transition: background 0.2s;
}

.panel-tools button:hover {
    background: var(--background3, #3a3a3a);
}

.panel-content {
    flex: 1;
    overflow: auto;
    position: relative;
}

/* Resizer */
.unified-resizer {
    height: 4px;
    background: var(--border, #444);
    cursor: ns-resize;
    transition: background 0.2s;
}

.unified-resizer:hover {
    background: var(--primary, #667eea);
}

/* Tools Tabs */
.tools-tabs {
    display: flex;
    flex-direction: column;
    border-bottom: 1px solid var(--border, #444);
}

.tool-tab {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: transparent;
    border: none;
    color: var(--text1, #e0e0e0);
    cursor: pointer;
    text-align: left;
    transition: background 0.2s;
    border-left: 3px solid transparent;
}

.tool-tab:hover {
    background: var(--background3, #3a3a3a);
}

.tool-tab.active {
    background: var(--background3, #3a3a3a);
    border-left-color: var(--primary, #667eea);
    font-weight: bold;
}

/* Tools Content */
.tools-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
}

.tool-panel h3 {
    margin: 0 0 16px 0;
    font-size: 16px;
}

.tool-action-btn {
    width: 100%;
    padding: 12px;
    background: var(--primary, #667eea);
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
    margin-bottom: 8px;
    transition: background 0.2s;
}

.tool-action-btn:hover {
    background: var(--primary-dark, #5568d3);
}

.tool-options {
    margin-top: 16px;
}

.tool-options label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
}

.tool-options select {
    width: 100%;
    padding: 8px;
    background: var(--background3, #3a3a3a);
    color: var(--text1, #e0e0e0);
    border: 1px solid var(--border, #444);
    border-radius: 4px;
}

/* Error Results */
.error-results {
    margin-top: 16px;
    padding: 12px;
    background: var(--background3, #3a3a3a);
    border-radius: 6px;
}

.error-results h4 {
    margin: 0 0 12px 0;
    font-size: 14px;
}

.error-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    background: var(--background2, #2b2b2b);
    border-radius: 4px;
    margin-bottom: 4px;
}

.error-word {
    color: #ff6b6b;
    font-weight: bold;
}

.error-suggestion {
    color: #51cf66;
    flex: 1;
}

.apply-btn {
    background: #51cf66;
    color: white;
    border: none;
    padding: 4px 12px;
    border-radius: 4px;
    cursor: pointer;
}

/* Properties */
.property-item {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid var(--border, #444);
}

.property-item label {
    font-weight: bold;
}

/* Status Bar */
.unified-status-bar {
    display: flex;
    align-items: center;
    gap: 24px;
    height: 32px;
    background: var(--background1, #1e1e1e);
    border-top: 1px solid var(--border, #444);
    padding: 0 16px;
    font-size: 12px;
}

.status-item {
    display: flex;
    align-items: center;
    gap: 8px;
}

.unified-editor-loading {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    height: 100vh;
    color: var(--text1, #e0e0e0);
    background: var(--background2, #2b2b2b);
    font-size: 16px;
}

/* Scrollbars */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--background2, #2b2b2b);
}

::-webkit-scrollbar-thumb {
    background: var(--border, #444);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: var(--text2, #888);
}
</style>
