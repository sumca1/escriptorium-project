import store from "./index.js";
import Editor from "../../vue/components/Editor.vue";
import { registerMessages, loadNamespace } from "../../vue/exports/i18nInjector";

// RTL Support for Hebrew & Arabic
import "../rtl-support.css";

// ensure front-end translations are registered for the editor app
registerMessages();

// Lazy load editor-specific translations
console.log('⏳ Editor: Loading editor namespace...');
loadNamespace('editor').then(() => {
    console.log('✅ Editor: Editor namespace loaded!');
}).catch(err => {
    console.error('❌ Editor: Failed to load editor namespace:', err);
});

export var partVM = new Vue({
    el: "#editor",
    store,
    components: {
        editor: Editor,
    },
});
