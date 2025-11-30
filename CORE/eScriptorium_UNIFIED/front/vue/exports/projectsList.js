import Vue from "vue";
import { registerMessages } from "./i18nInjector";
import store from "../store";
import ProjectsList from "../pages/ProjectsList/ProjectsList.vue";

// Register Hebrew translations
registerMessages();

export default new Vue({
    el: "#projects-list",
    store,
    components: {
        "projects-list": ProjectsList,
    },
});
