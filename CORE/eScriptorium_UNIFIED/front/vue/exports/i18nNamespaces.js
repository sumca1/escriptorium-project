// i18n Namespace Manager - Lazy loading translations
// Created: 2025-10-30
// Purpose: Load translation namespaces on-demand instead of all at once

import Vue from 'vue';
import common from '../locales/he_split/common.json';

// Loaded namespaces cache
const loadedNamespaces = {
    common: common // Always load common immediately
};

// Helper to detect current language
function getCurrentLanguage() {
    const match = document.cookie.match(/django_language=([^;]+)/);
    if (match) return match[1];
    return document.documentElement.lang || 'en';
}

// Merge all loaded namespaces into a single messages object
function getMergedMessages() {
    const merged = {};
    Object.values(loadedNamespaces).forEach(namespace => {
        Object.assign(merged, namespace);
    });
    return merged;
}

/**
 * Load a translation namespace dynamically
 * @param {string} namespace - 'editor' or 'other'
 * @returns {Promise<Object>} The loaded namespace
 */
export async function loadNamespace(namespace) {
    // Skip if already loaded
    if (loadedNamespaces[namespace]) {
        console.log(`✅ i18n namespace '${namespace}' already loaded`);
        return loadedNamespaces[namespace];
    }

    console.log(`⏳ Loading i18n namespace: ${namespace}`);
    
    try {
        let namespaceData;
        
        if (namespace === 'editor') {
            namespaceData = await import(
                /* webpackChunkName: "i18n-editor" */
                '../locales/he_split/editor.json'
            );
        } else if (namespace === 'other') {
            namespaceData = await import(
                /* webpackChunkName: "i18n-other" */
                '../locales/he_split/other.json'
            );
        } else {
            console.warn(`⚠️ Unknown namespace: ${namespace}`);
            return {};
        }

        // Cache the loaded namespace
        loadedNamespaces[namespace] = namespaceData.default || namespaceData;
        
        console.log(`✅ Loaded ${namespace} namespace (${Object.keys(loadedNamespaces[namespace]).length} keys)`);
        
        // Update Vue $t function with new messages
        updateVueTranslations();
        
        return loadedNamespaces[namespace];
    } catch (error) {
        console.error(`❌ Failed to load namespace '${namespace}':`, error);
        return {};
    }
}

/**
 * Update Vue's $t function with current loaded messages
 */
function updateVueTranslations() {
    const messages = getMergedMessages();
    
    if (Vue.prototype.$i18n) {
        // If vue-i18n is available, merge messages
        try {
            Vue.prototype.$i18n.mergeLocaleMessage('he', messages);
        } catch (e) {
            console.error('Failed to merge locale messages:', e);
        }
    } else {
        // Update our custom $t shim
        Vue.prototype.$t = function (key, params) {
            const currentLang = getCurrentLanguage();
            
            // Only translate if current language is Hebrew or Arabic
            if (currentLang !== 'he' && currentLang !== 'ar') {
                return key;
            }
            
            // Handle nested keys
            const keys = key.split('.');
            let val = messages;
            
            for (const k of keys) {
                if (val && typeof val === 'object' && k in val) {
                    val = val[k];
                } else {
                    val = key;
                    break;
                }
            }
            
            if (typeof val !== 'string') {
                val = key;
            }
            
            if (!params) return val;
            try {
                return val.replace(/\{(\w+)\}/g, (m, p) => (params[p] !== undefined ? params[p] : m));
            } catch (e) {
                return val;
            }
        };
    }
}

/**
 * Initialize i18n with common namespace
 * Call this on app startup
 */
export function registerMessages() {
    console.log('🌐 Initializing i18n with common namespace');
    console.log(`   - common: ${Object.keys(loadedNamespaces.common).length} keys`);
    
    updateVueTranslations();
}

/**
 * Preload namespaces for a specific page
 * @param {string[]} namespaces - Array of namespace names
 */
export async function preloadNamespaces(...namespaces) {
    console.log(`⏳ Preloading namespaces: ${namespaces.join(', ')}`);
    await Promise.all(namespaces.map(ns => loadNamespace(ns)));
    console.log('✅ All namespaces preloaded');
}

// Export default for backwards compatibility
export default getMergedMessages();
