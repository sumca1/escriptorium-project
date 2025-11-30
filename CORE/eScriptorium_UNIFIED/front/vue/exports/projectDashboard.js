import Vue from "vue";
import { registerMessages } from "./i18nInjector";
import store from "../store";
import Project from "../pages/Project/Project.vue";

// Register Hebrew translations
registerMessages();

export default new Vue({
    el: "#project-dashboard",
    store,
    components: {
        "project-dashboard": Project,
    },
});
