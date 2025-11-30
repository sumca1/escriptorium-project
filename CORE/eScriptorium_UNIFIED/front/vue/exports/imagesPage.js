import Vue from "vue";
import { registerMessages } from "./i18nInjector";
import store from "../store";
import Images from "../pages/Images/Images.vue";

// Register Hebrew translations
registerMessages();

export default new Vue({
    el: "#images-page",
    store,
    components: {
        "images-page": Images,
    },
});
