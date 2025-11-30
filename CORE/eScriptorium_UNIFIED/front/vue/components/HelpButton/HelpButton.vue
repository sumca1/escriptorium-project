<template>
    <div class="escr-help-button">
        <!-- Help Icon Button -->
        <button 
            @click="toggleHelp" 
            class="escr-help-icon-btn"
            :class="{ 'active': showHelp }"
            :aria-label="translate('Help')"
            :title="translate('Help')"
        >
            <QuestionIcon />
        </button>
        
        <!-- Help Modal -->
        <transition name="escr-help-fade">
            <div v-if="showHelp" class="escr-help-modal-overlay" @click="closeHelp">
                <div class="escr-help-modal" @click.stop>
                    <!-- Header -->
                    <div class="escr-help-header">
                        <h3 class="escr-help-title">
                            <QuestionIcon class="escr-help-title-icon" />
                            {{ translate('Help') }}: {{ topicTitle }}
                        </h3>
                        <button @click="closeHelp" class="escr-help-close" :aria-label="translate('Close')">
                            ✖
                        </button>
                    </div>
                    
                    <!-- Body -->
                    <div class="escr-help-body">
                        <div class="escr-help-quick-tips">
                            <h4>{{ translate('Quick Tips') }}</h4>
                            <ul>
                                <li v-for="(tip, index) in quickTips" :key="index">
                                    {{ tip }}
                                </li>
                            </ul>
                        </div>
                        
                        <div class="escr-help-actions">
                            <a 
                                :href="fullDocsUrl" 
                                target="_blank" 
                                class="escr-help-link escr-help-link-primary"
                            >
                                📄 {{ translate('Full Documentation') }}
                            </a>
                            
                            <button 
                                v-if="videoUrl"
                                @click="openVideo" 
                                class="escr-help-link escr-help-link-secondary"
                            >
                                🎥 {{ translate('Watch Tutorial') }}
                            </button>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="escr-help-footer">
                        <span class="escr-help-hint">
                            💡 {{ translate('Tip') }}: {{ translate('Press Esc to close') }}
                        </span>
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>

<script>
import QuestionIcon from "../Icons/QuestionIcon/QuestionIcon.vue";
import "./HelpButton.css";

export default {
    name: "EscrHelpButton",
    components: { QuestionIcon },
    props: {
        /**
         * Topic ID: "search", "find-replace", "advanced-search"
         */
        topic: {
            type: String,
            required: true
        }
    },
    data() {
        return {
            showHelp: false,
        }
    },
    computed: {
        topicTitle() {
            const titles = {
                'search': this.translate('Search'),
                'find-replace': this.translate('Find & Replace'),
                'advanced-search': this.translate('Advanced Search')
            };
            return titles[this.topic] || this.translate('Help');
        },
        
        quickTips() {
            const tips = {
                'search': [
                    this.translate('Use quotes for exact phrase: "שמואל בן יוסף"'),
                    this.translate('Use * for wildcard: שמו*ל finds שמואל, שמואיל'),
                    this.translate('Search is case-insensitive'),
                ],
                'find-replace': [
                    this.translate('Preview changes before applying'),
                    this.translate('Use Regex mode for advanced patterns'),
                    this.translate('Cannot be undone - use carefully!'),
                ],
                'advanced-search': [
                    this.translate('Elasticsearch searches all documents'),
                    this.translate('Supports fuzzy matching for typos'),
                    this.translate('Use filters to narrow results'),
                ]
            };
            return tips[this.topic] || [];
        },
        
        fullDocsUrl() {
            // נתיב למדריך המלא (נעדכן אחרי שנעתיק את הקבצים)
            const urls = {
                'search': '/static/docs/he/search.html',
                'find-replace': '/static/docs/he/find-replace.html',
                'advanced-search': '/static/docs/he/advanced-search.html'
            };
            return urls[this.topic] || '/static/docs/he/search.html';
        },
        
        videoUrl() {
            // אם יש סרטוני הדרכה
            const videos = {
                'search': null, // נעדכן אחרי שיהיה וידאו
                'find-replace': null,
                'advanced-search': null
            };
            return videos[this.topic];
        }
    },
    mounted() {
        // Listen for Esc key
        document.addEventListener('keydown', this.handleEsc);
    },
    beforeUnmount() {
        document.removeEventListener('keydown', this.handleEsc);
    },
    methods: {
        toggleHelp() {
            this.showHelp = !this.showHelp;
        },
        
        closeHelp() {
            this.showHelp = false;
        },
        
        openVideo() {
            if (this.videoUrl) {
                window.open(this.videoUrl, '_blank');
            }
        },
        
        handleEsc(event) {
            if (event.key === 'Escape' && this.showHelp) {
                this.closeHelp();
            }
        },
        
        translate(key) {
            // Integration with i18n
            return this.$t ? this.$t(key) : key;
        }
    }
}
</script>
