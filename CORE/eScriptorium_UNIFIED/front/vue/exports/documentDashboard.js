import Vue from "vue";
import { registerMessages } from "./i18nInjector";
import store from "../store";
import Document from "../pages/Document/Document.vue";

// Register Hebrew translations
registerMessages();

export default new Vue({
    el: "#document-dashboard",
    store,
    components: {
        "document-dashboard": Document,
    },
});
