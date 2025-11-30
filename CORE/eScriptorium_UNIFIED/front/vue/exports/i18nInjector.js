// GENERATED FILE - do not edit by hand
// Updated: 2025-10-30 - Using namespace-based translations
import Vue from 'vue';
import { registerMessages as registerNamespacedMessages, loadNamespace, preloadNamespaces } from './i18nNamespaces';

// Re-export for convenience
export { loadNamespace, preloadNamespaces };

// Backwards compatibility - this will be deprecated
import he from '../locales/he.json';
const messages = he || {};

// Helper to detect current language (keep for backwards compatibility)
function getCurrentLanguage() {
    // Check django_language cookie
    const match = document.cookie.match(/django_language=([^;]+)/);
    if (match) {
        return match[1];
    }
    
    // Fallback to html lang attribute
    const htmlLang = document.documentElement.lang || 'en';
    return htmlLang;
}

export function registerMessages() {
    // Use the new namespaced system
    console.log('🌐 Using namespaced translations (common loaded by default)');
    registerNamespacedMessages();
}

export default messages;
