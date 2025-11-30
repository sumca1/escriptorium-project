import Vue from "vue";
import store from "./index.js";
import DocumentsTasks from "../../vue/components/DocumentsTasks/List.vue";

// Register i18n translations for Vue components
import { registerMessages } from "../../vue/exports/i18nInjector";
registerMessages();

export var docstasksVM = new Vue({
    el: "#documents_tasks",
    store,
    components: {
        documentstasks: DocumentsTasks,
    },
});
